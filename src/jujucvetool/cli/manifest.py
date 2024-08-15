from io import TextIOWrapper
from logging import getLogger
from os import path
from typing import List
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich_click import RichContext
import rich_click as click

from jujucvetool.cloud import Cloud


logger = getLogger(__name__)


def print_manifest(console: Console, hostname: str, manifest: str, fancy: bool) -> None:
    if fancy:
        table = Table(title=hostname, title_justify="left", row_styles=["dim", ""])
        table.add_column("Package", justify="left", style="bold cyan", no_wrap=True)
        table.add_column("Version", justify="left", style="green", no_wrap=True)

        for line in manifest.splitlines():
            (package, package_version) = line.split("\t")
            table.add_row(package, package_version)

        console.print(table)
    else:
        console.print(manifest)


@click.command("get-manifests", help="Get manifests for all machines on the specified cloud.")
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
@click.option(
    "--output",
    "-o",
    metavar="DIR",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    required=False,
    default=None,
    help="Output the manifests to the specified directory.",
)
@click.pass_context
def get_manifests(
    context: RichContext,
    fancy: bool,
    controller: List[str],
    model: List[str],
    skip_controller: List[str],
    skip_model: List[str],
    output: Optional[str],
) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    for cloud_model in cloud.filter(controller, model, skip_controller, skip_model):
        for selected_machine in cloud_model.machines:
            hostname = selected_machine.hostname
            manifest = selected_machine.manifest

            if output:
                output_path = path.join(output, f"{selected_machine.slug}.manifest")
                with open(output_path, "w") as output_file:
                    output_file.write(manifest)
                    output_file.close()
                    logger.info(f"Wrote manifest for {hostname} to {output_path}")
            else:
                print_manifest(console, hostname, manifest, fancy)


click.rich_click.OPTION_GROUPS["jujucvetool get-manifests"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "--skip-controller", "--skip-model"]},
]


@click.command("get-manifest", help="Get the manifest for a specified machine.")
@click.option("--fancy/--no-fancy", type=click.BOOL, default=True, help="Use fancy output.")
@click.option(
    "--controller",
    "-c",
    metavar="CONTROLLER",
    type=click.STRING,
    required=True,
    help="Process the specified controller.",
)
@click.option(
    "--model",
    "-m",
    metavar="MODEL",
    type=click.STRING,
    required=True,
    help="Process the specified model.",
)
@click.option(
    "-o",
    "--output",
    metavar="FILE",
    type=click.File(mode="w", encoding="utf-8"),
    required=False,
    default=None,
    help="Output the manifest to the specified file.",
)
@click.argument("machine", metavar="ID", type=click.STRING)
@click.pass_context
def get_manifest(
    context: RichContext, fancy: bool, controller: str, model: str, machine: str, output: Optional[TextIOWrapper]
) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    selected_model = cloud.find(controller, model)
    if not selected_model:
        raise ValueError("Could not find the specified model")

    selected_machine = selected_model.find(machine)
    if not selected_machine:
        raise ValueError("Could not find the specified machine")

    hostname = selected_machine.hostname
    manifest = selected_machine.manifest

    if output:
        output.write(manifest)
        output.close()
    else:
        print_manifest(console, hostname, manifest, fancy)


click.rich_click.OPTION_GROUPS["jujucvetool get-manifest"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "machine"]},
    {"name": "Output", "options": ["--output"]},
]
