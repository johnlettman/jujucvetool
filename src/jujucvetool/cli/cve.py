from io import TextIOWrapper
from typing import List
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich_click import RichContext
import rich_click as click

from jujucvetool.cloud import Cloud
from jujucvetool.cve import ScanResults
from jujucvetool.cve import ScanResultsByMachine
from jujucvetool.cve import id_to_rich_link
from jujucvetool.cve import map_result_ids
from jujucvetool.cve import results_by_machine_to_csv
from jujucvetool.cve import results_by_machine_to_json
from jujucvetool.machine import Machine


def machine_title(machine: Machine) -> str:
    return f"[bold green]:laptop_computer-emoji: {machine.hostname}[/] " f"in [purple]{str(machine.model)}[/]"


def print_results_fancy(console: Console, results: ScanResults, machine: Machine) -> None:
    table = Table(title=machine_title(machine), title_justify="left", row_styles=["dim", ""])
    table.add_column("CVE", justify="left", style="bold cyan", no_wrap=True)
    table.add_column("Priority", justify="left", style="green", no_wrap=True)
    table.add_column("Package", justify="left", style="green", no_wrap=True)
    table.add_column("Fixed Version", justify="left", style="green", no_wrap=True)
    table.add_column("Repository", justify="right", style="green", no_wrap=True)

    for result in map_result_ids(results, id_to_rich_link):
        table.add_row(*result)

    console.print(table)


def print_results_plain(console: Console, results: ScanResults, machine: Machine) -> None:
    console.print(machine_title(machine))
    for result in map_result_ids(results, id_to_rich_link):
        (cve, priority, package, fixed_version, repository) = result
        console.print(
            f"[cyan]{cve}[/] | {priority} | [orange]{package}[/] | fixed in: {fixed_version} | repo: {repository}"
        )


def print_results(console: Console, results: ScanResults, machine: Machine, fancy: bool = True) -> None:
    print_results_fancy(console, results, machine) if fancy else print_results_plain(console, results, machine)


def output_results_by_machine(file: TextIOWrapper, results: ScanResultsByMachine, format="csv"):
    if format == "csv":
        results_by_machine_to_csv(file, results)
    elif format == "json":
        results_by_machine_to_json(file, results)


@click.command("cves", help="List CVEs across machines on the specified cloud.")
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
    metavar="FILE",
    type=click.File(mode="w", encoding="utf-8"),
    required=False,
    default=None,
    help="Output the results to the specified file.",
)
@click.option(
    "--format",
    "-f",
    metavar="FORMAT",
    type=click.Choice(["csv", "json", "adoc", "pdf"], case_sensitive=False),
    default="csv",
    show_default=True,
    help="Output the results with the specified format.",
)
@click.pass_context
def cves(
    context: RichContext,
    fancy: bool,
    controller: List[str],
    model: List[str],
    skip_controller: List[str],
    skip_model: List[str],
    output: Optional[TextIOWrapper],
    format: str,
) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    filtered = cloud.filter(controller, model, skip_controller, skip_model)

    if output:
        output_results_by_machine(output, [(m, m.cves) for m in filtered for m in m.machines], format)
    else:
        for _model in filtered:
            for _machine in _model.machines:
                print_results(console, _machine.cves, _machine, fancy)


click.rich_click.OPTION_GROUPS["jujucvetool cves"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "--skip-controller", "--skip-model"]},
]


@click.command("cves-for", help="List CVEs for a specific machine.")
@click.option("--fancy/--no-fancy", type=click.BOOL, default=True, help="Use fancy output.")
@click.option(
    "--controller",
    "-c",
    metavar="CONTROLLER",
    type=click.STRING,
    required=True,
    help="Process the specified controller.",
)
@click.option("--model", "-m", metavar="MODEL", type=click.STRING, required=True, help="Process the specified model.")
@click.argument("machine", metavar="ID", type=click.STRING)
@click.option(
    "--output",
    "-o",
    metavar="FILE",
    type=click.File(mode="w", encoding="utf-8"),
    required=False,
    default=None,
    help="Output the results to the specified file.",
)
@click.option(
    "--format",
    "-f",
    metavar="FORMAT",
    type=click.Choice(["csv", "json", "adoc", "pdf"], case_sensitive=False),
    default="csv",
    show_default=True,
    help="Output the results with the specified format.",
)
@click.pass_context
def cves_for(
    context: RichContext,
    fancy: bool,
    controller: str,
    model: str,
    machine: str,
    output: Optional[TextIOWrapper],
    format: str,
) -> None:
    cloud: Cloud = context.obj["cloud"]
    console = Console()

    _model = cloud.find(controller, model)
    if not _model:
        raise ValueError("Could not find the specified model")

    _machine = _model.find(machine)
    if not _machine:
        raise ValueError("Could not find the specified machine")

    if output:
        output_results_by_machine(output, [(_machine, _machine.cves)], format)
    else:
        print_results(console, _machine.cves, _machine, fancy)


click.rich_click.OPTION_GROUPS["jujucvetool cves-for"] = [
    {"name": "Formatting", "options": ["--fancy/--no-fancy"]},
    {"name": "Selection", "options": ["--controller", "--model", "machine"]},
    {"name": "Output", "options": ["--output", "--format"]},
]

# TODO:
