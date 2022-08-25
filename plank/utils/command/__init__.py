from plank.utils.command.base import *
from plank.config import Configuration

class ProjectCreateCommand(BaseCommand):
    def __invoke__(self, parameters: Dict[str, Any]) -> NoReturn:
        pass



class ServerRunCommand(BaseCommand):
    def __invoke__(self, parameters: Dict[str, Any]) -> NoReturn:
        print("parameters:", parameters)
        configuration_path = Path(parameters["configuration"])
        application_program: str = parameters.get("program", "debug")

        Configuration.preload(path=configuration_path)
        configuration = Configuration.from_program(program_name=application_program)

        app = Application.construct_from_configuration(configuration=configuration)

        launch_options = parameters["launch_options"]
        options = {
            key: value
            for key, value in [ option.split("=") for option in  launch_options]
        }
        print("app:", app, app.name)
        print("configuration.plugin.prefix:", configuration.plugin.prefix)
        app.launch(program=application_program, **options)

        # server: FastAPIServer = FastAPIServer.build(name=configuration.app.name, version=configuration.app.version,
        #                                             build_version=configuration.app.build_version,
        #                                             delegate=AppDelegate(), workspace=workspace, path_prefix="irian")


        # package_namespace, delegate_class_name = application_delegate.split(":")

        # workspace_path = Path(application_workspace)
        # module = importlib.import_module(package_namespace)
        # delegate_type = getattr(module, delegate_class_name)

        # app = Application.construct(name=application_name, version=application_version, delegate_type=delegate_type, workspace_path=workspace_path)
        # app.launch(program=application_program, store_id="s002_001")
        # print("app:", app)
        # server = FastAPIServer(binding=BindAddress(host="0.0.0.0", port=8080), application=app,
        #                        build_version="2022-07-25.000001",
        #                        path_prefix="irian", swagger_secrets_username="awoo", swagger_secrets_password="iamai")

    def __arguments__(self) -> List[click.Argument]:
        return [click.Argument(["launch_options"], nargs=-1, default=None)]

    def __options__(self) -> List[click.Option]:
        return [
            click.Option(["-t", "--server-type"], default="http", type=click.Choice(["http", "grpc"]), show_choices=True),
            click.Option(["-c", "--configuration"], required=True),
            click.Option(["-p", "--program"], default="debug")
            # click.Option(["--instance-type"], default="application", type=click.Choice(["application", "plugin"]), show_choices=True)
        ]


# class ServerRunCommand(click.MultiCommand):
#
#     def list_commands(self, ctx):
#         return ["application", "plugin"]
#
#     def get_command(self, ctx:click.Context, name: str):
#         print("name:", name, ctx.parent, ctx.info_name, ctx.params, ctx.meta)
#         return click.Command(name=name, callback=lambda *args, **kwargs: print("hello run:", args, kwargs))

class PolymathServerCommand(click.MultiCommand):

    def list_commands(self, ctx):
        return ["run"]

    def get_command(self, ctx:click.Context, name: str):
        return ServerRunCommand(name=name).make_command()

class PolymathProjectCommand(click.MultiCommand):

    def list_commands(self, ctx):
        return ["create"]

    def get_command(self, ctx:click.Context, name: str):
        return ProjectCreateCommand(name=name).make_command()


class PolymathConfigCommand(click.MultiCommand):

    def list_commands(self, ctx):
        return ["create"]

    def get_command(self, ctx:click.Context, name: str):
        return ProjectCreateCommand(name=name).make_command()


root_cmd = click.Group()
root_cmd.add_command( PolymathServerCommand(help=''), name="server")
root_cmd.add_command( PolymathProjectCommand(help=''), name="project")
root_cmd.add_command( PolymathConfigCommand(help=''), name="config")

# root_cmd.add_command( PolymathServerCommand(help=''), name="application")
# root_cmd.add_command( PolymathServerCommand(help=''), name="plugin")