import json
from shlex import quote as shell_quote
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional

from src.jujucvetool.model import Model
from src.jujucvetool.util import cached_property


if TYPE_CHECKING:
    from src.jujucvetool.cloud import Cloud


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
