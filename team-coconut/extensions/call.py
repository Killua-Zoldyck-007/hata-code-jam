import time

from config import TIMELIMIT
from databases.shared_data import common_data
from hata import Message, Client, ChannelVoice, ChannelText, BUILTIN_EMOJIS, VoiceState, Task, KOKORO, Embed
from utils.utils import setdefault, MixerStream, ALL, EscapedException, gettime

CALL_COMMANDS = ALL.command_class
Reimu: Client
Bcom: Client
Astra: Client


class Log:
    def __init__(self, direction, number, logdata, other=None):
        self.over = False
        self.direction = direction
        self.number = number
        self.logdata = logdata
        self.other: Log = other
        self.status = 'x'
        self.start = None
        self.starttime = time.perf_counter()

    def resettime(self):
        self.starttime = time.perf_counter()

    def error(self):
        self.status = 'X'
        self.other.status = 'X'
        self.end(True)

    def getdata(self):
        return self.direction + self.status

    def accept(self):
        self.resettime()
        self.status = 'a'
        self.other.status = 'a'

    def decline(self):
        self.status = 'd'
        self.other.status = 'd'
        self.end(True)

    def kill(self, notime=False):
        self.over = True
        _time = time.perf_counter() - self.starttime
        self.over = True
        if notime:
            _time = 0
        self.logdata.append([self.other.number, self.getdata(), self.starttime, _time])

    def end(self, notime=False):
        if not self.over:
            self.kill(notime)
            self.other.kill(notime)


def setup(_lib):
    ALL.make_category('CallCMDS')
    ALL.extend(CALL_COMMANDS)


def teardown(_lib):
    ALL.unextend(CALL_COMMANDS)


async def cleanup(id1, id2):
    common_data['TempCallLog'][id1].end()
    del common_data['TempCallLog'][id1]
    del common_data['TempCallLog'][id2]
    vc1 = common_data['CallData'][id1]['SelfVC']
    vc2 = common_data['CallData'][id2]['SelfVC']
    ch1 = common_data['CallData'][id1]['SelfCallCh']
    ch2 = common_data['CallData'][id2]['SelfCallCh']
    del common_data['CallData'][id1]
    del common_data['CallData'][id2]
    await vc1.client.safe_message_create(ch1, ch1, 'Call ended', ignore=True)
    await vc2.client.safe_message_create(ch2, ch2, 'Call ended', ignore=True)
    await vc1.disconnect()
    await vc2.disconnect()


@ALL.commands
async def endcall(client: Client, message: Message):
    """
    Ends the call
    """
    if message.guild.id not in common_data.get('CallData', {}):
        return await client.safe_message_create(message, message.channel, 'You are not in a call')
    await cleanup(message.guild.id, common_data['CallData'][message.guild.id]['Other'])


@ALL.commands
async def log(client: Client, message: Message):
    """
    Shows the call history of guild
    """
    data = common_data.get('CallLog', {}).get(message.guild.id)
    if data:
        counter = 0
        for pos, history in enumerate(data[::-1]):
            embed = Embed(f'Call Log for {message.guild.id}')
            embed.add_field(name=f'{pos+1}--> {history[0]}',
                            value=f'Called {gettime(time.perf_counter() - history[2])} ago, Call duration {gettime(history[3])}')
        return await client.safe_message_create(message, message.channel, embed=embed)
    await client.safe_message_create(message, message.channel, 'You have no call history')


@CALL_COMMANDS
class Register:
    """
    Registers the guild to be callable
    (you should be in a voice channel)
    """
    category = 'CallCMDS'

    async def command(self: Client, message: Message):
        client = self
        setdefault(common_data, 'CallRegisterData', {})
        voice_client = client.voice_client_for(message)
        if voice_client is None:
            voice_client = message.guild.voice_states.get(message.author.id, None)
        if not voice_client:
            return await client.safe_message_create(message, message.channel, 'You must join a voice channel first')
        if not client.check_voice_perms(voice_client.channel, True):
            return await client.safe_message_create(message, message.channel,
                                                    f'I dont have permission to connect to {voice_client.channel.name}')
        if not client.check_voice_perms(voice_client.channel, False, True):
            return await client.safe_message_create(message, message.channel,
                                                    f'I dont have permission to speak in {voice_client.channel.name}')
        guild_data = setdefault(common_data['CallRegisterData'], message.guild.id, {})
        guild_data['VoiceID'] = voice_client.channel.id
        guild_data['ChannelID'] = message.channel.id
        guild_data['UserID'] = message.author.id

        msg = f"The voice channel **`{voice_client.channel.name}`** is now registered as the server's Phone. " \
              f"you will receive phone request calls in {message.channel.mention}"
        msg += f'\n**{message.guild.id}** is your phone number'
        await client.safe_message_create(message, message.channel, msg)


