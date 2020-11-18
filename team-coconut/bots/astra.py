import config
from hata import Client
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand
from utils.utils import colourfunc
from utils.safe import SetupExternalSafeCommands

Astra: Client
setup_ext_commands(Astra, config.ASTRA_PREFIX)
SetupExternalSafeCommands(Astra)
Astra.commands(SubterraneanHelpCommand(color=colourfunc), 'help')
