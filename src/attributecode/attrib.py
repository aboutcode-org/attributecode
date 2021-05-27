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

import collections
import datetime
import io
import os

import jinja2

from attributecode import __version__
from attributecode import CRITICAL
from attributecode import ERROR
from attributecode import Error
from attributecode.util import add_unc
from attributecode.util import convert_object_to_dict
from attributecode.attrib_util import multi_sort


DEFAULT_TEMPLATE_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../../templates', 'default_html.template')

DEFAULT_LICENSE_SCORE = 100

def generate(abouts, license_dict, min_license_score, template=None, variables=None):
    """
    Generate an attribution text from an `abouts` list of About objects, a
    `template` template text and a `variables` optional dict of extra
    variables.

    Return a tuple of (error, attribution text) where error is an Error object
    or None and attribution text is the generated text or None.
    """
    rendered = None
    error = None
    template_error = check_template(template)
    if template_error:
        lineno, message = template_error
        error = Error(
            CRITICAL,
            'Template validation error at line: {lineno}: "{message}"'.format(**locals())
        )
        return error, None

    template = jinja2.Template(template)

    # Get the current UTC time
    utcnow = datetime.datetime.utcnow()

    try:
        # Convert the field object to dictionary as it's needed for the
        # groupby in JINJA2 template
        about_dict_list = []
        for about in abouts:
            about_dict = convert_object_to_dict(about)
            about_dict_list.append(about_dict)
        rendered = template.render(
            abouts=about_dict_list, license_dict=license_dict,
            min_license_score=min_license_score,
            utcnow=utcnow,
            tkversion=__version__,
            variables=variables
        )
    except Exception as e:
        lineno = getattr(e, 'lineno', '') or ''
        if lineno:
            lineno = ' at line: {}'.format(lineno)
        err = getattr(e, 'message', '') or ''
        error = Error(
            CRITICAL,
            'Template processing error {lineno}: {err}'.format(**locals()),
        )
        error = Error(
            CRITICAL,
            'Template processing error:' + str(e),
        )

    return error, rendered

def check_template(template_string):
    """
    Check the syntax of a template. Return an error tuple (line number,
    message) if the template is invalid or None if it is valid.
    """
    try:
        jinja2.filters.FILTERS['multi_sort'] = multi_sort
        jinja2.Template(template_string)
    except (jinja2.TemplateSyntaxError, jinja2.TemplateAssertionError) as e:
        return e.lineno, e.message


def generate_from_file(abouts, license_dict, min_license_score, template_loc=DEFAULT_TEMPLATE_FILE, variables=None):
    """
    Generate an attribution text from an `abouts` list of About objects, a
    `template_loc` template file location and a `variables` optional
    dict of extra variables.

    Return a tuple of (error, attribution text) where error is an Error object
    or None and attribution text is the generated text or None.
    """
    template_loc = add_unc(template_loc)
    with io.open(template_loc, encoding='utf-8') as tplf:
        tpls = tplf.read()
    return generate(abouts, license_dict, min_license_score, template=tpls, variables=variables)


def generate_and_save(abouts, license_dict, output_location, min_license_score=0, template_loc=None, variables=None):
    """
    Generate an attribution text from an `abouts` list of About objects, a
    `template_loc` template file location and a `variables` optional
    dict of extra variables. Save the generated attribution text in the
    `output_location` file.
    Return a list of Error objects if any.
    """
    errors = []

    rendering_error, rendered = generate_from_file(
        abouts,
        license_dict,
        min_license_score=min_license_score,
        template_loc=template_loc,
        variables=variables
    )

    if rendering_error:
        errors.append(rendering_error)

    if rendered:
        output_location = add_unc(output_location)
        with io.open(output_location, 'w', encoding='utf-8') as of:
            of.write(rendered)

    return errors, rendered