def check(_id, event):
    if _id == event.user.id and event.emoji in [BUILTIN_EMOJIS['white_check_mark'], BUILTIN_EMOJIS['x']]:
        return True
    return False


def check2(_id, event):
    if _id == event.user.id and event.content.lower() in ['d', 'a', 'decline', 'accept', 'y', 'yes', 'n', 'no']:
        return True
    return False


@CALL_COMMANDS
class Call:
    """
    It relays voice between two voice channels registered via the register command
    Usage - **`call [guild id or name]`**
    """
    category = 'CallCMDS'

    async def command(self: Client, message: Message, *number: 'str'):
        client = self
        if isinstance(number, tuple):
            number = ''.join(number)
        number = number.casefold()
        if not number.isnumeric():
            data = common_data.get('PhData', {}).get(message.author.id, {})
            if not number in data:
                return await client.safe_message_create(message, message.channel,
                                                        f'{number} not found on your saved contacts')
            number = data[number]
        number = int(number)
        if message.guild.id not in common_data.get('CallRegisterData', {}).keys():
            return await client.safe_message_create(message, message.channel,
                                                    'Register this server first by typing `r1register`')
        if number not in common_data.get('CallRegisterData', {}).keys():
            return await client.safe_message_create(message, message.channel, f'Number {number} not found')
        if number == message.guild.id:
            return await client.safe_message_create(message, message.channel, f'Call someone other than yourself')
        if number in common_data.get('CallData', {}).keys():
            return await client.safe_message_create(message, message.channel, f'{number} is already in a call ')
        if message.guild.id in common_data.get('CallData', {}).keys():
            return await client.safe_message_create(message, message.channel, f'You are already on a call ')
        await client.safe_message_create(message, message.channel, f'Attempting to call {number}')
        data = common_data['CallRegisterData']
        other_channel = ChannelText.precreate(data[number]['ChannelID'])

        log = setdefault(common_data, 'CallLog', {})
        mylogdata = setdefault(log, message.guild.id, [])
        otherlogdata = setdefault(log, number, [])
        mylog = Log('o', message.guild.id, mylogdata)
        otherlog = Log('i', number, otherlogdata, mylog)
        mylog.other = otherlog
        templog = setdefault(common_data, 'TempCallLog', {})
        templog[message.guild.id] = mylog
        templog[number] = otherlog

        if not other_channel.guild:
            mylog.error()
            return await client.safe_message_create(message, message.channel,
                                                    f'{number}\'s registered call receiving channel '
                                                    f'does not exist anymore.')
        other_voice = ChannelVoice.precreate(data[number]['VoiceID'])
        if not other_voice.guild:
            mylog.error()
            return await client.safe_message_create(message, other_channel,
                                                    f"<@{data[number]['UserID']}> your registered voice channel "
                                                    f"does not exist anymore.")
        my_voice = ChannelVoice.precreate(data[message.guild.id]['VoiceID'])
        if not my_voice.guild:
            mylog.error()
            return await client.safe_message_create(message, message.channel,
                                                    f"{message.author.mention} your registered voice channel "
                                                    f"does not exist anymore.")
        other_message = await client.safe_message_create(message, other_channel,
                                                         f"<@{data[number]['UserID']}> "
                                                         f"incoming call from {message.guild.id}",
                                                         log=True)
        escaped = False
        try:
            await client.safe_reaction_add(other_message, BUILTIN_EMOJIS['white_check_mark'], True)
            await client.safe_reaction_add(other_message, BUILTIN_EMOJIS['x'], True)
        except EscapedException as err:
            if err.type != 'add_reaction':
                raise err
            escaped = True
            await client.safe_message_create(message, other_channel, 'Accept(A/Y) or Decline(D/N)')
        if not escaped:
            try:
                res = await client.safe_wait_for('reaction', other_message, lambda x: check(data[number]['UserID'], x),
                                                 60)
            except TimeoutError:
                mylog.end()
                await client.safe_eaction_clear(other_message)
                await client.safe_message_create(message, other_channel, 'Call got timed out', log=True)
                return await client.safe_message_create(message, message.channel,
                                                        message.author.mention + ', Your call wasn\'t picked up')
            if res.emoji == BUILTIN_EMOJIS['white_check_mark']:
                mylog.accept()
                await client.safe_reaction_clear(other_message, True, False)
                await client.safe_message_create(message, other_channel, 'Call Accepted', log=True)
                await client.safe_message_create(message, message.channel,
                                                 message.author.mention + ', Your call was accepted')
            else:
                mylog.decline()
                await client.safe_reaction_clear(other_message, True, False)
                await client.safe_message_create(message, other_channel, 'Call Declined', log=True)
                return await client.safe_message_create(message, message.channel,
                                                        message.author.mention + ', Your call was declined', log=True)
        else:
            try:
                res = await client.safe_wait_for('message', other_message, lambda x: check2(data[number]['UserID'], x),
                                                 60)
            except TimeoutError:
                mylog.end()
                await client.safe_reaction_clear(other_message, True, False)
                await client.safe_message_create(message, other_channel, 'Call got timed out', log=True)
                return await client.safe_message_create(message, message.channel,
                                                        message.author.mention + ', Your call wasn\'t picked up')
            if res.content.lower() in ['a', 'accept', 'y', 'yes']:
                mylog.accept()
                await client.reaction_clear(other_message)
                await client.safe_message_create(message, other_channel, 'Call Accepted', log=True)
                await client.safe_message_create(message, message.channel,
                                                 message.author.mention + ', Your call was accepted')
            else:
                mylog.decline()
                await client.safe_reaction_clear(other_message, True, False)
                await client.safe_message_create(message, other_channel, 'Call Declined', log=True)
                return await client.safe_message_create(message, message.channel,
                                                        message.author.mention + ', Your call was declined', log=True)

        vc1 = await client.safe_join_voice_channel(other_message, other_voice, True, True)
        vc2 = await client.safe_join_voice_channel(message, my_voice, True, True)
        if not vc1:
            mylog.error()
            await client.safe_message_create(message, message.channel,
                                             f'Coudn\'t connect to {other_voice.name} in {other_message.guild.name}')
        if not vc2:
            mylog.error()
            await client.safe_message_create(message, other_channel,
                                             f'Coudn\'t connect to {my_voice.name} in {message.guild.name}')

        if not vc1 or not vc2:
            await ALL.leave(message)
            await ALL.leave(other_message)
            return

        mixer = MixerStream()
        for user in other_voice.voice_users:
            if user is client:
                continue

            source = vc1.listen_to(user, yield_decoded=True)
            await mixer.add(source)
        vc2.append(mixer)

        mixer = MixerStream()
        for user in my_voice.voice_users:
            if user is client:
                continue

            source = vc2.listen_to(user, yield_decoded=True)
            await mixer.add(source)
        vc1.append(mixer)
        data = setdefault(common_data, 'CallData', {})
        data[message.guild.id] = {'Other': number, 'OtherVC': vc1, 'SelfVC': vc2, 'SelfChannel': my_voice,
                                  'SelfCallCh': message.channel, 'OtherCallCh': other_channel}
        data[number] = {'Other': message.guild.id, 'OtherVC': vc2, 'SelfVC': vc1, 'SelfChannel': other_voice,
                        'SelfCallCh': other_channel, 'OtherCallCh': message.channel}
        KOKORO.call_later(TIMELIMIT, Task, cleanup(message.guild.id, number), KOKORO)


