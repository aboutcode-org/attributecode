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

import io
import os
import unittest

from testing_utils import get_test_loc
from testing_utils import get_temp_file

from attributecode import attrib
from attributecode import model
from attributecode import util

class TemplateTest(unittest.TestCase):

    def test_check_template_simple_valid_returns_None(self):
        expected = None
        assert expected == attrib.check_template('template_string')

    def test_check_template_complex_valid_returns_None(self):
        template = '''
        {% for about in abouts -%}
            {{ about.name.value }}: {{ about.version.value }}
            {% for res in about.about_resource.value -%}
                resource: {{ res }}
            {% endfor -%}
        {% endfor -%}'''
        expected = None
        assert expected == attrib.check_template(template)

    def test_check_template_complex_invalid_returns_error(self):
        template = '''
        {% for about in abouts -%}
            {{ about.name.value }}: {{ about.version.value }}
            {% for res in about.about_ressdsdsdsdsdsdource.value -%}
                resource: {{] res }}
            {% endfor -%}
        {% endfor -%}'''
        expected = (5, "unexpected ']'")
        assert expected == attrib.check_template(template)

    def test_check_template_invalid_return_error_lineno_and_message(self):
        expected = 1, "unexpected end of template, expected 'end of print statement'."
        assert expected == attrib.check_template('{{template_string')

    def test_check_template_all_builtin_templates_are_valid(self):
        builtin_templates_dir = os.path.dirname(attrib.DEFAULT_TEMPLATE_FILE)
        for template in os.listdir(builtin_templates_dir):
            template_loc = os.path.join(builtin_templates_dir, template)
            with io.open(template_loc, 'r', encoding='utf-8') as tmpl:
                template = tmpl.read()
            try:
                assert None == attrib.check_template(template)
            except:
                raise Exception(template_loc)


class GenerateTest(unittest.TestCase):

    def test_custom_temaplte(self):
        test_file = get_test_loc('test_attrib/scancode_custom_template/clean-text-0.3.0-mod-lceupi.json')
        custom_template =  get_test_loc('test_attrib/scancode_custom_template/scancode.template')
        errors, abouts = util.load_inventory(test_file, scancode=True)
        assert not errors

        lic_dict = {'isc': {'key': 'isc', 'short_name': 'ISC License', 'name': 'ISC License',
                            'category': 'Permissive', 'owner': 'ISC - Internet Systems Consortium',
                            'homepage_url': 'https://www.isc.org/software/license', 'notes': 'Per SPDX.org, this license is OSI certified.',
                            'spdx_license_key': 'ISC', 'text_urls': ['http://fedoraproject.org/wiki/Licensing:MIT#Old_Style_with_legal_disclaimer_2', 'http://openbsd.wikia.com/wiki/OpenBSD%27s_BSD_license', 'http://opensource.org/licenses/isc-license.txt', 'https://www.isc.org/software/license'],
                            'osi_url': 'http://opensource.org/licenses/isc-license.txt', 'other_urls': ['http://openbsd.wikia.com/wiki/OpenBSD%27s_BSD_license', 'http://www.isc.org/software/license', 'http://www.opensource.org/licenses/ISC', 'https://opensource.org/licenses/ISC', 'https://www.isc.org/downloads/software-support-policy/isc-license/', 'https://www.isc.org/isc-license-1.0.html'],
                            'license_text': 'Permission to use, copy, modify, and/or distribute this software for any purpose\nwith or without fee is hereby granted, provided that the above copyright notice\nand this permission notice appear in all copies.\n\nTHE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH\nREGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND\nFITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,\nINDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS\nOF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER\nTORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF\nTHIS SOFTWARE.\n'}}

        error, result = attrib.generate_from_file(abouts, lic_dict, min_license_score=0, template_loc=custom_template)
        assert not error

        expected_file = get_test_loc(
            'test_attrib/scancode_custom_template/expect.html')
        with open(expected_file) as exp:
            expected = exp.read()

        # strip the timestamp: the timestamp is wrapped in italic block
        result = remove_timestamp(result)
        expected = remove_timestamp(expected)
        assert expected == result

    def test_generate_with_default_template(self):
        test_file = get_test_loc('test_attrib/default_template/simple_sample.csv')
        errors, abouts = util.load_inventory(test_file)
        assert not errors

        lic_dict = {'bsd-new': 
                    {'key': 'bsd-new', 'short_name': 'BSD-3-Clause', 'name': 'BSD-3-Clause',
                     'category': 'Permissive', 'owner': 'Regents of the University of California',
                     'homepage_url': 'http://www.opensource.org/licenses/BSD-3-Clause',
                     'notes': 'Per SPDX.org, this license is OSI certified.',
                     'spdx_license_key': 'BSD-3-Clause', 'osi_license_key': 'BSD-3',
                     'text_urls': ['http://www.opensource.org/licenses/BSD-3-Clause'],
                     'osi_url': 'http://www.opensource.org/licenses/BSD-3-Clause',
                     'other_urls': ['http://framework.zend.com/license/new-bsd', 'https://opensource.org/licenses/BSD-3-Clause'],
                     'license_text': 'Redistribution and use in source and binary forms, with or without modification,\nare permitted provided that the following conditions are met:\n\nRedistributions of source code must retain the above copyright notice, this list\nof conditions and the following disclaimer.\n\nRedistributions in binary form must reproduce the above copyright notice, this\nlist of conditions and the following disclaimer in the documentation and/or\nother materials provided with the distribution.\n\nNeither the name of the ORGANIZATION nor the names of its contributors may be\nused to endorse or promote products derived from this software without specific\nprior written permission.\n\nTHIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS\n"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,\nTHE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE\nARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS\nBE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR\nCONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE\nGOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)\nHOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT\nLIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF\nTHE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'},
                    'mit': {'key': 'mit', 'short_name': 'MIT License', 'name': 'MIT License',
                            'category': 'Permissive', 'owner': 'MIT',
                            'homepage_url': 'http://opensource.org/licenses/mit-license.php',
                            'notes': 'Per SPDX.org, this license is OSI certified.', 'spdx_license_key': 'MIT',
                            'text_urls': ['http://opensource.org/licenses/mit-license.php'],
                            'osi_url': 'http://www.opensource.org/licenses/MIT',
                            'other_urls': ['https://opensource.com/article/18/3/patent-grant-mit-license', 'https://opensource.com/article/19/4/history-mit-license', 'https://opensource.org/licenses/MIT'],
                            'license_text': 'Permission is hereby granted, free of charge, to any person obtaining\na copy of this software and associated documentation files (the\n"Software"), to deal in the Software without restriction, including\nwithout limitation the rights to use, copy, modify, merge, publish,\ndistribute, sublicense, and/or sell copies of the Software, and to\npermit persons to whom the Software is furnished to do so, subject to\nthe following conditions:\n\nThe above copyright notice and this permission notice shall be\nincluded in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\nEXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\nIN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY\nCLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,\nTORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\nSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'}
                    }
        error, result = attrib.generate_from_file(abouts, lic_dict, min_license_score=0)
        assert not error

        expected_file = get_test_loc(
            'test_attrib/default_template/expect.html')
        with open(expected_file) as exp:
            expected = exp.read()

        # strip the timestamp: the timestamp is wrapped in italic block
        result = remove_timestamp(result)
        expected = remove_timestamp(expected)
        assert expected == result

def remove_timestamp(html_text):
    """
    Return the `html_text` generated attribution stripped from timestamps: the
    timestamp is wrapped in italic block in the default template.
    """
    return '\n'.join(x for x in html_text.splitlines() if not '<i>' in x)
