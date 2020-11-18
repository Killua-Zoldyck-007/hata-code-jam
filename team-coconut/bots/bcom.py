import random

import config
from hata import Client, UserBase, ChannelBase, Embed
from hata.ext.commands import setup_ext_commands, FlaggedAnnotation, ConverterFlag, checks
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand
from utils.utils import colourfunc
from utils.safe import SetupExternalSafeCommands

Bcom: Client
setup_ext_commands(Bcom, config.BCOM_PREFIX, mention_prefix=True)
SetupExternalSafeCommands(Bcom)
Bcom.commands(SubterraneanHelpCommand(color=colourfunc), name='help')


@Bcom.events
async def message_create(client, message):
    if message.author.is_bot:
        return
    lowercase_content = message.content.lower()

    if lowercase_content in ('owo', '0w0'):
        await client.message_create(message.channel, "OwO")

    elif lowercase_content in ('uwu',):
        await client.message_create(message.channel, "UwU")

    elif lowercase_content.startswith('ayy',):
        await client.message_create(message.channel, 'Lmfao')


async def owner_only_handler(client, message, command, _check):
    await client.message_create(message.channel, f'You must be the owner of the bot to use the `{command}` command.')


@Bcom.commands(checks=[checks.owner_only(handler=owner_only_handler)])
async def owner(client, message):
    await client.message_create(message.channel, f'My masuta is {client.owner:f} !')


# --

@Bcom.commands
async def nani(client, message, entity: ('user', 'channel', 'role') = None):
    if entity is None:
        result = 'Idk what that thing is UwU'
    elif isinstance(entity, UserBase):
        if entity.is_bot:
            result = 'That user us a bot'
        else:
            result = "That user is a human"
    elif isinstance(entity, ChannelBase):
        result = 'That thing is a channel'
    else:
        result = 'That thing is a role'

    await client.message_create(message.channel, result)


@Bcom.commands
async def av(client, message, user: FlaggedAnnotation('user', ConverterFlag.user_all) = None):
    """Gibs the avatar of the user\nUsage: ``n!av [user]``"""
    if user is None:
        user = message.author

    if user.avatar:
        color = user.avatar_hash & 0xffffff
    else:
        color = user.default_avatar.color

    url = user.avatar_url_as(size=4096)
    embed = Embed(f'{user:f}\'s avatar', color=color, url=url)
    embed.add_image(url)

    await client.message_create(message.channel, embed=embed)


@Bcom.commands
async def separate(client, message, sep, *args):
    """separates the words using the given separator
    Usage: ``n!separate (separator) (the text you want to be separated)"""
    if not args:
        result = 'Nothing to separate'
    else:
        result = f" {sep} ".join(args)
    await client.message_create(message.channel, result)


@Bcom.commands
async def owo(client, msg, text):
    """owofies your text
    you might not see the difference in short text"""

    def replace(s, old, new):
        li = s.rsplit(old, 1)
        return new.join(li)

    vowels = 'aeiouAEIOU'
    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')
    smileys = (';;w;;', '^w^', '>w<', 'UwU', r'(・`ω\´・)', r'(´・ω・\`)')
    text = replace(text, '!', f'! {random.choice(smileys)}')
    text = replace(text, '?', '? owo')
    text = replace(text, '.', f'. {random.choice(smileys)}')
    for v in vowels:
        if 'n{v}' in text:
            text = text.replace(f'n{v}', f'ny{v}')
        if 'N{V}' in text:
            text = text.replace(f'N{v}', f"N{'Y' if v.isupper() else 'y', v}")
    await client.message_create(msg.channel, text)


@Bcom.commands(separator='|')
async def choose(client, message, *args):
    """lets the bot choose between two or more things use ``|`` to separate choices"""
    await client.message_create(message.channel, f'I choose {random.choice(args)}')
