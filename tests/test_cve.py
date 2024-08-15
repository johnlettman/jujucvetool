import unittest
from unittest.mock import MagicMock

from cvescan.constants import UCT_DATA_URL
from cvescan.scan_result import ScanResult
from ust_download_cache import USTDownloadCache

from jujucvetool.cve import Priority, sort_priority, filter_unpatched, id_to_adoc_link, id_to_rich_link, \
    transform_result_id, map_result_ids, tally_priority, tally_priorities, get_ust_download_cache, get_ust_data_for, \
    get_scanner


class TestPriority(unittest.TestCase):
    def test_from_str(self):
        self.assertEqual(Priority.from_str('critical'), Priority.CRITICAL)
        self.assertEqual(Priority.from_str('high'), Priority.HIGH)
        self.assertEqual(Priority.from_str('medium'), Priority.MEDIUM)
        self.assertEqual(Priority.from_str('low'), Priority.LOW)
        self.assertEqual(Priority.from_str('negligible'), Priority.NEGLIGIBLE)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.results = [
            ScanResult('CVE-1234-5678', 'critical', 'package1', None, 'repo1'),
            ScanResult('CVE-2345-6789', 'high', 'package2', '1.0.1', 'repo2'),
            ScanResult('CVE-3456-7890', 'medium', 'package3', '2.0.0', 'repo3'),
            ScanResult('CVE-4567-8901', 'low', 'package4', None, 'repo4'),
        ]

    def test_sort_priority(self):
        sorted_results = sort_priority(self.results)
        sorted_priorities = [result.priority for result in sorted_results]
        self.assertEqual(sorted_priorities, ['critical', 'high', 'medium', 'low'])

    def test_filter_unpatched(self):
        unpatched_results = list(filter_unpatched(self.results))
        self.assertEqual(len(unpatched_results), 2)
        self.assertEqual(unpatched_results[0].cve_id, 'CVE-2345-6789')
        self.assertEqual(unpatched_results[1].cve_id, 'CVE-3456-7890')

    def test_id_to_adoc_link(self):
        link = id_to_adoc_link('CVE-1234-5678')
        self.assertEqual(link, 'https://nvd.nist.gov/vuln/detail/CVE-1234-5678[CVE-1234-5678]')

    def test_id_to_rich_link(self):
        link = id_to_rich_link('CVE-1234-5678')
        self.assertEqual(link, '[link=https://nvd.nist.gov/vuln/detail/CVE-1234-5678]CVE-1234-5678[/link]')

    def test_transform_result_id(self):
        transform = lambda x: x + '-transformed'
        transformed_result = transform_result_id(self.results[0], transform)
        self.assertEqual(transformed_result.cve_id, 'CVE-1234-5678-transformed')

    def test_map_result_ids(self):
        transform = lambda x: x + '-transformed'
        mapped_results = list(map_result_ids(self.results, transform))
        for result in mapped_results:
            self.assertTrue(result.cve_id.endswith('-transformed'))

    def test_tally_priority(self):
        tally = {}
        tally = tally_priority(tally, self.results[0])
        self.assertEqual(tally[Priority.CRITICAL], 1)

    def test_tally_priorities(self):
        tally = tally_priorities(self.results)
        self.assertEqual(tally[Priority.CRITICAL], 1)
        self.assertEqual(tally[Priority.HIGH], 1)
        self.assertEqual(tally[Priority.MEDIUM], 1)
        self.assertEqual(tally[Priority.LOW], 1)


class TestCachingFunctions(unittest.TestCase):
    def test_get_ust_download_cache(self):
        cache1 = get_ust_download_cache()
        cache2 = get_ust_download_cache()
        self.assertIs(cache1, cache2)

    def test_get_ust_data_for(self):
        mock_cache = MagicMock()
        mock_cache.get_data_from_url.return_value = 'mock_data'
        USTDownloadCache.__new__ = MagicMock(return_value=mock_cache)

        data = get_ust_data_for(series='focal')
        self.assertEqual(data, 'mock_data')

        url = UCT_DATA_URL % 'focal'
        mock_cache.get_data_from_url.assert_called_with(url)

    def test_get_scanner(self):
        scanner1 = get_scanner()
        scanner2 = get_scanner()
        self.assertIs(scanner1, scanner2)
