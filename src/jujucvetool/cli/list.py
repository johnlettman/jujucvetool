import click
from rich_click import RichContext

from src.jujucvetool.cloud import Cloud


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
