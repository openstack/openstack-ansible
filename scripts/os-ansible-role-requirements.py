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

import json
import os
import requests
import yaml

from cloudlib import arguments


def _arguments():
    """Return CLI arguments."""

    arguments_dict = {
        'shared_args': {
            'filter': {
                'commands': [
                    '--filter'
                ],
                'help': 'filter the git api repo returns to the string'
                        ' type that begins with the string provided.'
                        ' Filtering is ONLY ever used with pulling'
                        ' from the upstream github API.'
                        ' Default: %(default)s',
                'metavar': '[STR]',
                'default': 'openstack_role-'
            }
        },
        'optional_args': {
            'requirement_file': {
                'commands': [
                    '--requirement-file'
                ],
                'help': 'Path to a dictionary file. The file should contain'
                        ' one word per line. Default: %(default)s',
                'metavar': '[PATH]',
                'default': os.path.join(
                    os.getcwd(),
                    'ansible-role-requirements.yml'
                )
            },
            'repo': {
                'commands': [
                    '--repo'
                ],
                'help': 'Full path the git repo api path that the script will'
                        ' scan through.',
                'metavar': '[URL]',
                'default': 'https://api.github.com/orgs/os-cloud/repos'
            },
            'git_username': {
                'commands': [
                    '-u',
                    '--git-username'
                ],
                'help': 'Username for a github account.',
                'metavar': '[STR]',
                'default': None
            },
            'git_password': {
                'commands': [
                    '-p',
                    '--git-password'
                ],
                'help': 'Passowrd for a github account.',
                'metavar': '[STR]',
                'default': None
            }
        },
        'subparsed_args': {
            'update': {
                'help': 'Run an update on an existing inventory. This will'
                        ' attempt to update all of your role, that have a'
                        ' defined `github_api` key to the latest tag. If a tag'
                        ' is not available the default branch will be used.',
                'shared_args': ['filter']
            },
            'create': {
                'help': 'Create a new ansible requirements file based on the'
                        ' discovered repositories using a defined filter on'
                        ' the repo name.',
                'shared_args': ['filter']
            }
        }
    }

    return arguments.ArgumentParserator(
        arguments_dict=arguments_dict,
        epilog='Licensed Apache2',
        title='Create/Update an ansible galaxy repository file',
        detail='Ansible Galaxy repository generator that will parse an'
               ' existing requirements file and update it the latest stable'
               ' release or create a new one if one was not passed into the'
               ' generator or discovered.',
        description='Generate an ansible galaxy requirements file.',
        env_name='OpenStack'
    ).arg_parser()


def process_request(url, auth):
    """Perform an http request.

    :param url: full url to query
    :type url: ``str``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    :returns: ``dict``
    """
    content = requests.get(url, auth=auth)
    if content.status_code >= 300:
        raise SystemExit(content.content)
    return content.json()


def _get_repos(repo_access, auth):
    """Return a list of repositories from the provided github api.

    :param repo_access: requests head object.
    :type repo_access: ``str``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    :return: ``list``
    """
    if 'link' in repo_access.__dict__:
        repo_content = list()
        links = repo_access.__dict__['link'].split(',')
        pages = [i.replace(' ', '') for i in links if 'last' in i]
        page_link = pages[0].split(';')[0]
        page_link = page_link.strip('>').strip('<')
        page_link = page_link.split('=')
        for page in range(0, int(page_link[-1])):
            page_number = page + 1
            content = requests.get(
                '%s=%s' % (page_link, page_number),
                auth=auth
            )
            for repo in content.json():
                repo_content.append(repo)
        else:
            return json.loads(repo_content)
    else:
        return process_request(url=repo_access.__dict__['url'], auth=auth)


def get_repos(url, auth=None):
    """Return json from a request URL.

    This method assumes that you are hitting the github API.

    :param url: Full url to the git api user / org / or repo.
    :type url: ``str``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    :returns: ``dict``
    """
    return _get_repos(
        repo_access=requests.head(url, auth=auth),
        auth=auth
    )


def process_tags(git_repo, repo, auth):
    """Itentify and set the highest tag from a git repo.

    :param git_repo: github repo item
    :type git_repo: ``dict``
    :param repo: anisble repo manifest item
    :type repo: ``dict``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    """
    try:
        tags = process_request(url=git_repo['tags_url'], auth=auth)
        if tags:
            latest_release = max([i['name'] for i in tags])
        else:
            latest_release = git_repo['default_branch']
    except (IndexError, KeyError):
        repo['version'] = git_repo['default_branch']
    else:
        repo['version'] = latest_release


def create_from_github_repos(args, auth):
    """Return a list of dicts used for creating an ansible role manifest.

    :param args: user defined arguments
    :type args: ``dict``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    :return: ``list``
    """
    requirements = list()
    filter_name = args['filter']

    for repo in get_repos(url=args['repo'], auth=auth):
        if filter_name and not repo['name'].startswith(filter_name):
            continue

        print('* Repo created: [ %s ]' % repo['name'])
        item = dict()
        item['src'] = repo['html_url']
        item['name'] = repo['name'].split('-')[-1]
        item['github_api'] = repo['url']
        process_tags(git_repo=repo, repo=item, auth=auth)
        requirements.append(item)
    else:
        return requirements


def update_existing_repos(repos, auth):
    """Update existing repos for new tags.

    For this method to work the entry in the manifest must have an entry
    for ``github_api``. If this item is not found, the repo entry will be
    skipped.

    :param repos: list of items in an existing manifest.
    :type repos: ``list``
    :param auth: username, password credentials
    :type auth: ``tuple`` || ``None``
    :return:
    """
    for repo in repos:
        github_api = repo.get('github_api')
        if github_api:
            print('* Repo checking for update: [ %s ]' % repo['name'])
            git_repo = process_request(url=github_api, auth=auth)
            process_tags(git_repo=git_repo, repo=repo, auth=auth)
    else:
        return repos


def requirements_file(args):
    requirement_file = os.path.abspath(
        os.path.expanduser(
            args['requirement_file']
        )
    )

    if not os.path.isdir(os.path.dirname(requirement_file)):
        os.makedirs(os.path.dirname(requirement_file))

    return requirement_file


def build_requirements(args):
    args['requirement_file'] = requirements_file(args)

    if args['git_username']:
        _auth = (args['git_username'], args['git_password'])
    else:
        _auth = None

    if args['parsed_command'] == 'create':
        requirements = create_from_github_repos(args=args, auth=_auth)
    elif args['parsed_command'] == 'update':
        if os.path.isfile(args['requirement_file']):
            with open(args['requirement_file'], 'rb') as f:
                requirements = update_existing_repos(
                    repos=yaml.safe_load(f.read()),
                    auth=_auth
                )
        else:
            requirements = create_from_github_repos(args=args, auth=_auth)
    else:
        raise SystemExit(
            '"parsed_command: %s" not found.' % args['parsed_command']
        )

    with open(args['requirement_file'], 'wb') as f:
        f.write(
            yaml.safe_dump(
                sorted(requirements, key=lambda k: k['name']),
                default_flow_style=False,
                width=1000
            )
        )

    print('File Ready: [ %s ]' % args['requirement_file'])


def main():
    user_args = _arguments()
    build_requirements(args=user_args)


if __name__ == '__main__':
    main()
