# Copyright 2015, Rackspace US, Inc.
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
# (c) 2015, Kevin Carter <kevin.carter@rackspace.com>

import urlparse


"""Filter usage:

Simple filters that may be useful from within the stack
"""


def bit_length_power_of_2(value):
    """Return the smallest power of 2 greater than a numeric value.

    :param value: Number to find the smallest power of 2
    :type value: ``int``
    :returns: ``int``
    """
    return 2**(int(value)-1).bit_length()


def get_netloc(url):
    """Return the netloc from a URL.

    If the input value is not a value URL the method will raise an Ansible
    filter exception.

    :param url: the URL to parse
    :type url: ``str``
    :returns: ``str``
    """
    try:
        netloc = urlparse.urlparse(url).netloc
    except Exception as exp:
        raise errors.AnsibleFilterError(
            'Failed to return the netloc of: "%s"' % str(exp)
        )
    else:
        return netloc


def get_netloc_no_port(url):
    """Return the netloc without a port from a URL.

    If the input value is not a value URL the method will raise an Ansible
    filter exception.

    :param url: the URL to parse
    :type url: ``str``
    :returns: ``str``
    """
    return get_netloc(url=url).split(':')[0]


def get_netorigin(url):
    """Return the netloc from a URL.

    If the input value is not a value URL the method will raise an Ansible
    filter exception.

    :param url: the URL to parse
    :type url: ``str``
    :returns: ``str``
    """
    try:
        parsed_url = urlparse.urlparse(url)
        netloc = parsed_url.netloc
        scheme = parsed_url.scheme
    except Exception as exp:
        raise errors.AnsibleFilterError(
            'Failed to return the netorigin of: "%s"' % str(exp)
        )
    else:
        return '%s://%s' % (scheme, netloc)


class FilterModule(object):
    """Ansible jinja2 filters."""

    @staticmethod
    def filters():
        return {
            'bit_length_power_of_2': bit_length_power_of_2,
            'netloc': get_netloc,
            'netloc_no_port': get_netloc_no_port,
            'netorigin': get_netorigin
        }
