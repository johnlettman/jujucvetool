import click
from rich_click import RichContext

from jujucvetool.cloud import Cloud


@click.command("list-controllers", help="List controllers on the specified cloud.")
@click.pass_context
def list_controllers(context: RichContext):
    cloud: Cloud = context.obj["cloud"]

    for controller in cloud.controllers:
        print(str(controller))


@click.command("list-models", help="List models on the specified cloud.")
@click.pass_context
def list_models(context: RichContext):
    cloud: Cloud = context.obj["cloud"]

    for controller in cloud.controllers:
        for model in controller.models:
            print(str(model))
