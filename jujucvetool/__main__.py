#!/usr/bin/env python3
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version
import logging
from typing import Optional
from typing import Union

import fabric
from rich.logging import RichHandler
from rich.traceback import install as install_traceback
from rich_click import RichContext
from rich_click import rich_click
import rich_click as click

from jujucvetool.cli.cve import cves_for
from jujucvetool.cli.list import list_controllers
from jujucvetool.cli.list import list_models
from jujucvetool.cli.manifest import get_manifest
from jujucvetool.cli.manifest import get_manifests
from jujucvetool.cloud import Cloud


PROGRAM_NAME = "jujucvetool"

try:
    PROGRAM_VERSION = version(PROGRAM_NAME)
except PackageNotFoundError:
    # we will simply fall back to "unknown"
    PROGRAM_VERSION = "unknown"

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
    "[b][i]D'oh![/i][/b] That's not right. " "Try running the '--help' flag for more information.\n"
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


@click.group("jujucvetool")
@click.option(
    "--host",
    "-h",
    metavar="HOSTNAME",
    type=click.STRING,
    default="local",
    help="Login to the specified host for interacting with Juju. [b][cyan]Defaults to local.[/cyan][/b]",
)
@click.option(
    "--user",
    "-u",
    metavar="USERNAME",
    type=click.STRING,
    default=None,
    help="Login with specified user for interacting with Juju.",
)
@click.option(
    "--verbose",
    "-v",
    metavar="V",
    type=click.IntRange(0, 3, clamp=True),
    count=True,
    help="Increase logging verbosity.",
)
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
    conf.update(
        connect_kwargs={
            "look_for_keys": False,
            "allow_agent": True,
            "disabled_algorithms": dict(
                pubkeys=["rsa-sha2-512", "rsa-sha2-256"], keys=["rsa-sha2-512", "rsa-sha2-256"]
            ),
        }
    )

    # connect to cloud
    context.obj["cloud"] = Cloud(host, user, config=conf)


click.rich_click.OPTION_GROUPS["jujucvetool"] = [{"name": "Connection", "options": ["--host", "--user"]}]

main.add_command(list_controllers)
main.add_command(list_models)
main.add_command(get_manifest)
main.add_command(get_manifests)
main.add_command(cves_for)

if __name__ == "__main__":
    main(obj={}, prog_name="jujucvetool")
