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
import io
import json
import os
import posixpath
import shutil
import unittest

import mock

from attributecode import CRITICAL
from attributecode import ERROR
from attributecode import INFO
from attributecode import WARNING
from attributecode import Error
from attributecode import model
from attributecode.util import add_unc, on_windows
from attributecode.util import load_csv
from attributecode.util import to_posix

from testing_utils import extract_test_loc
from testing_utils import get_temp_dir
from testing_utils import get_temp_file
from testing_utils import get_test_loc


def check_csv(expected, result, regen=False, fix_cell_linesep=False):
    """
    Assert that the contents of two CSV files locations `expected` and
    `result` are equal.
    """
    if regen:
        shutil.copyfile(result, expected)
    expected = sorted([sorted(d.items()) for d in load_csv(expected)])
    result = [d.items() for d in load_csv(result)]
    if fix_cell_linesep:
        result = [list(fix_crlf(items)) for items in result]
    result = sorted(sorted(items) for items in result)

    assert expected == result


def fix_crlf(items):
    """
    Hackish... somehow the CVS returned on Windows is sometimes using a backward
    linesep convention:
    instead of LF inside cells and CRLF at EOL,
    they use CRLF everywhere.
    This is fixing this until we find can why
    """
    for key, value in items:
        if isinstance(value, str) and '\r\n' in value:
            value = value.replace('\r\n', '\n')
        yield key, value


def check_json(expected, result):
    """
    Assert that the contents of two JSON files are equal.
    """
    with open(expected) as e:
        expected = json.load(e, object_pairs_hook=OrderedDict)
    with open(result) as r:
        result = json.load(r, object_pairs_hook=OrderedDict)
    assert expected == result


def get_test_content(test_location):
    """
    Read file at test_location and return a unicode string.
    """
    return get_unicode_content(get_test_loc(test_location))


def get_unicode_content(location):
    """
    Read file at location and return a unicode string.
    """
    with io.open(location, encoding='utf-8') as doc:
        return doc.read()


class FieldTest(unittest.TestCase):
    def test_Field_init(self):
        model.Field()

    def test_empty_Field_has_no_content(self):
        field = model.Field()
        assert not field.has_content

    def test_empty_Field_has_default_value(self):
        field = model.Field()
        assert '' == field.value

    def check_validate(self, field_class, value, expected, expected_errors):
        """
        Check field values after validation
        """
        field = field_class(name='s', value=value, present=True)
        # check that validate can be applied multiple times without side effects
        for _ in range(2):
            errors = field.validate()
            assert expected_errors == errors
            assert expected == field.value

class CollectorTest(unittest.TestCase):

    def test_parse_license_expression(self):
        spec_char, returned_lic = model.parse_license_expression('mit or apache-2.0')
        expected_lic = ['mit', 'apache-2.0']
        expected_spec_char = []
        assert expected_lic == returned_lic
        assert expected_spec_char == spec_char

    def test_parse_license_expression_with_special_chara(self):
        spec_char, returned_lic = model.parse_license_expression('mit, apache-2.0')
        expected_lic = []
        expected_spec_char = [',']
        assert expected_lic == returned_lic
        assert expected_spec_char == spec_char

class FetchLicenseTest(unittest.TestCase):

    @mock.patch('attributecode.util.have_network_connection')
    def test_pre_process_and_fetch_license_dict(self, have_network_connection):
        have_network_connection.return_value = False
        licensedb_url = 'https://scancode-licensedb.aboutcode.org/'
        error_msg = (
            'Network problem. Please check your Internet connection. '
            'License fetching is skipped.')
        expected = ({}, [Error(ERROR, error_msg)])
        assert model.pre_process_and_fetch_license_dict([], licensedb_url, False) == expected

        have_network_connection.return_value = True
        expected = ({}, [])
        assert model.pre_process_and_fetch_license_dict([], licensedb_url, False) == expected


