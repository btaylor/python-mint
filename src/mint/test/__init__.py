from mint import mint
from mint import local_settings as settings

def setup():
    mint.login(settings.username, settings.password)

def teardown():
    mint.logout()
