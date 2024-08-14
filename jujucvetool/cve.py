from functools import reduce

from cvescan.scan_result import ScanResult
from enum import Enum
from typing import Iterable, Dict

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
PrioritiesTally = Dict[Priority, int]

def sort_priority(results: ScanResults) -> ScanResults:
    return sorted(results, key=lambda result: Priority.from_str(result.priority).value)

def filter_unpatched(results: ScanResults) -> ScanResults:
    return filter(lambda result: result.fixed_version is not None, results)

def transform_id_to_adoc_link(result: ScanResult) -> ScanResult:
    (cve_id, priority, package_name, fixed_version, repository) = result
    return ScanResult(f"https://nvd.nist.gov/vuln/detail/{cve_id}[{cve_id}]",
                      priority, package_name, fixed_version, repository)

def map_id_to_adoc_link(results: ScanResults) -> ScanResults:
    return map(transform_id_to_adoc_link, results)

def tally_priority(tally: PrioritiesTally, result: ScanResult) -> PrioritiesTally:
    priority = Priority.from_str(result.priority)
    tally[priority] = (tally[priority] + 1) if priority in tally else 1
    return tally

def tally_priorities(results: ScanResults) -> PrioritiesTally:
    return reduce(tally_priority, results, {})
