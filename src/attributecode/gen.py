#!/usr/bin/env python
# -*- coding: utf8 -*-

# ============================================================================
#  Copyright (c) 2013-2020 nexB Inc. http://www.nexb.com/ - All rights reserved.
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

import codecs
import yaml
from collections import OrderedDict

# FIXME: why posipath???
from posixpath import basename
from posixpath import dirname
from posixpath import exists
from posixpath import join
from posixpath import normpath

from attributecode import ERROR
from attributecode import CRITICAL
from attributecode import INFO
from attributecode import Error
from attributecode import model
from attributecode import util
from attributecode.util import add_unc
from attributecode.util import csv
from attributecode.util import file_fields
from attributecode.util import invalid_chars
from attributecode.util import to_posix
from attributecode.util import UNC_PREFIX_POSIX
from attributecode.util import unique


def check_duplicated_columns(location):
    """
    Return a list of errors for duplicated column names in a CSV file
    at location.
    """
    location = add_unc(location)
    with codecs.open(location, 'rb', encoding='utf-8-sig', errors='replace') as csvfile:
        reader = csv.reader(csvfile)
        columns = next(reader)
        columns = [col for col in columns]

    seen = set()
    dupes = OrderedDict()
    for col in columns:
        c = col.lower()
        if c in seen:
            if c in dupes:
                dupes[c].append(col)
            else:
                dupes[c] = [col]
        seen.add(c.lower())

    errors = []
    if dupes:
        dup_msg = []
        for name, names in dupes.items():
            names = u', '.join(names)
            msg = '%(name)s with %(names)s' % locals()
            dup_msg.append(msg)
        dup_msg = u', '.join(dup_msg)
        msg = ('Duplicated column name(s): %(dup_msg)s\n' % locals() +
               'Please correct the input and re-run.')
        errors.append(Error(ERROR, msg))
    return unique(errors)

def check_newline_in_file_field(component):
    """
    Return a list of errors for newline characters detected in *_file fields.
    """
    errors = []
    for k in component.keys():
        if k in file_fields:
            try:
                if '\n' in component[k]:
                    msg = ("New line character detected in '%s' for '%s' which is not supported."
                            "\nPlease use ',' to declare multiple files.") % (k, component['about_resource'])
                    errors.append(Error(CRITICAL, msg))
            except:
                pass
    return errors

def check_about_resource_filename(arp):
    """
    Return error for invalid/non-support about_resource's filename or
    empty string if no error is found. 
    """
    if invalid_chars(arp):
        msg = ("Invalid characters present in 'about_resource' "
                   "field: " + arp)
        return (Error(CRITICAL, msg))
    return ''

def load_inventory(location, configuration=None, scancode=False, reference_dir=None):
    """
    Load the inventory file at `location` 

    Optionally use `reference_dir` as the directory location of extra reference
    license and notice files to reuse.
    """
    errors = []
    abouts = []
    if scancode:
        inventory = util.load_scancode_json(location, configuration)
    else:
        if location.endswith('.csv'):
            # FIXME: this should not be done here.
            dup_cols_err = check_duplicated_columns(location)
            if dup_cols_err:
                errors.extend(dup_cols_err)
                return errors, abouts
            inventory = util.load_csv(location, configuration)
        elif location.endswith('.xlsx'):
            dup_cols_err, inventory = util.load_excel(location, configuration)
            if dup_cols_err:
                errors.extend(dup_cols_err)
                return errors, abouts
        else:
            inventory = util.load_json(location)

    errors = []
    for component in inventory:
        newline_in_file_err = check_newline_in_file_field(component)
        for err in newline_in_file_err:
            errors.append(err)

    if errors:
        return errors, abouts

    for component in inventory:
        about = model.About(component)

        ld_errors = about.load_dict(
            component,
            scancode=scancode,
            running_inventory=False,
            reference_dir=reference_dir,
        )

        for e in ld_errors:
            if not e in errors:
                errors.extend(ld_errors)

        abouts.append(about)

    return unique(errors), abouts
