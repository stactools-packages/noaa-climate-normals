import unittest

import stactools.noaa_climate_normals


class TestModule(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(stactools.noaa_climate_normals.__version__)
