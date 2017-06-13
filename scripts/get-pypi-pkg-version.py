#!/usr/bin/env python2
#
# Copyright 2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2016, Jesse Pretorius <jesse.pretorius@rackspace.co.uk>
#


"""Returns the versions of a list of pypi packages you specify."""


from __future__ import print_function

import argparse
import re
import xmlrpclib

PRE_RELEASE_RE = re.compile('a|b|rc')


def get_package_version(pypiConn, pkg_name):
    """Get the current package version from PyPI."""
    pkg_result = [v for v in pypiConn.package_releases(pkg_name, True)
                  if not PRE_RELEASE_RE.search(v)]
    if pkg_result:
        pkg_version = pkg_result[0]
    else:
        pkg_version = 'Not available.'

    return pkg_version


def main():
    """Run the main application."""

    # Setup argument parsing
    parser = argparse.ArgumentParser(
        description='PyPI Current Package Version Checker',
        epilog='Licensed "Apache 2.0"')

    parser.add_argument(
        '-f',
        '--format',
        choices=['requirements', 'bare'],
        default='requirements',
        help='<Optional> Output format',
        required=False
    )

    parser.add_argument(
        '-l',
        '--layout',
        choices=['vertical', 'horizontal'],
        default='vertical',
        help='<Optional> Output layout',
        required=False
    )

    parser.add_argument(
        '-p',
        '--packages',
        nargs='+',
        help='<Required> Space-delimited list of packages',
        required=True
    )

    # Parse arguments
    args = parser.parse_args()

    # Setup pypi object
    pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')

    # Setup the newline if the results layout should be vertical
    # Also add a space delimiter appropriately
    if args.layout == 'vertical':
        delimiter = ''
        endline = '\n'
    else:
        delimiter = ' '
        endline = ''

    # Print the results to stdout
    for pkg_name in args.packages:
        pkg_version = get_package_version(pypi, pkg_name)
        if args.format == 'requirements':
            print(pkg_name + '==' + pkg_version + delimiter, end=endline)
        else:
            print(pkg_version + delimiter, end=endline)


if __name__ == "__main__":
    main()
