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


"""Simple input script to return a list of branches in a github repo.

This script will return a space seperated list of all of the branches available
from within a git repo as found in the github api. When running the script you
can provide a list of branches that you want to exclude from the returned list.
This exclusion list a matched based list and will exclude anything that matches
the list of strings.

Example Usage:
~$ # Endpoint
~$ GITHUB_API_ENDPOINT="https://api.github.com/repos/stackforge/os-ansible-deployment"
~$ # Exclusions
~$ EXCLUDE_RELEASES="v9.0.0 gh-pages revert"
~$ # Run script
~$ /opt/openstack-branch-grabber.py "${GITHUB_API_ENDPOINT}" "${EXCLUDE_RELEASES}"

Example Library Usage:
>>> endpoint_url = "https://api.github.com/repos/stackforge/os-ansible-deployment"
>>> exclude_list = ["v9.0.0", "gh-pages", "revert"]
>>> print(main(endpoint_url, exclude_list))
9.0.0 9.0.1 9.0.2 9.0.3 stable/icehouse proposed/juno master
"""


import functools
import requests
import sys
import time


def retry(exception_check, tries=3, delay=1, backoff=1):
    """Retry calling the decorated function using an exponential backoff.

    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param exception_check: ``Exception || Tuple`` the exception to check.
                             may be a tuple of exceptions to check
    :param tries: ``int`` number of times to try (not retry) before giving up
    :param delay: ``int`` initial delay between retries in seconds
    :param backoff: ``int`` backoff multiplier e.g. value of 2 will double the
                    delay each retry
    """
    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_check:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


@retry(exception_check=Exception)
def get_url(url):
    return requests.get(url)


@retry(exception_check=(AttributeError, ValueError))
def return_releases(url, exclude_list=None):
    """Return a list of releases found in the github api.

    :param url: ``str`` URL to hit public github api
    :param exclude_list: ``str`` Branches to exclude
    """
    _releases = get_url(url)
    loaded_releases = _releases.json()
    releases = list()

    if exclude_list is None:
        exclude_list = list()

    for i in loaded_releases:
        for k, v in i.iteritems():
            if k == 'name':
                # if the name is not excluded append it
                if not any([v.startswith(i) for i in exclude_list]):
                    releases.append(v)
    else:
        # Return a unique list.
        return list(set(releases))


def main(endpoint_url, exclude_list):
    """Run the main application."""

    # Create an array of all releases and branches.
    all_releases = list()
    all_releases.extend(
        return_releases(
            url="%s/tags" % endpoint_url,
            exclude_list=exclude_list
        )
    )
    all_releases.extend(
        return_releases(
            url="%s/branches" % endpoint_url,
            exclude_list=exclude_list
        )
    )

    # Print all of the releases that were found within the github api.
    print(' '.join(all_releases))


if __name__ == '__main__':
    # git api endpoint to use for searching for releases and branches
    endpoint = sys.argv[1]

    # Create an array of excluded items
    if len(sys.argv) >= 3:
        exclude = sys.argv[2].split()
    else:
        exclude = list()

    main(endpoint_url=endpoint, exclude_list=exclude)
