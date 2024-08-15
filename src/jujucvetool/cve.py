from enum import Enum
from functools import lru_cache
from functools import reduce
from logging import getLogger
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable

from cvescan.constants import UCT_DATA_URL
from cvescan.cvescanner import CVEScanner
from cvescan.scan_result import ScanResult
from ust_download_cache import USTDownloadCache

from src.jujucvetool.util import singleton


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    NEGLIGIBLE = 5

    @staticmethod
    def from_str(string: str) -> "Priority":
        return Priority[string.upper()]


ScanResults = Iterable[ScanResult]
ScanResultIDTransform = Callable[[str], str]
PrioritiesTally = Dict[Priority, int]


def sort_priority(results: ScanResults) -> ScanResults:
    return sorted(results, key=lambda result: Priority.from_str(result.priority).value)


def filter_unpatched(results: ScanResults) -> ScanResults:
    return filter(lambda result: result.fixed_version is not None, results)


def id_to_adoc_link(cve_id: str) -> str:
    return f"https://nvd.nist.gov/vuln/detail/{cve_id}[{cve_id}]"


def id_to_rich_link(cve_id: str) -> str:
    return f"[link=https://nvd.nist.gov/vuln/detail/{cve_id}]{cve_id}[/link]"


def transform_result_id(result: ScanResult, transform: ScanResultIDTransform) -> ScanResult:
    (cve_id, priority, package_name, fixed_version, repository) = result
    return ScanResult(transform(cve_id), priority, package_name, fixed_version, repository)


def map_result_ids(results: ScanResults, transform: ScanResultIDTransform) -> ScanResults:
    return map(lambda result: transform_result_id(result, transform), results)


def tally_priority(tally: PrioritiesTally, result: ScanResult) -> PrioritiesTally:
    priority = Priority.from_str(result.priority)
    tally[priority] = (tally[priority] + 1) if priority in tally else 1
    return tally


def tally_priorities(results: ScanResults) -> PrioritiesTally:
    return reduce(tally_priority, results, {})


@singleton
def get_ust_download_cache() -> USTDownloadCache:
    return USTDownloadCache(getLogger())


@lru_cache()
def get_ust_data_for(series: str = "xenial") -> Any:
    url = UCT_DATA_URL % series
    return get_ust_download_cache().get_data_from_url(url)


@singleton
def get_scanner() -> CVEScanner:
    return CVEScanner(getLogger())
