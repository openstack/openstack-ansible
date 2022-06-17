#!/usr/bin/python3

import datetime
import multiprocessing
import os
import sys
import signal
import subprocess
import yaml
from systemd import journal
from collections import defaultdict

# ----------------------------------------------------------------------
# load ansible-role-requirements.yml
def get_ansible_role_names():
    with open(str(sys.argv[1]), 'r') as a_r_r_file:
        try:
            a_r_r = yaml.safe_load(a_r_r_file)
        except yaml.YAMLError as exc:
            print(exc)

    role_service_names = []
    role_prefix = "os_"
    for role in a_r_r:
        if role['name'].startswith(role_prefix):
            role_service_names.append(role['name'][len(role_prefix):])

    return role_service_names


# ----------------------------------------------------------------------
# get the list of containers and where their journals are
def get_container_journals():
    journals = []

    try:
        s = subprocess.run(['lxc-ls', '-1'], stdout=subprocess.PIPE)
    except FileNotFoundError:
        return journals

    containers = s.stdout.decode('utf-8').splitlines()

    for container_name in containers:
        info = {}
        info['name'] = container_name
        info['subdir'] = "openstack"
        s = subprocess.run(['lxc-info', '--pid', '--no-humanize', container_name], stdout=subprocess.PIPE)
        info['pid'] = s.stdout.decode('utf-8').strip()

        if(len(info['pid']) == 0):
          continue

        info['etc_dir'] = "/proc/" + str(info['pid']) + "/root/etc"

        with open(info['etc_dir'] + "/machine-id", 'r') as machine_id_file:
            machine_id = machine_id_file.read().strip()

        info['journal_dir'] = "/proc/" + str(info['pid']) + \
                              "/root/var/log/journal/" + machine_id
        journals.append(info)

    return journals


# ----------------------------------------------------------------------
def demux_one_journal(j):
    print("Gathering journals from " + j['name'])

    # open the journal from a specific directory, or use the host journal
    if 'journal_dir' in j:
        print("  Using journal dir " + j['journal_dir'])
        jreader = journal.Reader(path=j['journal_dir'])
    else:
        print("  Using host journal")
        jreader = journal.Reader()

    # the path to where we will save the journal for this host/container
    j_dir = working_dir + '/logs'
    if 'subdir' in j:
        j_dir = j_dir + '/' + j['subdir']
    d_dir = j_dir
    j_dir = j_dir + '/' + j['name']
    d_dir = d_dir + '/deprecations/' + j['name']

    # Create regular logs directory
    if not os.path.isdir(j_dir):
        os.makedirs(j_dir)

    # Create deperecations directory
    if not os.path.isdir(d_dir):
        os.makedirs(d_dir)

    output_files = {}

    # for each journal entry, try to match it with the services we care about
    # and split each service out into its own list of journal entries
    for entry in jreader:
        if 'MESSAGE' not in entry:
            continue
        if '_SYSTEMD_UNIT' not in entry:
            continue

        unit = entry['_SYSTEMD_UNIT']
        if not next((s for s in service_names if s in unit), None):
            continue

        # write each matched service journal entry out
        s_name = '/' + unit + '.journal-' + timestamp + '.log'
        j_filename = j_dir + s_name
        message = str(entry['MESSAGE'])
        message_time = str(entry['__REALTIME_TIMESTAMP'])
        result_message = f"{message_time} {unit} {message}\n"
        if j_filename not in output_files:
            output_files[j_filename] = open(j_filename, 'w')
        output_files[j_filename].write(result_message)

        if 'eprecat' not in message:
            continue

        d_filename = d_dir + s_name
        if d_filename not in output_files:
            output_files[d_filename] = open(d_filename, 'w')
        output_files[d_filename].write(result_message)

    for fd in output_files.values():
        fd.close()

    # We created directories regardless if they needed or not. We should drop empty ones.
    empty_dirs = set([j_dir, d_dir]) - set([os.path.dirname(fn) for fn in output_files.keys()])

    for e_dir in empty_dirs:
        try:
            os.rmdir(e_dir)
        except OSError:
            continue

    print(''.join(['    Written ' + k + '\n' for k in output_files.keys()]))

    return True


# ----------------------------------------------------------------------
def init_signal():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


# ----------------------------------------------------------------------
# always collect the host journal, first in the list as it's probably
# the largest
host_journal = [{}]
host_journal[0]['name'] = 'host'

journals = []
journals = journals + host_journal
journals = journals + get_container_journals()

print(journals)

# common log names are passed as the trailing arguments
if len(sys.argv) > 2:
  common_log_names = sys.argv[2::]
else:
  common_log_names = []

service_names = set(common_log_names + get_ansible_role_names())
print("Service names to search for " + str(service_names))

if os.getenv('WORKING_DIR') is not None:
    working_dir = os.getenv('WORKING_DIR')
else:
    working_dir = os.getcwd()

if os.getenv('TS') is not None:
    timestamp = os.getenv('TS')
else:
    timestamp = datetime.datetime.now().strftime('%H-%M-%S')

p = multiprocessing.Pool(multiprocessing.cpu_count(), init_signal)
journal_success = p.map(demux_one_journal, journals)
p.close()

success = all(i for i in journal_success)
if success:
    print("Journal collection Success!")
else:
    print("Error during journal collection")
