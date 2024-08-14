import json
from shlex import quote as shell_quote
from typing import TYPE_CHECKING, Iterable, Optional, Dict, Any

from jujucvetool.machine import Machine

if TYPE_CHECKING:
    from jujucvetool.cloud import Cloud
    from jujucvetool.controller import Controller


class Model:
    name: str
    short_name: str
    controller: "Controller"

    def __init__(self, name: str, short_name: str, controller: "Controller"):
        self.name = name
        self.short_name = short_name
        self.controller = controller

    def __str__(self) -> str:
        return f"{self.controller}:{self.name}"

    @property
    def cloud(self) -> "Cloud":
        return self.controller.cloud

    @property
    def machines(self) -> Iterable[Machine]:
        model = shell_quote(str(self))
        command = f"juju list-machines --format=json --model={model}"
        result = self.cloud.run(command).stdout
        parsed: Optional[Dict[str, Dict[str, Any]]] = json.loads(result)

        if parsed is None or "machines" not in parsed:
            raise ValueError("Unable to parse machines")

        machine_ids = parsed["machines"].keys()
        return map(lambda machine_id: Machine(machine_id, self), machine_ids)
