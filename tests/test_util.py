#!/usr/bin/env python
# -*- coding: utf8 -*-

# ============================================================================
#  Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ============================================================================

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import string
import unittest

import saneyaml

from testing_utils import extract_test_loc
from testing_utils import get_test_loc
from testing_utils import get_temp_dir
from testing_utils import on_posix
from testing_utils import on_windows

from attributecode import CRITICAL
from attributecode import ERROR
from attributecode import Error
from attributecode import model
from attributecode import util


class TestResourcePaths(unittest.TestCase):

    def test_to_posix_from_win(self):
        test = r'c:\this\that'
        expected = 'c:/this/that'
        result = util.to_posix(test)
        assert expected == result

    def test_to_posix_from_posix(self):
        test = r'/this/that'
        expected = '/this/that'
        result = util.to_posix(test)
        assert expected == result

    def test_to_posix_from_mixed(self):
        test = r'/this/that\this'
        expected = '/this/that/this'
        result = util.to_posix(test)
        assert expected == result

class TestCsv(unittest.TestCase):

    def test_load_csv_without_mapping(self):
        test_file = get_test_loc('test_util/csv/about.csv')
        expected = [OrderedDict([
            ('about_file', 'about.ABOUT'),
            ('about_resource', '.'),
            ('name', 'ABOUT tool'),
            ('version', '0.8.1')])
        ]
        result = util.load_csv(test_file)
        assert expected == result

    def test_load_csv_load_rows(self):
        test_file = get_test_loc('test_util/csv/about.csv')
        expected = [OrderedDict([
            ('about_file', 'about.ABOUT'),
            ('about_resource', '.'),
            ('name', 'ABOUT tool'),
            ('version', '0.8.1')])
        ]
        result = util.load_csv(test_file)
        assert expected == result

    def test_load_csv_does_convert_column_names_to_lowercase(self):
        test_file = get_test_loc('test_util/csv/about_key_with_upper_case.csv')
        expected = [OrderedDict(
                    [('about_file', 'about.ABOUT'),
                     ('about_resource', '.'),
                     ('name', 'ABOUT tool'),
                     ('version', '0.8.1')])
                    ]
        result = util.load_csv(test_file)
        assert expected == result

    def test_load_csv_microsoft_utf_8(self):
        test_file = get_test_loc('test_util/csv/test_ms_utf8.csv')
        expected = [OrderedDict([(u'about_resource', u'/myFile'), (u'name', u'myName')])]
        result = util.load_csv(test_file)
        assert expected == result

    def test_load_csv_utf_8(self):
        test_file = get_test_loc('test_util/csv/test_utf8.csv')
        expected = [OrderedDict([(u'about_resource', u'/myFile'), (u'name', u'\u540d')])]
        result = util.load_csv(test_file)
        assert expected == result

class TestJson(unittest.TestCase):

    def test_load_json(self):
        test_file = get_test_loc('test_util/json/expected.json')
        expected = [{'about_file_path': '/load/this.ABOUT',
                     'about_resource': '.', 'name': 'AboutCode',
                     'version': '0.11.0'}]
        result = util.load_json(test_file)
        assert expected == result

    def test_load_non_list_json2(self):
        test_file = get_test_loc('test_util/json/not_a_list.json')
        expected = [{'about_file_path': '/load/this.ABOUT',
                     'about_resource': '.', 'name': 'AboutCode',
                     'version': '0.11.0'}]
        result = util.load_json(test_file)
        assert expected == result

    def test_load_json_from_scancode(self):
        test_file = get_test_loc('test_util/json/scancode_info.json')
        expected = [dict(OrderedDict([
            ('type', 'file'),
            ('name', 'Api.java'),
            ('path', 'Api.java'),
            ('base_name', 'Api'),
            ('extension', '.java'),
            ('size', 5074),
            ('date', '2017-07-15'),
            ('sha1', 'c3a48ec7e684a35417241dd59507ec61702c508c'),
            ('md5', '326fb262bbb9c2ce32179f0450e24601'),
            ('mime_type', 'text/plain'),
            ('file_type', 'ASCII text'),
            ('programming_language', 'Java'),
            ('is_binary', False),
            ('is_text', True),
            ('is_archive', False),
            ('is_media', False),
            ('is_source', True),
            ('is_script', False),
            ('files_count', 0),
            ('dirs_count', 0),
            ('size_count', 0),
            ('scan_errors', []),
        ]))]
        result = util.load_scancode_json(test_file)
        assert expected == result

