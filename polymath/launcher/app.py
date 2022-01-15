from polymath.app import Application
from polymath.launcher import Launcher

class SimpleLauncher(Launcher):

    @property
    def app(self)->Application:
        return self.__app

    def __init__(self, app: Application):
        self.__app = app
        app.did_set_launcher(self)

    def launch(self, **options):
        self.app.launch(**options)