#!/usr/bin/env python
# Copyright 2017, Rackspace US, Inc.
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

import os

import yaml


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SCENARIO_FILE = '../../tests/vars/bootstrap-aio-vars.yml'
HTML_TABLE = """<html><table border="1">"""


def main():
    scenario_file = os.path.join(SCRIPT_PATH, SCENARIO_FILE)
    with open(scenario_file) as f:
        _meta_data = yaml.safe_load(f.read())

    scenario_meta_data = _meta_data['confd_overrides']
    scenarios = list(sorted(scenario_meta_data.keys()))
    scenarios.insert(0, '')
    HTML_TABLE = '<table border="1">'
    HTML_TABLE += '<thead valign="bottom"><tr>'
    for s in scenarios:
        HTML_TABLE += '<th style="padding-left:5px;padding-right:5px;" class="head">{}</th>'.format(s)
    HTML_TABLE += '</tr></thead><tbody valign="top">'

    config_items = set()
    for items in scenario_meta_data.values():
        for item in items:
            config_items.add(item['name'].split('.')[0])
    config_items = list(config_items)

    for item in config_items:
        HTML_TABLE += '<tr>'
        HTML_TABLE += '<td align="left">{}</td>'.format(item.lower())
        for scenario in scenarios:
            try:
                scenario_meta = scenario_meta_data[scenario]
            except KeyError:
                pass
            else:
                for _items in scenario_meta:
                    if item == _items['name'].split('.')[0]:
                        HTML_TABLE += '<td align="center">X</td>'
                        break
                else:
                    HTML_TABLE += '<td>&#160;</td>'
        HTML_TABLE += '</tr>'
    HTML_TABLE += '</tbody>'
    HTML_TABLE += '</table>'

    return HTML_TABLE


if __name__ == '__main__':
    print(main())
