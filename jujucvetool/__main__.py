#!/usr/bin/env python3
import logging
from importlib.metadata import PackageNotFoundError, version
from typing import Union, Optional, List

import fabric
import rich_click as click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.traceback import install as install_traceback
from rich_click import RichContext, rich_click

from jujucvetool.cloud import Cloud

PROGRAM_NAME = "jujucvetool"
PROGRAM_VERSION = "unknown"
try:
    PROGRAM_VERSION = version(PROGRAM_NAME)
except PackageNotFoundError:
    pass

LOGGING_LEVELS = {
    0: logging.ERROR,
    1: logging.WARN,
    2: logging.INFO,
    3: logging.DEBUG,
}

logger = logging.getLogger(__name__)

click.rich_click.COMMAND_GROUPS = {}
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_OPTION_DEFAULT = "dim cyan"

click.rich_click.ERRORS_SUGGESTION = (
    "[b][i]D'oh![/i][/b] That's not right. "
    "Try running the '--help' flag for more information.\n"
)

click.rich_click.ERRORS_EPILOGUE = (
    "Project: "
    "[link=https://github.com/johnlettman/jujucvetool]"
    "https://github.com/johnlettman/jujucvetool"
    "[/link]"
)


def configure_logging(logging_level: Union[int, str, None]) -> None:
    logging.basicConfig(
        level=logging_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                locals_max_length=4,
                markup=True,
            )
        ],
    )
    logger.debug(
        "Logger configured with level %s",
        logging.getLevelName(logging_level or logging.NOTSET),
    )

    install_traceback(show_locals=True, suppress=[rich_click, click])
    logger.debug("Traceback handler installed.")


@click.group(PROGRAM_NAME)
@click.option(
    "--host",
    "-h",
    metavar="HOSTNAME",
    type=click.STRING,
    default="local",
    help="Login to the specified host for interacting with Juju. [b][cyan]Defaults to local.[/cyan][/b]")
@click.option(
    "--user",
    "-u",
    metavar="USERNAME",
    type=click.STRING,
    default=None,
    help="Login with specified user for interacting with Juju.")
@click.option(
    "--verbose",
    "-v",
    metavar="V",
    type=click.IntRange(0, 3, clamp=True),
    count=True,
    help="Increase logging verbosity.")
@click.pass_context
@click.version_option(PROGRAM_VERSION, "--version", "-V")
def main(context: RichContext, host: str, user: Optional[str], verbose: int = 0) -> None:
    context.ensure_object(dict)

    # configure program-wide logging
    context.obj["loglevel"] = LOGGING_LEVELS[verbose]
    configure_logging(context.obj["loglevel"])

    # configure SSH connections
    fabric.Config.global_defaults()
    conf = fabric.Config()
    conf.update(connect_kwargs={
        'look_for_keys': False,
        "allow_agent": True,
        "disabled_algorithms": dict(
            pubkeys=["rsa-sha2-512", "rsa-sha2-256"],
            keys=["rsa-sha2-512", "rsa-sha2-256"])
    })

    # connect to cloud
    context.obj["cloud"] = Cloud(host, user, config=conf)


click.rich_click.OPTION_GROUPS[PROGRAM_NAME] = [
    {"name": "Connection", "options": ["--host", "--user"]}
]


@click.command("list-controllers")
@click.pass_context
def list_controllers(context: RichContext):
    cloud: Cloud = context.obj["cloud"]

    for controller in cloud.controllers:
        print(str(controller))


@click.command("list-models")
@click.pass_context
def list_models(context: RichContext):
    cloud: Cloud = context.obj["cloud"]

    for controller in cloud.controllers:
        for model in controller.models:
            print(str(model))


FORMAT_GROUP = {"name": "Formatting", "options": ["--fancy/--no-fancy"]}
FILTERS_GROUP = {"name": "Selection", "options": ["--controller", "--model", "--skip-controller", "--skip-model"]}


@click.command("get-manifests")
@click.option(
    "--fancy/--no-fancy",
    type=click.BOOL,
    default=True,
    help="Use fancy output.")
@click.option(
    "--controller",
    "-c",
    metavar="CONTROLLER",
    type=click.STRING,
    multiple=True,
    help="\n\n".join([
        "Process the specified controller. [b][cyan]Supports multiple.[/cyan][/b]",
        "[i]When specified, this overrides the default behavior of selecting all controllers.[/i]"
    ]))
@click.option(
    "--model",
    "-m",
    metavar="MODEL",
    type=click.STRING,
    multiple=True,
    help="\n\n".join([
        "Process the specified controller. [b][cyan]Supports multiple.[/cyan][/b]",
        "[i]When specified, this overrides the default behavior of selecting all models.[/i]"
    ]))
@click.option(
    "--skip-controller",
    "-C",
    metavar="CONTROLLER",
    type=click.STRING,
    multiple=True,
    help="Skip processing the specified controller. [b][cyan]Supports multiple.[/cyan][/b]")
@click.option(
    "--skip-model",
    "-M",
    metavar="MODEL",
    type=click.STRING,
    multiple=True,
    help="Skip processing the specified model. [b][cyan]Supports multiple.[/cyan][/b]")
@click.pass_context
def get_manifests(context: RichContext, fancy: bool, controller: List[str], model: List[str],
                  skip_controller: List[str], skip_model: List[str]):
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    for model in cloud.filter(controller, model, skip_controller, skip_model):
        for machine in model.machines:
            if fancy:
                table = Table(title=machine.hostname, title_justify="left", row_styles=["dim", ""])
                table.add_column("Package", justify="left", style="bold cyan", no_wrap=True)
                table.add_column("Version", justify="left", style="green", no_wrap=True)

                for line in machine.manifest.splitlines():
                    (package, package_version) = line.split("\t")
                    table.add_row(package, package_version)

                console.print(table)
            else:
                console.print(machine.manifest)


click.rich_click.OPTION_GROUPS[" ".join([PROGRAM_NAME, "get-manifests"])] = [
    FORMAT_GROUP,
    FILTERS_GROUP
]

main.add_command(list_controllers)
main.add_command(list_models)
main.add_command(get_manifests)

if __name__ == "__main__":
    main(obj={}, prog_name=PROGRAM_NAME)
