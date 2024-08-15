from shlex import quote as shell_quote
from typing import TYPE_CHECKING
from typing import Dict
from typing import Optional
from typing import Union

from cvescan.dpkg_parser import get_installed_pkgs_from_manifest as packages_from_manifest
from fabric import Result as FabricResult
from invoke import Result as InvokeResult
from slugify import slugify

from jujucvetool.cve import ScanResults
from jujucvetool.cve import get_scanner
from jujucvetool.cve import get_ust_data_for
from jujucvetool.util import cached_property
from jujucvetool.util import codename_from_manifest


if TYPE_CHECKING:
    from jujucvetool.cloud import Cloud
    from jujucvetool.controller import Controller
    from jujucvetool.model import Model


class Machine:
    machine_id: str
    model: "Model"

    def __init__(self, machine_id: str, model: "Model"):
        self.machine_id = machine_id
        self.model = model

    def __str__(self) -> str:
        return str(self.machine_id)

    @property
    def reference(self) -> str:
        return f"-m {str(self.model)} {self.machine_id}"

    @property
    def slug(self) -> str:
        return slugify(f"{str(self.model)}.{str(self)}")

    @property
    def controller(self) -> "Controller":
        return self.model.controller

    @property
    def cloud(self) -> "Cloud":
        return self.model.cloud

    def run(self, command: str) -> Optional[Union[FabricResult, InvokeResult]]:
        model = shell_quote(str(self.model))
        machine_id = shell_quote(str(self.machine_id))
        command = f"juju ssh --model={model} {machine_id} -- {command}"
        return self.cloud.run(command)

    @cached_property
    def hostname(self) -> str:
        return self.run("hostname").stdout

    @property
    def manifest(self) -> str:
        return self.run("dpkg-query -W").stdout

    @property
    def packages(self) -> Dict[str, str]:
        return packages_from_manifest(self.manifest)

    @cached_property
    def codename(self) -> str:
        return codename_from_manifest(self.packages)

    @property
    def cves(self) -> ScanResults:
        data = get_ust_data_for(self.codename)
        scanner = get_scanner()

        return scanner.scan(self.codename, data, self.packages)
