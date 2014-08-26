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

# Python Standard Libraries
import os
import sys
import time
import os.path
import logging
import functools
import subprocess
import logging.handlers

# PIP Libraries
import click
import pexpect


# Configuration
playbook_cmd = "ansible-playbook %s -e @/etc/rpc_deploy/user_variables.yml %s"
restart_containers_sleep_seconds = 120
color_codes_to_strip_from_log = [
    '\033[0m',
    '\033[0;31m',
    '\033[0;32m',
    '\033[0;33m',
    '\033[0;34m',
    '\033[0;36m']


class LXCNotInstalledOrNotRunnableError(Exception):
    def __init__(self, error, output):
        self.error = error
        self.output = output

    def __str__(self):
        return repr("%s: %s" % (self.error, self.output))


class TooManyPlaybookFailuresError(Exception):
    def __init__(self, playbook, retries):
        self.playbook = playbook
        self.retries = retries

    def __str__(self):
        return repr([self.playbook, self.retries])


class ChildProcessReturnedNonZeroError(Exception):
    def __init__(self, errorcode):
        self.errorcode = errorcode

    def __str__(self):
        return repr(self.errorcode)


class StripColorCodesFormatter(logging.Formatter):
    def format(self, record):
        for code_to_strip in color_codes_to_strip_from_log:
            record.msg = record.msg.replace(
                code_to_strip, '')
        return logging.Formatter.format(self, record)


def configure_logger(log_file):
    logger = logging.getLogger('OpenStackInstaller')

    log_formatter = StripColorCodesFormatter(
        "%(name)s: %(asctime)s - %(levelname)s: %(message)s")

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=104857600, backupCount=10)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def execute(command):
    """
    Executes a command, polling for output and printing the output as it runs.
    """
    child = pexpect.spawn(command)
    while True:
        try:
            child.expect('\n', timeout=None)
            click.echo(child.before)
            LOG.debug(child.before)
        except pexpect.EOF:
            break
    child.close()
    if child.exitstatus != 0:
        raise ChildProcessReturnedNonZeroError(child.exitstatus)


def scriptdir():
    """
    Returns the directory where this script is located.
    """
    return os.path.dirname(os.path.realpath(__file__))


def rundir():
    """
    Returns the directory where our ansible playbooks should be executed from.
    """
    return os.path.realpath(
        os.path.join(scriptdir(), '../rpc_deployment'))


def get_container_name(containerstring):
    """
    Returns the container name that contains containerstring. In the case
    where there are multiple containers matching containerstring, returns only
    the first one. Returns None for no match.
    """
    try:
        containers = subprocess.check_output(
            'lxc-ls',
            stderr=subprocess.STDOUT).split('\n')
    except subprocess.CalledProcessError as e:
        raise LXCNotInstalledOrNotRunnableError(e.returncode, e.output)
    except OSError as e:
        raise LXCNotInstalledOrNotRunnableError(e.errno, e.strerror)
    for line in containers:
        if containerstring in line:
            return line
    return None


def print_status(haproxy, galera, rabbit, ansible_rundir, retries):
    click.echo("Running ansible-lxc-rpc installer/updater.")
    click.echo("About to install openstack.")
    click.echo("Using %s as our ansible run directory" % ansible_rundir)
    click.echo("Trying %s retries with each playbook" % retries)
    if haproxy:
        click.echo("We will install haproxy. Do not use this in a "
                   "production environment.")
    else:
        click.echo("NOT installing haproxy. This means you must have a "
                   "loadbalancer in place, configured separately.")
    if galera:
        click.echo("We will install galera.")
    else:
        click.echo("NOT installing galera. This means that you must "
                   "separately install and configure the database.")
    if rabbit:
        click.echo('We will install RabbitMQ.')
    else:
        click.echo("NOT installing RabbitMQ. This means you are "
                   "reponsible for installing and configuring it.")


def run_restart_containers_playbook(retries, ansible_rundir, galera):
    run_playbook('setup/restart-containers.yml', retries, ansible_rundir)
    LOG.debug("Sleeping %s seconds" % restart_containers_sleep_seconds)
    time.sleep(restart_containers_sleep_seconds)
    if galera:
        # Restarting containers does not always restart galera, especially
        # if it's an AIO. The system startup scripts do not have the bootstrap
        # necessary for a single-node cluster.
        run_playbook(
            'infrastructure/galera-startup.yml', retries, ansible_rundir)


