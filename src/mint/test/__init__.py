from mint import mint
from mint.test import local_settings as settings

def setup():
    mint.login(settings.username, settings.password)

def teardown():
    mint.logout()
