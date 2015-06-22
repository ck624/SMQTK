__author__ = 'purg'

import mock
import nose.tools as ntools
import os
import unittest

from smqtk.data_rep.data_element_impl.file_element import DataFileElement
from smqtk.tests import TEST_DATA_DIR

import smqtk_config


class TestDataFileElement (unittest.TestCase):

    def test_init_filepath_abs(self):
        fp = '/foo.txt'
        d = DataFileElement(fp)
        ntools.assert_equal(d._filepath, fp)

    def test_init_relFilepath(self):
        fp = 'foo.txt'
        d = DataFileElement(fp)
        ntools.assert_equal(d._filepath,
                            os.path.join(smqtk_config.WORK_DIR, fp))

    def test_content_type(self):
        d = DataFileElement('foo.txt')
        ntools.assert_equal(d.content_type(), 'text/plain')

    @mock.patch('smqtk.data_rep.data_element_abstract.DataElement.write_temp')
    def test_writeTempOverride(self, mock_DataElement_wt):
        # no manual directory, should return the base filepath
        expected_filepath = '/path/to/file.txt'
        d = DataFileElement(expected_filepath)
        fp = d.write_temp()

        ntools.assert_false(mock_DataElement_wt.called)
        ntools.assert_equal(expected_filepath, fp)

    @mock.patch('smqtk.data_rep.data_element_abstract.DataElement.write_temp')
    def test_writeTempOverride_sameDir(self, mock_DataElement_wt):
        expected_filepath = '/path/to/file.txt'
        target_dir = '/path/to'

        d = DataFileElement(expected_filepath)
        fp = d.write_temp(temp_dir=target_dir)

        ntools.assert_false(mock_DataElement_wt.called)
        ntools.assert_equal(fp, expected_filepath)

    @mock.patch('smqtk.data_rep.data_element_abstract.safe_create_dir')
    @mock.patch('fcntl.fcntl')  # global
    @mock.patch('os.close')  # global
    @mock.patch('os.open')  # global
    @mock.patch('__builtin__.open')
    def test_writeTempOverride_diffDir(self, mock_open, mock_os_open,
                                       mock_os_close, mock_fcntl, mock_scd):
        source_filepath = '/path/to/file.png'
        target_dir = '/some/other/dir'

        d = DataFileElement(source_filepath)
        fp = d.write_temp(temp_dir=target_dir)

        ntools.assert_not_equal(fp, source_filepath)
        ntools.assert_equal(os.path.dirname(fp), target_dir)

        # subsequent call to write temp should not invoke creation of a new file
        fp2 = d.write_temp()
        ntools.assert_equal(fp2, source_filepath)

        # request in same dir should return same path as first request with that
        # directory
        fp3 = d.write_temp(target_dir)
        ntools.assert_equal(fp, fp3)

        # request different target dir
        target2 = '/even/different/path'
        fp4 = d.write_temp(target2)
        ntools.assert_equal(os.path.dirname(fp4), target2)
        ntools.assert_not_equal(fp, fp4)
        ntools.assert_equal(len(d._temp_filepath_stack), 2)

    def test_cleanTemp(self):
        # a write temp and clean temp should not affect original file
        source_file = os.path.join(TEST_DATA_DIR, 'test_file.dat')
        ntools.assert_true(os.path.isfile(source_file))
        d = DataFileElement(source_file)
        d.write_temp()
        ntools.assert_equal(len(d._temp_filepath_stack), 0)
        d.clean_temp()
        ntools.assert_true(os.path.isfile(source_file))