@CALL_COMMANDS
class Save:
    """
    It saves the number as a name so that you can call that number via that name
    (like a phonebook)
    Usage - **`save [guild id you want to save] [name]`**
    """
    category = 'CallCMDS'

    async def command(self: Client, message: Message, number: int, *name: str):
        client = self
        if isinstance(name, tuple):
            name = ''.join(name)
        name = name.casefold()
        phdata = setdefault(common_data, 'PhData', {})
        userdata = setdefault(phdata, message.author.id, {})
        msg = f'Saved {number} as {name} in your phonebook'
        if name in userdata:
            msg = f'Updated {name} from {userdata[name]} to {number} in your phonebook'
        userdata[name] = number
        await client.safe_message_create(message, message.channel, msg)


@ALL.events
async def user_voice_join(client: Client, voice_state: VoiceState):
    if voice_state.guild.id in common_data.get('CallData', {}).keys():
        if voice_state.channel == common_data['CallData'][voice_state.guild.id]['SelfChannel']:
            _client = common_data['CallData'][voice_state.guild.id]['SelfVC']
            if _client.client is client:
                stream = _client.listen_to(voice_state.user)
                vc = common_data['CallData'][voice_state.guild.id]['OtherVC']
                if vc.source is None:
                    vc.append(MixerStream())
                await vc.source.add(stream)


@ALL.events
async def user_voice_leave(client: Client, voice_state: VoiceState):
    if voice_state.guild.id in common_data.get('CallData', {}).keys():
        if voice_state.channel == common_data['CallData'][voice_state.guild.id]['SelfChannel']:
            vc = common_data['CallData'][voice_state.guild.id]['OtherVC']
            if vc.client is client:
                if vc.source is None:
                    return
                await vc.source.remove(voice_state.user.id)
