from hata import CLIENTS, Embed, ChannelVoice, ChannelText
from hata.backend.dereaddons_local import _spaceholder
from hata.ext.commands import utils
from utils.utils import EscapedException


class SetupExternalSafeCommands:
    """
    Sets up the safe commands for the client
    """
    def __init__(self, client):
        client.safe_message_create = self.safe_message_create
        client.safe_reaction_add = self.safe_reaction_add
        client.safe_reaction_clear = self.safe_reaction_clear
        client.safe_join_voice_channel = self.safe_join_voice_channel
        client.check_voice_perms = self.check_voice_perms
        client.safe_wait_for = self.safe_wait_for
        client.safe_webhook_get_channel = self.safe_webhook_get_channel
        client.safe_webhook_create = self.safe_webhook_create
        self.client = client

    async def safe_message_create(self, message, channel, content=None, embed=None, file=None,
                                  allowed_mentions=_spaceholder,
                                  message_reference=None, tts=False, nonce=None, log=False, ignore=False):
        channeled = True
        if isinstance(message, ChannelText):
            channeled = False
        err = f'Dont have permissions to send message in {channel.id}'
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        _var = False
        for _client in _CLIENTS:
            perms = channel.cached_permissions_for(_client)
            if perms.can_send_messages:
                if embed:
                    if not perms.can_embed_links:
                        if not _var:
                            _var = _client
                        continue
                return await _client.message_create(channel, content, embed, file, allowed_mentions, message_reference,
                                                    tts, nonce)
        if _var:
            return await _var.message_create(channel, f'{embed.title}\n{embed.description}', None, file,
                                             allowed_mentions, message_reference, tts, nonce)
        if channeled:
            if message.channel is channel or not log:
                return print(err)
        else:
            if message is channel or not log:
                return print(err)
        embed = Embed(title='Dont have permissions to send message in that channel', description=f'{channel.mention}')
        if channeled:
            await self.safe_message_create(message, message.channel, message.author.mention, embed, None, _spaceholder,
                                           None, False, None, False)
        else:
            await self.safe_message_create(message, message, None, embed, None, _spaceholder,
                                           None, False, None, False)
        if not ignore:
            raise EscapedException(err, 'send_message')
        print(err)

    @staticmethod
    async def safe_wait_for(type_, message, function, timeout):
        for _client in CLIENTS:
            perms = message.channel.cached_permissions_for(_client)
            if perms.can_read_message_history:
                if type_ == 'reaction':
                    return await utils.wait_for_reaction(_client, message, function, timeout)
                elif type_ == 'message':
                    return await utils.wait_for_message(_client, message.channel, function, timeout)
                else:
                    raise NotImplemented()

    async def safe_reaction_add(self, message, emoji, show_error=False):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        for _client in _CLIENTS:
            perms = message.channel.cached_permissions_for(_client)
            if perms.can_add_reactions:
                return await _client.reaction_add(message, emoji)
        if show_error:
            await self.safe_message_create(message, message.channel, 'Give me permissions to add reaction')
        raise EscapedException(f'Dont have permissions to add reactions in {message.channel.id}', 'add_reaction')

    async def safe_reaction_clear(self, message, show_error=False, important=True):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        err = f'Dont have permissions to remove reactions in {message.channel.id}'
        for _client in _CLIENTS:
            perms = message.channel.cached_permissions_for(_client)
            if perms.can_manage_messages:
                return await _client.reaction_clear(message)
        if show_error:
            await self.safe_message_create(message, message.channel, 'Give me manage messages permission', ignore=True)
        if important:
            raise EscapedException(err, 'remove_reaction')
        print(err)

    def check_voice_perms(self, voice_channel, connect=True, speak=True):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        for _client in _CLIENTS:
            perms = voice_channel.cached_permissions_for(_client)
            if connect and speak and perms.can_connect and perms.can_speak:
                return True
            elif connect and perms.can_connect:
                return True
            elif speak and perms.can_speak:
                return True

    async def safe_webhook_get_channel(self, message, channel):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        for _client in _CLIENTS:
            perms = channel.cached_permissions_for(_client)
            if perms.can_manage_webhooks:
                return await _client.webhook_get_channel(channel)
        err = f'Don\'t have manage webhooks permissions in {channel.mention}'
        await self.safe_message_create(message, message.channel, err, ignore=True)
        raise EscapedException(err, 'manage_webhooks')

    async def safe_webhook_create(self, message, channel, name, avatar=None):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        for _client in _CLIENTS:
            perms = channel.cached_permissions_for(_client)
            if perms.can_manage_webhooks:
                return await _client.webhook_create(channel, name, avatar)
        err = f'Don\'t have manage webhooks permissions in {channel.mention}'
        await self.safe_message_create(message, message.channel, err, ignore=True)
        raise EscapedException(err, 'manage_webhooks')

    async def safe_join_voice_channel(self, message, voice_channel: ChannelVoice, show_error=True, escape=False):
        _CLIENTS = list(CLIENTS)[:]
        _CLIENTS = [_CLIENTS.pop(_CLIENTS.index(self.client))] + _CLIENTS
        err = f'Dont have permissions to join that voice channel {voice_channel.name}'
        for _client in _CLIENTS:
            perms = voice_channel.cached_permissions_for(_client)
            if perms.can_connect:
                return await _client.join_voice_channel(voice_channel)
        if show_error:
            await self.safe_message_create(message, message.channel, err, ignore=True)
        if not escape:
            raise EscapedException(err, 'join_voice')
        print(err)
