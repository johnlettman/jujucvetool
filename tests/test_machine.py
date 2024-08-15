import unittest
from unittest.mock import MagicMock, patch
from fabric import Result as FabricResult
from invoke import Result as InvokeResult
from jujucvetool.machine import Machine


class TestMachine(unittest.TestCase):
    def setUp(self):
        self.model = MagicMock()
        self.model.__str__.return_value = 'test-model'
        self.machine = Machine(machine_id='1', model=self.model)

    def test_machine_str(self):
        self.assertEqual(str(self.machine), '1')

    def test_reference_property(self):
        reference = self.machine.reference
        self.assertEqual(reference, '-m test-model 1')

    def test_controller_property(self):
        self.model.controller = MagicMock()
        self.assertEqual(self.machine.controller, self.model.controller)

    def test_cloud_property(self):
        self.model.cloud = MagicMock()
        self.assertEqual(self.machine.cloud, self.model.cloud)
