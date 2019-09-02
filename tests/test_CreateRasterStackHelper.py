from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.create_raster_stack_helper import CreateRasterStackHelper
import numpy as np
import unittest
import rasterio
import os


class CreateRasterStackTestCase(unittest.TestCase):

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\', '/')
        self.oh = occurrence_handler(self.root + '/occurrence_handler')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = gis_handler(self.root + '/gis_handler')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False
        self.crs = CreateRasterStackHelper(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):

        self.assertEqual(self.crs.oh, self.oh)
        self.assertEqual(self.crs.gh, self.gh)
        self.assertEqual(self.crs.ch, self.ch)

    def test_create_raster_stack(self):
        self.crs = CreateRasterStackHelper(self.oh, self.gh, self.ch, self.verbose)
        self.assertFalse(os.path.isdir(self.root + '/gis_handler/gis/stack'))
        self.assertFalse(os.path.isfile(self.gh.stack + '/stacked_env_variables.tif'))
        self.crs.create_raster_stack()
        self.assertTrue(os.path.isdir(self.root + '/gis_handler/gis/stack'))
        self.assertTrue(os.path.isfile(self.gh.stack + '/stacked_env_variables.tif'))
        ra = rasterio.open(self.gh.variables[0])
        rb = rasterio.open(self.gh.variables[1])
        rc = rasterio.open(self.gh.variables[2])
        rd = rasterio.open(self.gh.variables[3])
        raster_result = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        np.testing.assert_array_equal(ra.read(1), raster_result.read(1))
        np.testing.assert_array_equal(rb.read(1), raster_result.read(2))
        np.testing.assert_array_equal(rc.read(1), raster_result.read(3))
        np.testing.assert_array_equal(rd.read(1), raster_result.read(4))
        [raster.close() for raster in [ra, rb, rc, rd, raster_result]]
        os.remove(self.gh.stack + '/stacked_env_variables.tif')
        os.rmdir(self.gh.stack)
        os.rmdir(self.gh.gis)


if __name__ == '__main__':
    unittest.main()