from typing import List

from rich.console import Console
from rich.table import Table
from rich_click import RichContext
import rich_click as click

from jujucvetool.cloud import Cloud
from jujucvetool.machine import Machine


def print_manifest(console: Console, fancy: bool, machine: Machine) -> None:
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


@click.command("get-manifests")
@click.option("--fancy/--no-fancy", type=click.BOOL, default=True, help="Use fancy output.")
@click.option(
    "--controller",
    "-c",
    metavar="CONTROLLER",
    type=click.STRING,
    multiple=True,
    help="\n\n".join(
        [
            "Process the specified controller. [b][cyan]Supports multiple.[/cyan][/b]",
            "[i]When specified, this overrides the default behavior of selecting all controllers.[/i]",
        ]
    ),
)
@click.option(
    "--model",
    "-m",
    metavar="MODEL",
    type=click.STRING,
    multiple=True,
    help="\n\n".join(
        [
            "Process the specified model. [b][cyan]Supports multiple.[/cyan][/b]",
            "[i]When specified, this overrides the default behavior of selecting all models.[/i]",
        ]
    ),
)
@click.option(
    "--skip-controller",
    "-C",
    metavar="CONTROLLER",
    type=click.STRING,
    multiple=True,
    help="Skip processing the specified controller. [b][cyan]Supports multiple.[/cyan][/b]",
)
@click.option(
    "--skip-model",
    "-M",
    metavar="MODEL",
    type=click.STRING,
    multiple=True,
    help="Skip processing the specified model. [b][cyan]Supports multiple.[/cyan][/b]",
)
@click.pass_context
def get_manifests(
    context: RichContext,
    fancy: bool,
    controller: List[str],
    model: List[str],
    skip_controller: List[str],
    skip_model: List[str],
) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    for cloud_model in cloud.filter(controller, model, skip_controller, skip_model):
        for machine in cloud_model.machines:
            print_manifest(console, fancy, machine)


click.rich_click.OPTION_GROUPS["jujucvetool get-manifests"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "--skip-controller", "--skip-model"]},
]


@click.command("get-manifest")
@click.option("--fancy/--no-fancy", type=click.BOOL, default=True, help="Use fancy output.")
@click.option(
    "--controller",
    "-c",
    metavar="CONTROLLER",
    type=click.STRING,
    required=True,
    help="\n\n".join(["Process the specified controller."]),
)
@click.option(
    "--model",
    "-m",
    metavar="MODEL",
    type=click.STRING,
    required=True,
    help="\n\n".join(["Process the specified model."]),
)
@click.argument("machine", metavar="ID", type=click.STRING)
@click.pass_context
def get_manifest(context: RichContext, fancy: bool, controller: str, model: str, machine: str) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    selected_model = cloud.find(controller, model)
    if not selected_model:
        raise ValueError("Could not find the specified model")

    selected_machine = selected_model.find(machine)
    if not selected_machine:
        raise ValueError("Could not find the specified machine")

    print_manifest(console, fancy, selected_machine)


click.rich_click.OPTION_GROUPS["jujucvetool get-manifest"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "machine"]},
]
