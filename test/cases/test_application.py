import unittest
from plank.app import *
from plank.plugin import Plugin

class ApplicationDelegate(Application.Delegate):

    def __init__(self):
        self.launch_options = None
        self.will_launch_mark = False
        self.did_launch_mark = False


    def application_will_launch(self, app: Application, launch_options: Dict[str, Any]):
        self.will_launch_mark = True
        self.launch_options = launch_options

    def application_did_launch(self, app: Application):
        self.did_launch_mark = True

    def application_did_discover_plugins(self, app: Application, plugins: List[Plugin]):
        print(plugins)


class ApplicationTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.test_configuration = Configuration.build(name="TestConfiguration", config_dict={
            "plugin": {
                "plugin.prefix": ["unittest_plugin"]
            },
            "path": {
                "path.workspace": "${HOME}",
                "path.data": "${path.workspace}/data",
                "path.plugin": "${path.data}/${PLUGIN}"
            }
        })

    def test_launch_delegate(self):
        delegate = ApplicationDelegate()
        app = Application(delegate=delegate, configuration=self.test_configuration)
        app.launch(test="value")

        print(app.plugins)
        self.assertEqual(delegate.will_launch_mark, True)  # add assertion here
        self.assertEqual(delegate.did_launch_mark, True)
        self.assertEqual(delegate.launch_options, {"test": "value"})


if __name__ == '__main__':
    unittest.main()
