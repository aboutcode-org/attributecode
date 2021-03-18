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

"""
AboutCode toolkit is a tool to process ABOUT files. ABOUT files are
small text files that document the provenance (aka. the origin and
license) of software components as well as the essential obligation
such as attribution/credits and source code redistribution. See the
ABOUT spec at http://dejacode.org.

AboutCode toolkit reads and validates ABOUT files and collect software
components inventories.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import json

from itertools import zip_longest  # NOQA
from urllib.parse import urljoin, urlparse  # NOQA
from urllib.request import urlopen, Request  # NOQA
from urllib.error import HTTPError  # NOQA

import urllib.request

from license_expression import Licensing

from attributecode import __version__
from attributecode import CRITICAL
from attributecode import ERROR
from attributecode import INFO
from attributecode import WARNING
from attributecode import Error
from attributecode import util



class Field(object):
    """
    An ABOUT file field. The initial value is a string. Subclasses can and
    will alter the value type as needed.
    """

    def __init__(self, name=None, value=None):
        # normalized names are lowercased per specification
        self.name = name
        # save this and do not mutate it afterwards
        if isinstance(value, str):
            self.original_value = value
        elif value:
            self.original_value = repr(value)
        else:
            self.original_value = value

        # can become a string, list or OrderedDict() after validation
        self.value = value or self.default_value()
        self.errors = []

    def default_value(self):
        return ''

    @property
    def has_content(self):
        return self.original_value

    def __repr__(self):
        name = self.name
        value = self.value
        r = ('Field(name=%(name)r, value=%(value)r)')
        return r % locals()

def validate_field_name(name):
    if not util.is_valid_name(name):
        msg = ('Field name: %(name)r is ignored as it contains illegal name characters.')
        return Error(INFO, msg % locals())

class About(object):
    """
    Create an ABOUT object
    """
    def set_standard_fields(self):
        """
        Create fields in an ordered dict to keep a standard ordering. We
        could use a metaclass to track ordering django-like but this approach
        is simpler.
        """
        self.fields = OrderedDict([
            ('name', Field()),
            ('version', Field()),

            ('download_url', Field()),
            ('homepage_url', Field()),
            ('package_url', Field()),
            ('notes', Field()),

            ('license_expression', Field()),
            ('license_key', Field()),
            ('license_name', Field()),
            ('license_file', Field()),
            ('license_url', Field()),
            ('copyright', Field()),
            ('notice_file', Field()),
        ])

        for name, field in self.fields.items():
            # we could have a hack to get the actual field name
            # but setting an attribute is explicit and cleaner
            field.name = name
            setattr(self, name, field)

    def __init__(self, location=None):
        """
        Create an instance.
        If strict is True, raise an Exception on errors. Otherwise the errors
        attribute contains the errors.
        """
        self.set_standard_fields()
        self.custom_fields = OrderedDict()
        self.errors = []

    def __repr__(self):
        return repr(self.all_fields())

    def all_fields(self):
        """
        Return the list of all Field objects.
        """
        return list(self.fields.values()) + list(self.custom_fields.values())

    def hydrate(self, fields):
        """
        Process an iterable of field (name, value) tuples. Update or create
        Fields attributes and the fields and custom fields dictionaries.
        Return a list of errors.
        """
        errors = []
        seen_fields = OrderedDict()
        try:
            for name, value in fields:
                orig_name = name
                name = name.lower()

                # A field that has been already processed ... and has a value
                previous_value = seen_fields.get(name)
                if previous_value:
                    if value != previous_value:
                        msg = (u'Field %(orig_name)s is a duplicate. '
                               u'Original value: "%(previous_value)s" '
                               u'replaced with: "%(value)s"')
                        errors.append(Error(WARNING, msg % locals()))
                        continue
                seen_fields[name] = value

                # A standard field
                standard_field = self.fields.get(name)
                if standard_field:
                    standard_field.original_value = value
                    standard_field.value = value
                    continue

                # A custom field
                illegal_name_error = validate_field_name(name)
                if illegal_name_error:
                    errors.append(illegal_name_error)
                    continue

                custom_field = self.custom_fields.get(name)
                if custom_field:
                    # An known custom field
                    custom_field.original_value = value
                    custom_field.value = value
                else:
                    # A new, unknown custom field
                    # custom fields are always handled as StringFields
                    custom_field = Field(name=name, value=value)
                    self.custom_fields[name] = custom_field
                    try:
                        if name in dir(self):
                            raise Exception('Illegal field: %(name)r: %(value)r.' % locals())
                        setattr(self, name, custom_field)
                    except:
                        msg = 'Internal error with custom field: %(name)r: %(value)r.'
                        errors.append(Error(CRITICAL, msg % locals()))
        except AttributeError:
            msg = 'One of the columns does not have column name.'
            errors.append(Error(CRITICAL, msg % locals()))

        return errors

    def process(self, fields, reference_dir=None):
        """
        Validate and set as attributes on this About object a sequence of
        `fields` name/value tuples. Return a list of errors.
        """
        self.reference_dir = reference_dir
        errors = self.hydrate(fields)
        return errors

    def load_dict(self, fields_dict, scancode =False, reference_dir=None,):
        """
        Load this About object from a `fields_dict` name/value dict.
        Return a list of errors.
        """
        errors = []
        # do not keep empty
        fields = list(fields_dict.items())

        if scancode:
            for key, value in fields:
                if not value:
                    # never return empty or absent fields
                    continue
                if key == u'license_expressions':
                    # dedup the license_key in the license_expression
                    self.license_key.value = list(set(value))
        else:
            for key, value in fields:
                if not value:
                    # never return empty or absent fields
                    continue
                if key == u'license_expression':
                    special_char_in_expression, lic_list = parse_license_expression(value)
                    self.license_key.value = lic_list
                    if special_char_in_expression:
                        msg = ('License expression cannot contains the following special characters: ' +
                               special_char_in_expression)
                        errors.append(Error(CRITICAL, msg))

        process_errors = self.process(
            fields=fields,
            reference_dir=reference_dir,
        )
        if process_errors:
            errors.extend(process_errors)
        self.errors = errors
        return errors

def pre_process_and_fetch_license_dict(abouts, url, scancode, reference=None):
    """
    Parse the license expression from the about object and return a dictionary
    list with license key as a key and its corresponding license information as
    a value. Note that this value is also a dictionary.
    """
    license_data_dict = {}
    captured_license = []
    errors = []
    if util.have_network_connection():
        try:
            request = Request(url)
            urlopen(request)
        except:
            msg = u"URL not reachable. Invalid License DB url."
            errors.append(Error(ERROR, msg))
    else:
        msg = u'Network problem. Please check your Internet connection. License fetching is skipped.'
        errors.append(Error(ERROR, msg))

    if errors:
        return license_data_dict, errors

    for about in abouts:
        lic_list = []
        if scancode:
            if about.license_expressions.value:
                lic_list = list(set(about.license_expressions.value))
        else:
            if not about.license_expression.value:
                continue
            else:
                special_char_in_expression, lic_list = parse_license_expression(about.license_expression.value)
                if special_char_in_expression:
                    msg = (u"The following character(s) cannot be in the license_expression: " +
                           str(special_char_in_expression))
                    errors.append(Error(ERROR, msg))
                    continue
        for lic_key in lic_list:
            if not lic_key in captured_license:
                license_url = url + lic_key + '.json'
                license_text_url = ''
                try:
                    json_url = urlopen(license_url)
                    data = json.loads(json_url.read())
                    license_text_url = url + data['key'] + '.LICENSE'
                    license_dict = data
                    license_text = urllib.request.urlopen(license_text_url).read().decode('utf-8')
                    license_dict['license_text'] = license_text
                    captured_license.append(lic_key)
                    license_data_dict[lic_key] = license_dict
                except urllib.error.HTTPError:
                    # license_expression key not found in LicenseDB
                    # but license_file field present
                    if about.license_file.value:
                        file_name = about.license_file.value
                        error, text = util.get_file_text(file_name, reference)
                        if not error:
                            license_dict = {}
                            license_dict['key'] = lic_key
                            license_dict['license_text'] = text
                            license_data_dict[lic_key] = license_dict
                        else:
                            errors.append(error)
                    else:
                        msg = ("One of the URLs (or both) is not reachable: " + '\n' +
                            license_url + '\n' + license_text_url)
                        errors.append(Error(ERROR, msg)) 
                except:
                    msg = "License key, " + lic_key + ", not recognize."
                    errors.append(Error(ERROR, msg))

    return license_data_dict, errors

def parse_license_expression(lic_expression):
    licensing = Licensing()
    lic_list = []
    special_char = detect_special_char(lic_expression)
    if not special_char:
        # Parse the license expression and save it into a list
        lic_list = licensing.license_keys(lic_expression)
    return special_char, lic_list

def detect_special_char(expression):
    not_support_char = [
        '!', '@', '#', '$', '%', '^', '&', '*', '=', '{', '}',
        '|', '[', ']', '\\', ':', ';', '<', '>', '?', ',', '/']
    special_character = []
    for char in not_support_char:
        if char in expression:
            special_character.append(char)
    return special_character

