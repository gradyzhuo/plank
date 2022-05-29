import importlib
from pathlib import Path
from polymath.app import Application
from polymath.commandline.base import *
from polymath import logger

class ProjectCreateCommand(BaseCommand):
    def __invoke__(self, parameters: Dict[str, Any]) -> NoReturn:
        pass



class ServerRunCommand(BaseCommand):
    def __invoke__(self, parameters: Dict[str, Any]) -> NoReturn:
        print("parameters:", parameters)
        application_name = parameters["application_name"]
        application_version = parameters["application_version"]
        application_workspace = parameters["application_workspace"]
        application_delegate: str = parameters["application_delegate"]
        application_program: str = parameters["application_program"]
        package_namespace, delegate_class_name = application_delegate.split(":")

        workspace_path = Path(application_workspace)
        module = importlib.import_module(package_namespace)
        delegate_type = getattr(module, delegate_class_name)

        app = Application.construct(name=application_name, version=application_version, delegate_type=delegate_type, workspace_path=workspace_path)
        app.launch(program=application_program, store_id="s002_001")
        print("app:", app)
        # server = FastAPIServer(binding=BindAddress(host="0.0.0.0", port=8080), application=app,
        #                        build_version="2022-07-25.000001",
        #                        path_prefix="irian", swagger_secrets_username="awoo", swagger_secrets_password="iamai")

    def __arguments__(self) -> List[click.Argument]:
        pass

    def __options__(self) -> List[click.Option]:
        return [
            click.Option(["-t", "--server-type"], default="http", type=click.Choice(["http", "grpc"]), show_choices=True),
            click.Option(["-n", "--application-name"], required=True),
            click.Option(["-v", "--application-version"], required=True),
            click.Option(["-d", "--application-delegate"], required=True, help="form: {package.namespace}:{delegate_class}"),
            click.Option(["-w", "--application-workspace"], required=True),
            click.Option(["-p", "--application-program"], default="release")

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


root_cmd = click.Group()
root_cmd.add_command( PolymathServerCommand(help=''), name="server")
root_cmd.add_command( PolymathProjectCommand(help=''), name="project")

# root_cmd.add_command( PolymathServerCommand(help=''), name="application")
# root_cmd.add_command( PolymathServerCommand(help=''), name="plugin")