class TestMiscUtils(unittest.TestCase):

    def test_unique_does_deduplicate_and_keep_ordering(self):
        items = ['a', 'b', 'd', 'b', 'c', 'a']
        expected = ['a', 'b', 'd', 'c']
        results = util.unique(items)
        assert expected == results

    def test_check_duplicated_columns(self):
        test_file = get_test_loc('test_util/dup_keys.csv')
        expected = [Error(ERROR, 'Duplicated column name(s): copyright with copyright\nPlease correct the input and re-run.')]
        result = util.check_duplicated_columns(test_file)
        assert expected == result

    def test_check_duplicated_columns_handles_lower_upper_case(self):
        test_file = get_test_loc('test_util/dup_keys_with_diff_case.csv')
        expected = [Error(ERROR, 'Duplicated column name(s): copyright with Copyright\nPlease correct the input and re-run.')]
        result = util.check_duplicated_columns(test_file)
        assert expected == result

    def test_check_newline_in_file_field(self):
        test_dict1 = {'about_resource': '/test/test.c', 'name': 'test.c', 'notice_file': 'NOTICE\nNOTICE2'}
        test_dict2 = {'about_resource': '/test/test.c', 'name': 'test.c', 'notice_file': 'NOTICE, NOTICE2'}
        expected = [
            Error(CRITICAL,
                  "New line character detected in 'notice_file' for '/test/test.c' which is not supported."
                  "\nPlease use ',' to declare multiple files.")]
        result1 = util.check_newline_in_file_field(test_dict1)
        result2 = util.check_newline_in_file_field(test_dict2)
        assert result1 == expected
        assert result2 == []

    def test_load_inventory_simple_csv(self):
        location = get_test_loc('test_util/load/simple_sample.csv')
        base_dir = get_temp_dir()
        errors, abouts = util.load_inventory(location)
        assert errors == []

        assert abouts[0].name.value == 'cryptohash-sha256'
        assert abouts[1].name.value == 'some_component'
        
        assert abouts[0].version.value == 'v 0.11.100.1'
        assert abouts[1].version.value == 'v 0.0.1'

        assert abouts[0].license_expression.value == 'bsd-new and mit'
        assert abouts[1].license_expression.value == 'mit'

    def test_load_inventory_simple_xlsx(self):
        location = get_test_loc('test_util/load/simple_sample.xlsx')
        base_dir = get_temp_dir()
        errors, abouts = util.load_inventory(location)
        assert errors == []

        assert abouts[0].name.value == 'cryptohash-sha256'
        assert abouts[1].name.value == 'some_component'
        
        assert abouts[0].version.value == 'v 0.11.100.1'
        assert abouts[1].version.value == 'v 0.0.1'

        assert abouts[0].license_expression.value == 'bsd-new and mit'
        assert abouts[1].license_expression.value == 'mit'


    def test_load_scancode_json(self):
        location = get_test_loc('test_util/load/clean-text-0.3.0-lceupi.json')
        base_dir = get_temp_dir()
        configuration = None
        inventory = util.load_scancode_json(location, configuration)

        expected = {'path': 'clean-text-0.3.0', 'type': 'directory',
                    'name': 'clean-text-0.3.0', 'base_name': 'clean-text-0.3.0',
                    'extension': '', 'size': 0, 'date': None, 'sha1': None,
                    'md5': None, 'sha256': None, 'mime_type': None, 'file_type': None,
                    'programming_language': None, 'is_binary': False, 'is_text': False,
                    'is_archive': False, 'is_media': False, 'is_source': False,
                    'is_script': False, 'licenses': [], 'license_expressions': [],
                    'percentage_of_license_text': 0, 'copyrights': [], 'holders': [],
                    'authors': [], 'packages': [], 'emails': [], 'urls': [], 'files_count': 9,
                    'dirs_count': 1, 'size_count': 32826, 'scan_errors': []}

        # We will only check the first element in the inventory list 
        assert inventory[0] == expected

    def test_load_scancode_json_with_conf(self):
        location = get_test_loc('test_util/load/clean-text-0.3.0-lceupi.json')
        base_dir = get_temp_dir()
        configuration = get_test_loc('test_util/load/key.config')
        inventory = util.load_scancode_json(location, configuration)

        expected = {'resource': 'clean-text-0.3.0', 'type': 'directory',
                    'name': 'clean-text-0.3.0', 'base_name': 'clean-text-0.3.0',
                    'extension': '', 'size': 0, 'date': None, 'sha1': None,
                    'md5': None, 'sha256': None, 'mime_type': None, 'file_type': None,
                    'programming_language': None, 'is_binary': False, 'is_text': False,
                    'is_archive': False, 'is_media': False, 'is_source': False,
                    'is_script': False, 'licenses': [], 'license_expressions': [],
                    'percentage_of_license_text': 0, 'copyrights': [], 'holders': [],
                    'authors': [], 'packages': [], 'emails': [], 'urls': [], 'files_count': 9,
                    'dirs_count': 1, 'size_count': 32826, 'scan_errors': []}

        # We will only check the first element in the inventory list 
        assert inventory[0] == expected

    def test_load_csv_with_conf(self):
        location = get_test_loc('test_util/load/simple_sample.csv')
        base_dir = get_temp_dir()
        configuration = get_test_loc('test_util/load/key.config')
        inventory = util.load_csv(location, configuration)

        expected = [OrderedDict([('name', 'cryptohash-sha256'), ('version', 'v 0.11.100.1'),
                                 ('license_expression', 'bsd-new and mit'),
                                 ('resource', '/project/cryptohash-sha256')]),
                    OrderedDict([('name', 'some_component'), ('version', 'v 0.0.1'),
                                ('license_expression', 'mit'),
                                ('resource', '/project/some_component')])]
        assert inventory == expected

    def test_load_xlsx_with_conf(self):
        location = get_test_loc('test_util/load/simple_sample.xlsx')
        base_dir = get_temp_dir()
        configuration = get_test_loc('test_util/load/key.config')
        dup_cols_err, inventory = util.load_excel(location, configuration)

        expected = [OrderedDict([('name', 'cryptohash-sha256'), ('version', 'v 0.11.100.1'),
                                 ('license_expression', 'bsd-new and mit'),
                                 ('resource', '/project/cryptohash-sha256')]),
                    OrderedDict([('name', 'some_component'), ('version', 'v 0.0.1'),
                                ('license_expression', 'mit'),
                                ('resource', '/project/some_component')])]
        assert inventory == expected
        assert dup_cols_err == []

    def test_convert_object_to_dict(self):
        location = get_test_loc('test_util/load/simple_sample.csv')
        base_dir = get_temp_dir()
        errors, abouts = util.load_inventory(location)
        assert errors == []

        expected = {'name': 'cryptohash-sha256', 'version': 'v 0.11.100.1', 'download_url': '',
                    'homepage_url': '', 'package_url': '', 'notes': '', 'license_expression': 'bsd-new and mit',
                    'license_key': ['bsd-new', 'mit'], 'license_name': '', 'license_file': '', 'license_url': '',
                    'copyright': '', 'notice_file': '', 'path': '/project/cryptohash-sha256'}
        results = util.convert_object_to_dict(abouts[0])
        assert results == expected

    def test_number_of_component_generated_from_default_template(self):
        location = get_test_loc(
            'test_attrib/default_template/expect.html')
        num_component = util.number_of_component_generated_from_default_template(location)
        assert num_component == 2