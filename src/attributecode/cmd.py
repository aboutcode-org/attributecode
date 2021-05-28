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

from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import io
import os
import sys

import click

# silence unicode literals warnings
click.disable_unicode_literals_warning = True

from attributecode import WARNING
from attributecode.util import unique

from attributecode import __version__
from attributecode import severities
from attributecode.attrib import check_template
from attributecode.attrib import DEFAULT_TEMPLATE_FILE, DEFAULT_LICENSE_SCORE
from attributecode.attrib import generate_and_save as generate_attribution_doc
from attributecode.model import pre_process_and_fetch_license_dict
from attributecode.util import filter_errors
from attributecode.util import get_file_text
from attributecode.util import load_inventory
from attributecode.util import number_of_component_generated_from_default_template


__copyright__ = """
    Copyright (c) nexB Inc and others. All rights reserved.
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License."""


prog_name = 'AttributeCode'


intro = '''%(prog_name)s version %(__version__)s
%(__copyright__)s
''' % locals()

def print_version():
    click.echo('Running attributecode version ' + __version__)

def validate_template(ctx, param, value):
    if not value:
        return DEFAULT_TEMPLATE_FILE

    with io.open(value, encoding='utf-8') as templatef:
        template_error = check_template(templatef.read())

    if template_error:
        lineno, message = template_error
        raise click.UsageError(
            'Template syntax error at line: '
            '{lineno}: "{message}"'.format(**locals()))
    return value


######################################################################
# option validators
######################################################################

def validate_key_values(ctx, param, value):
    """
    Return the a dict of {key: value} if valid or raise a UsageError
    otherwise.
    """
    if not value:
        return

    kvals, errors = parse_key_values(value)
    if errors:
        ive = '\n'.join(sorted('  ' + x for x in errors))
        msg = ('Invalid {param} option(s):\n'
               '{ive}'.format(**locals()))
        raise click.UsageError(msg)
    return kvals


######################################################################
# Error management
######################################################################

def report_errors(errors, quiet, verbose, log_file_loc=None):
    """
    Report the `errors` list of Error objects to screen based on the `quiet` and
    `verbose` flags.

    If `log_file_loc` file location is provided also write a verbose log to this
    file.
    Return True if there were severe error reported.
    """
    errors = unique(errors)
    messages, severe_errors_count = get_error_messages(errors, quiet, verbose)
    for msg in messages:
        click.echo(msg)
    if log_file_loc:
        log_msgs, _ = get_error_messages(errors, quiet=False, verbose=True)
        with io.open(log_file_loc, 'w', encoding='utf-8') as lf:
            lf.write('\n'.join(log_msgs))
    return severe_errors_count


def get_error_messages(errors, quiet=False, verbose=False):
    """
    Return a tuple of (list of error message strings to report,
    severe_errors_count) given an `errors` list of Error objects and using the
    `quiet` and `verbose` flags.
    """
    errors = unique(errors)
    severe_errors = filter_errors(errors, WARNING)
    severe_errors_count = len(severe_errors)

    messages = []

    if severe_errors and not quiet:
        error_msg = 'Command completed with {} errors or warnings.'.format(severe_errors_count)
        messages.append(error_msg)

    for severity, message in errors:
        sevcode = severities.get(severity) or 'UNKNOWN'
        msg = '{sevcode}: {message}'.format(**locals())
        if not quiet:
            if verbose:
                messages .append(msg)
            elif severity >= WARNING:
                messages .append(msg)
    return messages, severe_errors_count


######################################################################
# Misc
######################################################################

def parse_key_values(key_values):
    """
    Given a list of "key=value" strings, return:
    - a dict {key: value}
    - a sorted list of unique error messages for invalid entries where there is
      a missing a key or value.
    """
    if not key_values:
        return {}, []

    errors = set()
    parsed_key_values = defaultdict(list)
    for key_value in key_values:
        key, _, value = key_value.partition('=')

        key = key.strip().lower()
        if not key:
            errors.add('missing <key> in "{key_value}".'.format(**locals()))
            continue

        value = value.strip()
        if not value:
            errors.add('missing <value> in "{key_value}".'.format(**locals()))
            continue

        parsed_key_values[key] = value

    return dict(parsed_key_values), sorted(errors)

######################################################################
# Main Command
######################################################################