def run_playbook(playbook, retries, ansible_rundir):
    """
    Runs an individual playbook. Attempts multiple runs.
    """
    extra_options = ""
    success = False
    attempt = 1
    os.chdir(ansible_rundir)

    playbook = os.path.join('playbooks', playbook)
    os.environ["ANSIBLE_FORCE_COLOR"] = "true"
    while not success:
        playbook_full_cmd = playbook_cmd % (extra_options, playbook)
        try:
            LOG.info(
                'About to execute attempt %s of command: "%s"' %
                (attempt, playbook_full_cmd))
            execute(playbook_full_cmd)
            LOG.info('Successfully completed playbook "%s"' % playbook)
            success = True
        except ChildProcessReturnedNonZeroError:
            attempt += 1
            pb_name = playbook.split('/')[-1].split('.')[0]
            extra_options = "-vvvv --limit @/%s/%s.retry" % (
                os.path.expanduser("~"), pb_name)
            os.environ["GIT_CURL_VERBOSE"] = "1"
        if not success and attempt > retries:
            raise TooManyPlaybookFailuresError(playbook, retries)


@click.command()
@click.option('--haproxy/--no-haproxy',
              default=False,
              help='Should we install Haproxy? Defaults to no.')
@click.option('--galera/--no-galera',
              default=False,
              help='Should we install Galera? Defaults to no.')
@click.option('--rabbit/--no-rabbit',
              default=False,
              help='Should we install RabbitMQ? Defaults to no.')
@click.option('--retries',
              default=3,
              help='Number of retries to attempt on an Ansible playbook '
                   'before giving up.')
def run_the_ansibles(haproxy, galera, rabbit, retries):
    ansible_rundir = rundir()
    print_status(haproxy, galera, rabbit, ansible_rundir, retries)

    run_p = functools.partial(
        run_playbook, retries=retries, ansible_rundir=ansible_rundir)
    run_p('setup/host-setup.yml')
    run_p('setup/build-containers.yml')
    run_restart_containers_playbook(retries, ansible_rundir, galera=False)
    run_p('setup/host-common.yml')

    if galera:
        galera_container = get_container_name('galera')
        if galera_container is not None and os.path.isfile(
                os.path.join('/openstack/', galera_container, 'galera.cache')):
            run_p('infrastructure/galera-bootstrap.yml')
            run_p('infrastructure/galera-config.yml')
            run_p('infrastructure/galera-startup.yml')
        else:
            run_p('infrastructure/galera-install.yml')
            run_p('infrastructure/galera-startup.yml')

    run_p('infrastructure/memcached-install.yml')

    if rabbit:
        run_p('infrastructure/rabbit-install.yml')

    run_p('infrastructure/rsyslog-install.yml')
    run_p('infrastructure/elasticsearch-install.yml')
    run_p('infrastructure/logstash-install.yml')
    run_p('infrastructure/kibana-install.yml')
    run_p('infrastructure/rsyslog-config.yml')
    run_p('infrastructure/es2unix-install.yml')

    if haproxy:
        run_p('infrastructure/haproxy-install.yml')

    run_restart_containers_playbook(retries, ansible_rundir, galera)

    run_p('openstack/utility.yml')
    run_p('openstack/openstack-common.yml')
    run_p('openstack/keystone.yml')
    run_p('openstack/keystone-add-all-services.yml')
    run_p('openstack/keystone-add-users.yml')
    run_p('openstack/glance-all.yml')
    run_p('openstack/heat-all.yml')
    run_p('openstack/nova-all.yml')
    run_p('openstack/neutron-all.yml')
    run_p('openstack/cinder-all.yml')
    run_p('openstack/horizon.yml')
    run_restart_containers_playbook(retries, ansible_rundir, galera)


LOG = configure_logger('/var/log/rpc-openstack-installer.log')


def main():
    try:
        run_the_ansibles()
    except TooManyPlaybookFailuresError as e:
        LOG.critical(
            "Failed running playbook '%s' %s times. Aborting..." %
            (e.playbook, e.retries))
        sys.exit(50)
    except LXCNotInstalledOrNotRunnableError as e:
        LOG.critical(
            'Failed running lxc-ls. '
            'Got return code %s and output "%s"' % (e.error, e.output))
        sys.exit(51)


if __name__ == '__main__':
    main()
