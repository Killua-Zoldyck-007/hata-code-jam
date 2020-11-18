from databases.shared_data import common_data
from hata import Client, Message, ChannelText, CHANNELS, CLIENTS
from utils.utils import ALL, send, setdefault

CHAT_COMMANDS = ALL.command_class
Reimu: Client
Bcom: Client
Astra: Client


def setup(_lib):
    ALL.make_category('ChatCMDS')
    ALL.extend(CHAT_COMMANDS)


def teardown(_lib):
    ALL.unextend(CHAT_COMMANDS)


@CHAT_COMMANDS
class Connect:
    """
    Connects the current channel to any other channel in any other server
    Usage - **`connect [channel mention or id]`**
    """
    category = 'ChatCMDS'

    @staticmethod
    async def command(client: Client, message: Message, channel: ('int', 'channel')):
        if isinstance(channel, ChannelText):
            channel = channel.id
        if not isinstance(channel, int):
            return await client.safe_message_create(message, message.channel, 'Invalid Channel')
        if not (channel := CHANNELS.get(channel)):
            return await client.safe_message_create(message, message.channel, 'Invalid Channel')
        initial_webhook = await client.safe_webhook_get_channel(message, message.channel)
        final_webhook = await client.safe_webhook_get_channel(message, channel)
        data = setdefault(common_data, 'ChatData', {})
        guild_data = setdefault(data, message.guild.id, {})
        if len(guild_data) >= 2:
            return await client.safe_message_create(message, message.channel, 'Your guild already has 2 connections')
        other_guild_data = setdefault(data, channel.guild.id, {})
        if len(other_guild_data) >= 2:
            return await client.safe_message_create(message, message.channel,
                                                    f'{channel.guild.name} already has 2 connections')
        if message.channel.id in guild_data:
            return await client.safe_message_create(message, message.channel,
                                                    f'You are already connected '
                                                    f'with <#{guild_data[message.channel.id]["other"].id}>')
        if channel.id in other_guild_data:
            return await client.safe_message_create(message, message.channel,
                                                    f'<#{other_guild_data[channel.id]["other"].id}> '
                                                    f'is already connected with another channel.')
        if message.channel is channel:
            return await client.safe_message_create(message, message.channel,
                                                    'You must provide a different channel to connect with')
        if initial_webhook:
            initial_webhook = initial_webhook[0]
        else:
            initial_webhook = await client.safe_webhook_create(message, message.channel, 'Coconuts')
        if final_webhook:
            final_webhook = final_webhook[0]
        else:
            final_webhook = await client.safe_webhook_create(message, channel, 'Coconuts')
        guild_data[message.channel.id] = {}
        guild_data[message.channel.id]['webhook'] = final_webhook
        guild_data[message.channel.id]['other'] = channel
        other_guild_data[channel.id] = {}
        other_guild_data[channel.id]['webhook'] = initial_webhook
        other_guild_data[channel.id]['other'] = message.channel
        if channel.guild is message.guild:
            await client.safe_message_create(message, message.channel, f'Connected to {channel.mention}')
            return await client.safe_message_create(message, channel, f'Connected to {message.channel.mention}')
        await client.safe_message_create(message, message.channel,
                                         f'Connected to {channel.mention} in **`{channel.guild.name}`**')
        await client.safe_message_create(message, channel,
                                         f'Connected to {message.channel.mention} in **`{message.guild.name}`**')


@CHAT_COMMANDS.from_class
class Disconnect:
    """
    Disconnects the current channel from all other channel connections
    Usage - **`disconnect`**(no other parameters)
    """
    category = 'CHAT'

    @staticmethod
    async def command(client: Client, message: Message):
        data = setdefault(common_data, 'ChatData', {})
        guild_data = setdefault(data, message.guild.id, {})
        if message.channel.id not in guild_data:
            return await client.safe_message_create(message, message.channel,
                                                    'There isn\'t a connection in this channel')
        other = guild_data[message.channel.id]['other']
        if other.guild is message.guild:
            await client.safe_message_create(message, message.channel, f'Disconnected from {other.mention}')
            await client.safe_message_create(message, other, f'Disconnected from {message.channel.mention}')
        else:
            await client.safe_message_create(message, other,
                                             f'Disconnected from {message.channel.mention} '
                                             f'in **`{message.guild.name}`**')
            await client.safe_message_create(message, message.channel,
                                             f'Disconnected from {other.mention} in **`{other.guild.name}`**')
        del common_data['ChatData'][other.guild.id][other.id]
        del common_data['ChatData'][message.guild.id][message.channel.id]


CLIENTS = list(CLIENTS)[:]


async def unify(message: Message):
    if message.author.is_bot:
        return
    if message.channel.id in common_data.get('ChatData', {}).get(message.guild.id, {}):
        for _client in CLIENTS:
            if message.content.startswith(_client.command_processer.prefix):
                return
        other = common_data['ChatData'][message.guild.id][message.channel.id]['other']
        for _client in CLIENTS:
            if other.cached_permissions_for(_client).can_manage_webhooks:
                break
        else:
            return
        return await send(_client, common_data['ChatData'][message.guild.id][message.channel.id]['webhook'],
                          message)


@ALL.events
async def message_create(client: Client, message: Message):
    if Reimu.id in message.guild.users:
        if client is not Reimu:
            return
    elif Bcom.id in message.guild.users:
        if client is not Bcom:
            return
    await unify(message)
