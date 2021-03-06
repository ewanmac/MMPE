'''
Created on 12/09/2013

@author: mmpe
'''

from __future__ import division, print_function, absolute_import, \
    unicode_literals
import h5py
try: range = xrange; xrange = None
except NameError: pass
try: str = unicode; unicode = None
except NameError: pass
import numpy as np
import gtsdf
import h5py

import unittest

class Test(unittest.TestCase):
    f = "temp/"
    def test_minimum_requirements (self):
        fn = self.f + "minimum.hdf5"
        f = h5py.File(fn, "w")
        #no type
        self.assertRaises(ValueError, gtsdf.load, fn)
        f.attrs["type"] = "General time series data format"

        #no no_blocks
        self.assertRaises(ValueError, gtsdf.load, fn)
        f.attrs["no_blocks"] = 0

        #no block0000
        self.assertRaises(ValueError, gtsdf.load, fn)
        b = f.create_group("block0000")

        #no data
        self.assertRaises(ValueError, gtsdf.load, fn)
        b.create_dataset("data", data=np.empty((0, 0)))
        gtsdf.load(fn)

    def test_save_no_hdf5_ext(self):
        fn = self.f + "no_hdf5_ext"
        gtsdf.save(fn, np.arange(12).reshape(4, 3))
        _, _, info = gtsdf.load(fn + ".hdf5")
        self.assertEqual(info['name'], 'no_hdf5_ext')

    def test_load_filename(self):
        fn = self.f + "filename.hdf5"
        gtsdf.save(fn, np.arange(12).reshape(4, 3))
        _, _, info = gtsdf.load(fn)
        self.assertEqual(info['name'], 'filename')


    def test_load_fileobject(self):
        fn = self.f + "fileobject.hdf5"
        gtsdf.save(fn, np.arange(12).reshape(4, 3))
        _, _, info = gtsdf.load(fn)
        self.assertEqual(info['name'], 'fileobject')

    def test_save_wrong_no_attr_info(self):
        fn = self.f + "wrong_no_attr_info.hdf5"
        self.assertRaises(AssertionError, gtsdf.save, fn, np.arange(12).reshape(4, 3), attribute_names=['Att1'])
        self.assertRaises(AssertionError, gtsdf.save, fn, np.arange(12).reshape(4, 3), attribute_units=['s'])
        self.assertRaises(AssertionError, gtsdf.save, fn, np.arange(12).reshape(4, 3), attribute_descriptions=['desc'])

    def test_info(self):
        fn = self.f + "info.hdf5"
        gtsdf.save(fn, np.arange(12).reshape(6, 2),
                   name='datasetname',
                   description='datasetdescription',
                   attribute_names=['att1', 'att2'],
                   attribute_units=['s', 'm/s'],
                   attribute_descriptions=['d1', 'd2'])
        _, _, info = gtsdf.load(fn)
        self.assertEqual(info['name'], "datasetname")
        self.assertEqual(info['type'], "General time series data format")
        self.assertEqual(info['description'], "datasetdescription")
        self.assertEqual(list(info['attribute_names']), ['att1', 'att2'])
        self.assertEqual(list(info['attribute_units']), ['s', 'm/s'])
        self.assertEqual(list(info['attribute_descriptions']), ['d1', 'd2'])

    def test_no_time(self):
        fn = self.f + 'time.hdf5'
        gtsdf.save(fn, np.arange(12).reshape(6, 2))
        time, _, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(time, np.arange(6))

    def test_int_time(self):
        fn = self.f + 'time.hdf5'
        gtsdf.save(fn, np.arange(12).reshape(6, 2), time=range(4, 10))
        time, _, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(time, range(4, 10))


    def test_time_offset(self):
        fn = self.f + 'time.hdf5'
        gtsdf.save(fn, np.arange(12).reshape(6, 2), time=range(6), time_start=4)
        time, _, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(time, range(4, 10))


    def test_time_gain_offset(self):
        fn = self.f + 'time.hdf5'
        gtsdf.save(fn, np.arange(12).reshape(6, 2), time=range(6), time_step=1 / 4, time_start=4)
        time, _, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(time, np.arange(4, 5.5, .25))

    def test_float_time(self):
        fn = self.f + 'time.hdf5'
        gtsdf.save(fn, np.arange(12).reshape(6, 2), time=np.arange(4, 5.5, .25))
        time, _, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(time, np.arange(4, 5.5, .25))

    def test_data(self):
        fn = self.f + 'time.hdf5'
        d = np.arange(12).reshape(6, 2)
        gtsdf.save(fn, d)
        f = h5py.File(fn)
        self.assertEqual(f['block0000']['data'].dtype, np.uint16)
        f.close()
        _, data, _ = gtsdf.load(fn)
        np.testing.assert_array_almost_equal(data, np.arange(12).reshape(6, 2), 4)

    def test_data_float(self):
        fn = self.f + 'time.hdf5'
        d = np.arange(12).reshape(6, 2)
        gtsdf.save(fn, d, dtype=np.float32)
        f = h5py.File(fn)
        self.assertEqual(f['block0000']['data'].dtype, np.float32)
        f.close()
        _, data, _ = gtsdf.load(fn)
        np.testing.assert_array_equal(data, np.arange(12).reshape(6, 2))


    def test_all(self):
        fn = self.f + "all.hdf5"
        gtsdf.save(fn, np.arange(12).reshape(6, 2),
                   name='datasetname',
                   time=range(6), time_step=1 / 4, time_start=4,
                   description='datasetdescription',
                   attribute_names=['att1', 'att2'],
                   attribute_units=['s', 'm/s'],
                   attribute_descriptions=['d1', 'd2'])
        time, data, info = gtsdf.load(fn)
        self.assertEqual(info['name'], "datasetname")
        self.assertEqual(info['type'], "General time series data format")
        self.assertEqual(info['description'], "datasetdescription")
        self.assertEqual(list(info['attribute_names']), ['att1', 'att2'])
        self.assertEqual(list(info['attribute_units']), ['s', 'm/s'])
        self.assertEqual(list(info['attribute_descriptions']), ['d1', 'd2'])
        np.testing.assert_array_equal(time, np.arange(4, 5.5, .25))
        np.testing.assert_array_almost_equal(data, np.arange(12).reshape(6, 2), 4)

    def test_append(self):
        fn = self.f + 'append.hdf5'
        d = np.arange(12, dtype=np.float32).reshape(6, 2)
        d[2, 0] = np.nan
        gtsdf.save(fn, d)
        _, data, _ = gtsdf.load(fn)
        np.testing.assert_array_almost_equal(data, d, 4)
        gtsdf.append_block(fn, d)
        _, data, _ = gtsdf.load(fn)
        self.assertEqual(data.shape, (12, 2))
        np.testing.assert_array_almost_equal(data, np.append(d, d, 0), 4)


    def test_nan_float(self):
        fn = self.f + 'nan.hdf5'
        d = np.arange(12, dtype=np.float32).reshape(6, 2)
        d[2, 0] = np.nan
        gtsdf.save(fn, d)
        _, data, _ = gtsdf.load(fn)
        np.testing.assert_array_almost_equal(data, d, 4)

    def test_nan_float(self):
        fn = self.f + 'nan.hdf5'
        d = np.arange(12, dtype=np.float32).reshape(6, 2)
        d[2, 0] = np.nan
        gtsdf.save(fn, d, dtype=np.float32)
        _, data, _ = gtsdf.load(fn)
        np.testing.assert_array_almost_equal(data, d, 4)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
