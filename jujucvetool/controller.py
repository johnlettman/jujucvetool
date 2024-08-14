import json
from typing import TYPE_CHECKING, Optional, Dict, Any, Iterable
from shlex import quote as shell_quote

from jujucvetool.model import Model
from jujucvetool.util import cached_property

if TYPE_CHECKING:
    from jujucvetool.cloud import Cloud


class Controller:
    name: str
    cloud: "Cloud"

    def __init__(self, name: str, cloud: "Cloud"):
        self.name = name
        self.cloud = cloud

    def __str__(self) -> str:
        return self.name

    @cached_property
    def models(self) -> Iterable[Model]:
        controller = shell_quote(self.name)
        command = f"juju list-models --format=json --controller={controller}"
        result = self.cloud.run(command).stdout
        parsed: Optional[Dict[str, Dict[str, Any]]] = json.loads(result)

        if parsed is None or "models" not in parsed:
            raise ValueError("Unable to parse models")

        models = parsed["models"]
        return map(lambda model: Model(model["name"], model["short-name"], self), models)
