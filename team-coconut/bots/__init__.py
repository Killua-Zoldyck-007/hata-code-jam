import os

from hata import Client, CLIENTS
from hata.ext.extension_loader import EXTENSION_LOADER

import config

Reimu = Client(config.REIMU_TOKEN, name='Reimu')
Bcom = Client(config.BCOM_TOKEN, name='Bcom')
Astra = Client(config.ASTRA_TOKEN, name='Astra')

TO_LOAD = ['bcom', 'reimu', 'astra', 'common']

CLIENT_CONTEXT = {}
for client in CLIENTS:
    CLIENT_CONTEXT[client.name] = client

for path in TO_LOAD:
    EXTENSION_LOADER.load_extension(f'bots.{path}', **CLIENT_CONTEXT)  # loads the bots

EXTENSIONS = []

for path in os.listdir('extensions'):
    if path.endswith('.py'):
        EXTENSIONS.append(path[:-3])

for path in EXTENSIONS:
    EXTENSION_LOADER.add('extensions.'+path, **CLIENT_CONTEXT)

EXTENSION_LOADER.load_all()  # loads the Extensions