@click.command()
@click.version_option(version=__version__, prog_name=prog_name, message=intro)
@click.argument('input',
    required=True,
    metavar='INPUT',
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True))

@click.argument('output',
    required=True,
    metavar='OUTPUT',
    type=click.Path(exists=False, dir_okay=False, writable=True, resolve_path=True))

@click.option('-c', '--configuration',
    metavar='FILE',
    type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
    help='Path to an optional YAML configuration file for renaming fields name.')

@click.option('--min-license-score',
    type=int,
    help='Attribute components that have license score higher than the defined '
        '--min-license-score.')

@click.option('--scancode',
    is_flag=True,
    help='Indicate the input JSON file is from scancode_toolkit.')

@click.option('--reference',
    metavar='DIR',
    type=click.Path(exists=True, file_okay=False, readable=True, resolve_path=True),
    help='Path to a directory with reference files where "license_file" and/or "notice_file"' 
        ' located.')

@click.option('--template',
    metavar='FILE',
    callback=validate_template,
    type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True),
    help='Path to an optional custom attribution template to generate the '
         'attribution document. If not provided the default built-in template is used.')

@click.option('--vartext',
    multiple=True,
    callback=validate_key_values,
    metavar='<key>=<value>',
    help='Add variable text as key=value for use in a custom attribution template.')

@click.option('-q', '--quiet',
    is_flag=True,
    help='Do not print error or warning messages.')

@click.option('--verbose',
    is_flag=True,
    help='Show all error and warning messages.')

@click.help_option('-h', '--help')
def attributecode(input, output, configuration, scancode, min_license_score, reference, template, vartext, quiet, verbose):
    """
Generate attribution from JSON, CSV or Excel file.
    """
    if scancode:
        if not input.endswith('.json'):
            msg = 'The input file from scancode toolkit needs to be in JSON format.'
            click.echo(msg)
            sys.exit(1)
        if not min_license_score:
            min_license_score=DEFAULT_LICENSE_SCORE

    if min_license_score:
        if not scancode:
            msg = ('This option requires JSON file generated by scancode toolkit as the input. ' +
                    'The "--scancode" option is required.')
            click.echo(msg)
            sys.exit(1)

    errors, abouts = load_inventory(
        location=input,
        configuration=configuration,
        scancode=scancode,
        reference_dir=reference
    )

    licensedb_url = 'https://scancode-licensedb.aboutcode.org/'
    license_dict, lic_errors = pre_process_and_fetch_license_dict(abouts, licensedb_url, scancode, reference)
    errors.extend(lic_errors)
    sorted_license_dict = sorted(license_dict)

    # Read the license_file and store in a dictionary
    for about in abouts:
        if about.license_file.value or about.notice_file.value:
            if not reference:
                msg = '"license_file" / "notice_file" field contains value. Use `--reference` to indicate its parent directory.'
                click.echo(msg)
                sys.exit(1)
            if about.license_file.value:
                file_name = about.license_file.value
                error, text = get_file_text(file_name, reference)
                if not error:
                    about.license_file.value = {}
                    about.license_file.value[file_name] = text
                else:
                    errors.append(error)
            if about.notice_file.value:
                file_name = about.notice_file.value
                error, text = get_file_text(file_name, reference)
                if not error:
                    about.notice_file.value = {}
                    about.notice_file.value[file_name] = text
                else:
                    errors.append(error)


    rendered = ''
    if abouts:
        attrib_errors, rendered = generate_attribution_doc(
            abouts=abouts,
            license_dict=dict(sorted(license_dict.items())),
            output_location=output,
            min_license_score=min_license_score,
            template_loc=template,
            variables=vartext,
        )
        errors.extend(attrib_errors)

    errors = unique(errors)
    errors_count = report_errors(errors, quiet, verbose, log_file_loc=output + '-error.log')

    if rendered:
        # Check if the default template is used
        import filecmp
        default_template = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../templates/default_html.template')
        if filecmp.cmp(default_template, template):
            num_comps = number_of_component_generated_from_default_template(output)
            msg = '{num_comps} component(s) is/are in the generated attribution at the {output}'.format(**locals())
        else:
            msg = 'Attribution generated at: {output}'.format(**locals())
        click.echo(msg)
    else:
        msg = 'Attribution generation failed.'
        click.echo(msg)

    sys.exit(errors_count)


if __name__ == '__main__':
    attributecode()
