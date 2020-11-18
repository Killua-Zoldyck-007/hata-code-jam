import random
from hata import Client, UserBase, ChannelBase, Embed, eventlist, Message
from hata.ext.commands import setup_ext_commands, FlaggedAnnotation, ConverterFlag, checks, Command
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

FUN_COMMANDS = eventlist(type_=Command)
Bcom: Client

def setup(lib):
    category = Bcom.command_processer.get_category("FUN")
#    if not category:
#        Bcom.command_processer.get_category("FUN")
    Bcom.commands.extend(FUN_COMMANDS)

def teardown(lib):
    Bcom.commands.unextend(FUN_COMMANDS)

@FUN_COMMANDS.from_class
class choose:
    category = 'fun'

    async def command(client, message, *args):
        """lets the bot choose between two or more things use ``|`` to separate choices"""
        await client.message_create(message.channel, f'I choose {random.choice(args)}')

@FUN_COMMANDS.from_class
class owo:
    category = 'fun'

    async def owo(client, msg, text):
        """owofies your text but you might not see the difference in short text"""
        def replace(s, old, new):
            li = s.rsplit(old, 1)
            return new.join(li)
    
        vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
        text = text.replace('L', 'W').replace('l', 'w')
        text = text.replace('R', 'W').replace('r', 'w')
        smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω\´・)', '(´・ω・\`)']
        text = replace(text, '!', f'! {random.choice(smileys)}')
        text = replace(text, '?', '? owo')
        text = replace(text, '.', f'. {random.choice(smileys)}')
        for v in vowels:
            if 'n{v}' in text:
                text = text.replace(f'n{v}', f'ny{v}')
            if 'N{V}' in text:
                text = text.replace(f'N{v}', f"N{'Y' if v.isupper() else 'y', v}")
        await client.message_create(msg.channel, text)

@FUN_COMMANDS.from_class
class separate:
    category = 'fun'

    async def separate(client, message, sep, *args):
        """separates the words using the given separator\nUsage: ``n!separate (separator) (the text you want to be separated)"""
        if not args:
            result = 'Nothing to separate'
        else:
            result = f" {sep} ".join(args)
        await client.message_create(message.channel, result)
