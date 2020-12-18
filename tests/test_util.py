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