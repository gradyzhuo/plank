__version__ = "1.8"

from .app import Application, ApplicationDelegate

def invoke(app_delegate: ApplicationDelegate, **launch_options):
    app = Application(delegate=app_delegate)
    app.launch(**launch_options)