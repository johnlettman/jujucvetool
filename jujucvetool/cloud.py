import json
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from fabric import Config
from fabric import Connection
from fabric import Result as FabricResult
from invoke import Result as InvokeResult
from invoke.context import Context

from jujucvetool.controller import Controller
from jujucvetool.model import Model
from jujucvetool.util import cached_property


class Cloud(Connection, Context):
    doas: str | None = None

    def __init__(self, host: str, doas: str | None = None, *args, **kwargs):
        self.doas = doas

        if host == "local":
            Context.__init__(self)
            self.original_host = host
        else:
            config = Config()
            config.update(
                connect_kwargs={
                    "look_for_keys": False,
                    "allow_agent": True,
                    "disabled_algorithms": dict(
                        pubkeys=["rsa-sha2-512", "rsa-sha2-256"], keys=["rsa-sha2-512", "rsa-sha2-256"]
                    ),
                }
            )

            Connection.__init__(self, host, config=config, *args, **kwargs)

    def open(self) -> None:
        if self.original_host != "local":
            Connection.open(self)

    def run(self, *args, **kwargs) -> Optional[Union[FabricResult, InvokeResult]]:
        if "hide" not in kwargs:
            kwargs["hide"] = True

        if "warn" not in kwargs:
            kwargs["warn"] = False

        if self.doas is None or self.doas == self.user:
            return (
                Context.run(self, *args, **kwargs)
                if self.original_host == "local"
                else Connection.run(self, *args, **kwargs)
            )
        else:
            return (
                Context.sudo(self, *args, user=self.doas, **kwargs)
                if self.original_host == "local"
                else Connection.sudo(self, *args, user=self.doas, **kwargs)
            )

    @cached_property
    def controllers(self) -> Iterable[Controller]:
        result = self.run("juju list-controllers --format=json").stdout
        parsed: Optional[Dict[str, Dict[str, Any]]] = json.loads(result)

        if parsed is None or "controllers" not in parsed:
            raise ValueError("Unable to parse controllers")

        names = parsed["controllers"].keys()
        return map(lambda name: Controller(name, self), names)

    @cached_property
    def hostname(self) -> str:
        return self.run("hostname").stdout

    @cached_property
    def has_openstack(self) -> bool:
        return self.run("which openstack").exited == 0

    @cached_property
    def has_juju(self) -> bool:
        return self.run("which juju").exited == 0

    def whoami(self) -> str:
        return self.run("whoami").stdout

    def filter(
        self, is_controllers: List[str], is_models: List[str], not_controllers: List[str], not_models: List[str]
    ) -> Generator[Model, None, None]:
        for controller in self.controllers:
            for model in controller.models:
                if (
                    len(is_controllers) == 0 or model.controller.name in is_controllers
                ) and model.controller.name not in not_controllers:
                    yield model
                elif (len(is_models) == 0 or model.name in is_models) and model.name not in not_models:
                    yield model
                elif (len(is_models) == 0 or model.short_name in is_models) and model.short_name not in not_models:
                    yield model

    def find(self, controller_name: str, model_name: str) -> Optional[Model]:
        for controller in self.controllers:
            if controller.name == controller_name:
                for model in controller.models:
                    if model.short_name == model_name or model.name == model_name:
                        return model

        # none found:
        return None
