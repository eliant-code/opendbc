"""BluePilot Ford lateral safety tests (opendbc/bluepilot_lateral/safety/tests), run as part of this suite so
its coverage requirement sees the BluePilot paths in modes/ford.h."""
import unittest

from opendbc.bluepilot_lateral.safety.tests import (test_ford_bluepilot, test_ford_bluepilot_angle_mode, test_ford_bluepilot_limits,
                                                    test_ford_bluepilot_matrix, test_ford_bluepilot_pinion)

MODULES = (test_ford_bluepilot, test_ford_bluepilot_angle_mode, test_ford_bluepilot_limits, test_ford_bluepilot_matrix, test_ford_bluepilot_pinion)


def load_tests(loader, standard_tests, pattern):
  suite = unittest.TestSuite()
  for m in MODULES:
    suite.addTests(loader.loadTestsFromModule(m))
  return suite


if __name__ == "__main__":
  unittest.main()
