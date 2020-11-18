import audioop
from audioop import add as add_voice

from config import CORE_GUILD
from config import WHITELISTED_OWNERS
from hata import CLIENTS, Client, Message, Webhook, eventlist
from hata.discord.opus import OpusDecoder
from hata.discord.player import AudioSource
from hata.ext.commands import Command
from hata.ext.commands.command import checks


def get_seq():
    """
    Returns a dictionary of co related clients
    """
    client_sequence = {}
    for pos, _client in enumerate(CLIENTS):
        if len(CLIENTS) == pos + 1:
            client_sequence[_client.id] = list(CLIENTS)[-1]
        else:
            client_sequence[_client.id] = list(CLIENTS)[pos + 1]
    return client_sequence


def gettime(seconds):
    """
    Returns the highest rounded time from seconds
    """
    seconds = int(seconds)
    gets = lambda x: '' if x == 1 else 's'
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    months = days // 30
    years = months // 12
    if seconds < 60:
        return f'{seconds} second{gets(seconds)}'
    elif seconds < 60*60:
        return f'{minutes} minute{gets(minutes)}'
    elif seconds < 60*60*24:
        return f'{hours} hour{gets(hours)}'
    elif seconds < 60*60*24*30:
        return f'{days} day{gets(days)}'
    elif seconds < 60*60*24*30*12:
        return f'{months} months{gets(months)}'
    else:
        return f'{years} year{gets(years)}'


class CommandClass:
    """
    Class which handles extension for all clients
    """
    def __init__(self):
        self.command_klass_list = []
        self.clients = list(CLIENTS)
        for i in range(len(self.clients)):
            self.command_klass_list.append(eventlist(type_=Command))

    def __call__(self, klass):
        for i in range(len(self.clients)):
            self.command_klass_list[i].from_class(klass)
        return klass

    def from_class(self, klass):
        self.__call__(klass)


class Wrapper:
    """
    Class which handles Commands, Events and Extensions for all the clients
    """
    def __init__(self):
        self.command_class = CommandClass()

    @staticmethod
    async def leave(message):
        for client in CLIENTS:
            vc = client.voice_client_for(message)
            if vc:
                await vc.disconnect()

    @staticmethod
    def extend(cmd_class):
        for pos, client in enumerate(cmd_class.clients):
            client.commands.extend(cmd_class.command_klass_list[pos])

    @staticmethod
    def unextend(cmd_class):
        for pos, client in enumerate(cmd_class.clients):
            client.commands.unextend(cmd_class.command_klass_list[pos])

    @staticmethod
    def make_category(name):
        for client in list(CLIENTS):
            category = client.command_processer.get_category(name)
            if not category:
                client.command_processer.create_category(name)

    def commands(self, func=None, **kwargs):
        if func is None:
            return self.wrap('w', **kwargs)
        return self.wrap('w', **kwargs)(func)

    @staticmethod
    def wrap(m, **kwargs):
        def addfunc(func):
            for client in CLIENTS:
                if m == 'w':
                    client.commands(**kwargs)(func)
                elif m == 'e':
                    client.events(**kwargs)(func)
            return func

        return addfunc

    def events(self, func=None, **kwargs):
        if func is None:
            return self.wrap('e', **kwargs)
        return self.wrap('e', **kwargs)(func)


async def owneronly(_client: Client, message: Message, *_args, **_kwargs):
    if message.author.id not in WHITELISTED_OWNERS:
        return False
    return True


owneronly = [checks.custom(function=owneronly)]


def colourfunc(_client, message, _name):
    """
    Returns colour of user at guild
    """
    return message.author.color_at(message.guild)


async def send(client: Client, webhook: Webhook, message: Message):
    """
    sends message via webhook
    """
    await client.webhook_send(webhook, message.content, avatar_url=message.author.avatar_url, name=message.author.name)


class SEQUENTIAL_ASK_NEXT:
    """
    Class which is supposed to correlate the command between the clients
    """
    async def _exec(self, client: Client, message: Message, *args):
        await self.before_exec(client, message, *args)
        _next = get_seq()[client.id]
        if message.author not in CLIENTS:
            if message.guild.id != CORE_GUILD:
                return await self.function(client, message, *args)
            res = await self.singlefunction(client, message, *args)
            if res:
                await client.message_create(message.channel, f'Asking {_next.mention}')
                await client.message_create(message.channel, f'{_next.command_processer.prefix}lookup {"".join(args)}')
        else:
            if message.guild.id == CORE_GUILD:
                res = await self.singlefunction(client, message, *args)
                if res:
                    await client.message_create(message.channel, f'Asking {_next.mention}')
                    return await client.message_create(message.channel,
                                                       f'{_next.command_processer.prefix}lookup {"".join(args)}')
                return await self.function(client, message, *args)


class MixerStream(AudioSource):
    """
    Class which merges audio streams
    """
    __slots__ = ('_decoder', '_postprocess_called', 'sources',)

    def __init__(self, *sources):
        self.sources = list(sources)
        self._decoder = OpusDecoder()
        self._postprocess_called = False

    async def postprocess(self):
        if self._postprocess_called:
            return

        self._postprocess_called = True
        for source in self.sources:
            await source.postprocess()

    async def add(self, source):
        if self._postprocess_called:
            await source.postprocess()

        self.sources.append(source)

    async def remove(self, userid):
        for source in self.sources[:]:
            if source.user.id == userid:
                self.sources.remove(source)

    async def read(self):
        sources = self.sources
        result = b'\x00' * 3840

        for index in reversed(range(len(sources))):
            source = sources[index]
            data = await source.read()
            if data is None:
                del sources[index]
                await source.cleanup()
                continue
            if not source.NEEDS_ENCODE:
                data = self._decoder.decode(data)
            if data == b'\x00' * 3840:
                continue
            if result == b'\x00' * 3840:
                result = data
            else:
                result = add_voice(result, data, 1)
            continue
        return audioop.mul(result, 1, 0.75)

    async def cleanup(self):
        self._postprocess_called = False
        sources = self.sources
        while sources:
            source = sources.pop()
            await source.cleanup()


def setdefault(_dict, val, default):
    _dict[val] = _dict.get(val, default)
    return _dict[val]


def inverse(_dict):
    return dict(zip(_dict.values(), _dict.keys()))


class EscapedException(Exception):
    def __init__(self, error, _type=None):
        super().__init__(error)
        self.error = error
        self.type = _type


ALL = Wrapper()
