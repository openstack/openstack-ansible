#!/usr/bin/env python
# Copyright 2014, Rackspace US, Inc.
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
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>

"""
This script will build a pip.conf file dynamically based on a simple
configuration layout.  The purpose of this script is to allow automation to
deploy parts of the main `pip.conf` file incrementally creating links and
sections as needed.

Structure:
    $HOME/.pip/
    $HOME/.pip/base
    $HOME/.pip/links.d

creates:
    $HOME/.pip/pip.conf


* The script reads all configuration files from the base directory and then
  applies the sections to the main config file at "$HOME/.pip/pip.conf"
* Within the [install] section will be generated with the value `find-links`
  built from the link files found in "$HOME/.pip/links.d".
"""

import ConfigParser
import os
import urlparse


def config_files(config_dir_path, extension='.link'):
    """Discover all link files.

    :param config_dir_path: ``str`` Path to link directory
    :param extension: ``str`` Extension for files
    :return: ``list``
    """
    link_files = list()
    for root_path, _, pip_files in os.walk(config_dir_path):
        for f in pip_files:
            if f.endswith(extension):
                link_files.append(os.path.join(root_path, f))
    else:
        return link_files


def pip_links(links_files):
    """Read all link files.

    :param links_files: ``list`` List of files to read containing links
    :return: `list``
    """
    links = list()
    for link in links_files:
        with open(link, 'rb') as f:
            links.extend(f.readlines())
    else:
        return links


def load_config(config_file):
    """Load config from a file.

    :param config_file: ``str``  path to config file
    :return: ``object``
    """
    config = ConfigParser.ConfigParser()
    if config_file is None:
        return config

    try:
        with open(config_file) as f:
            config.readfp(f)
    except IOError:
        return config
    else:
        return config


def set_links(links):
    """Set all links and ensure there are no blank lines.

    :param links: ``list`` List of all raw links
    :return: ``str``
    """
    pip_find_links = list()
    for link in links:
        if link != '\n' or not link:
            pip_find_links.append(link.rstrip('\n'))

    links = [i for i in list(set(pip_find_links))]
    return '\n%s' % '\n'.join(links)


def build_main_config(add_conf, main_config):
    """Build configuration from all found conf files.

    :param add_conf: ``object`` ConfigParser object
    :param main_config: ``object`` ConfigParser object
    """
    for section in add_conf.sections():
        try:
            main_config.add_section(section)
        except ConfigParser.DuplicateSectionError:
            pass

        for k, v in add_conf.items(section):
            main_config.set(section, k, v)


def build_install_section(main_dir_path, main_config):
    """Build the install section with links.

    :param main_dir_path: ``str`` Directory path
    :param main_config: ``object`` ConfigParser object
    """
    links = list()
    trusted_host = list()
    links_dir = os.path.join(main_dir_path, 'links.d')
    if os.path.isdir(links_dir):
        _link = config_files(config_dir_path=links_dir, extension='.link')
        _links = pip_links(_link)
        links.extend(_links)
        for _link in _links:
            # Make sure that just the hostname/ip is used.
            trusted_host.append(urlparse.urlparse(_link).netloc.split(':')[0])
        else:
            main_config.set('global', 'trusted-host', set_links(trusted_host))

    # Add install section if not already found
    try:
        main_config.add_section('install')
    except ConfigParser.DuplicateSectionError:
        pass

    # Get all items from the install section
    try:
        install_items = main_config.items('install')
    except ConfigParser.NoSectionError:
        install_items = None

    link_strings = set_links(links)
    if install_items:
        for item in install_items:
            if item[0] != 'find-links':
                main_config.set('install', *item)

    main_config.set('install', 'find-links', link_strings)


def main():
    """Run the main application."""
    main_file_path = os.path.expanduser('~/.pip/pip.conf')
    main_config = load_config(config_file=None)

    main_dir_path = os.path.dirname(main_file_path)
    base_dir_path = os.path.join(main_dir_path, 'base')
    if os.path.isdir(base_dir_path):
        _confs = config_files(base_dir_path, extension='.conf')
        for _conf in _confs:
            _config = load_config(config_file=_conf)
            build_main_config(_config, main_config)

    build_install_section(main_dir_path, main_config)

    # Write out the config file
    with open(main_file_path, 'wb') as f:
        main_config.write(f)


if __name__ == '__main__':
    main()
