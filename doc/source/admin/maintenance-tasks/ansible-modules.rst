Running ad-hoc Ansible plays
============================

Being familiar with running ad-hoc Ansible commands is helpful when
operating your OpenStack-Ansible deployment. For a review, we can look at the
structure of the following Ansible command:

.. code-block:: console

   $ ansible example_group -m shell -a 'hostname'

This command calls on Ansible to run the ``example_group`` using
the ``-m`` shell module with the ``-a`` argument which is the hostname command.
You can substitute example_group for any groups you may have defined. For
example, if you had ``compute_hosts`` in one group and ``infra_hosts`` in
another, supply either group name and run the command. You can also use the
``*`` wild card if you only know the first part of the group name, for
instance if you know the group name starts with compute you would use
``compute_h*``. The ``-m`` argument is for module.

Modules can be used to control system resources or handle the execution of
system commands. For more information about modules, see
`Module Index <https://docs.ansible.com/ansible/modules_by_category.html>`_ and
`About Modules <https://docs.ansible.com/ansible/modules.html>`_.

If you need to run a particular command against a subset of a group, you
could use the limit flag ``-l``. For example, if a ``compute_hosts`` group
contained ``compute1``, ``compute2``, ``compute3``, and ``compute4``, and you
only needed to execute a command on ``compute1`` and ``compute4`` you could
limit the command as follows:

.. code-block:: console

   $ ansible example_group -m shell -a 'hostname' -l compute1,compute4

.. note::

   Each host is comma-separated with no spaces.

.. note::

   Run the ad-hoc Ansible commands from the ``openstack-ansible/playbooks``
   directory.

For more information, see `Inventory <https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html>`_
and `Patterns <https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html>`_.

Running the shell module
------------------------

The two most common modules used are the ``shell`` and ``copy`` modules. The
``shell``  module takes the command name followed by a list of space delimited
arguments. It is almost like the command module, but runs the command through
a shell (``/bin/sh``) on the remote node.

For example, you could use the shell module to check the amount of disk space
on a set of Compute hosts:

.. code-block:: console

   $ ansible compute_hosts -m shell -a 'df -h'

To check on the status of your Galera cluster:

.. code-block:: console

   $ ansible galera_container -m shell -a "mariadb \
   -e 'show status like \"%wsrep_cluster_%\";'"

When a module is being used as an ad-hoc command, there are a few parameters
that are not required. For example, for the ``chdir`` command, there is no need
to :command:`chdir=/home/user ls` when running Ansible from the CLI:

.. code-block:: console

   $ ansible compute_hosts -m shell -a 'ls -la /home/user'

For more information, see `shell - Execute commands in nodes
<https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html>`_.

Running the copy module
-----------------------

The copy module copies a file on a local machine to remote locations. To copy
files from remote locations to the local machine you would use the fetch
module. If you need variable interpolation in copied files, use the template
module. For more information, see `copy - Copies files to remote locations
<https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html>`_.

The following example shows how to move a file from your deployment host to the
``/tmp`` directory on a set of remote machines:

.. code-block:: console

   $ ansible remote_machines -m copy -a 'src=/root/FILE '\
   'dest=/tmp/FILE'

The fetch module gathers files from remote machines and stores the files
locally in a file tree, organized by the hostname.

.. note::

    This module transfers log files that might not be present, so a missing
    remote file will not be an error unless ``fail_on_missing`` is set to
    ``yes``.


The following examples shows the :file:`nova-compute.log` file being pulled
from a single Compute host:


.. code-block:: console

   root@libertylab:/opt/rpc-openstack/openstack-ansible/playbooks# ansible compute_hosts -m fetch -a 'src=/var/log/nova/nova-compute.log dest=/tmp'
   aio1 | success >> {
       "changed": true,
       "checksum": "865211db6285dca06829eb2215ee6a897416fe02",
       "dest": "/tmp/aio1/var/log/nova/nova-compute.log",
       "md5sum": "dbd52b5fd65ea23cb255d2617e36729c",
       "remote_checksum": "865211db6285dca06829eb2215ee6a897416fe02",
       "remote_md5sum": null
   }

   root@libertylab:/opt/rpc-openstack/openstack-ansible/playbooks# ls -la /tmp/aio1/var/log/nova/nova-compute.log
   -rw-r--r-- 1 root root 2428624 Dec 15 01:23 /tmp/aio1/var/log/nova/nova-compute.log

Using tags
----------

Tags are similar to the limit flag for groups, except tags are used to only run
specific tasks within a playbook. For more information on tags, see
`Tags <https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html>`_.

Ansible forks
-------------

The default ``MaxSessions`` setting for the OpenSSH Daemon is 10. Each Ansible
fork makes use of a session. By default, Ansible sets the number of forks to
5. However, you can increase the number of forks used in order to improve
deployment performance in large environments.

Note that more than 10 forks will cause issues for any playbooks which use
``delegate_to`` or ``local_action`` in the tasks. It is recommended that the
number of forks are not raised when executing against the control plane, as
this is where delegation is most often used.

When increasing the number of Ansible forks in, particularly beyond 10,
SSH connection issues can arise due to the default sshd setting
MaxStartups 10:30:100. This setting limits the number of simultaneous
unauthenticated SSH connections to 10, after which new connection attempts
start getting dropped probabilistically — with a 30% chance initially,
increasing linearly up to 100% as the number of connections approaches 100.

The number of forks used may be changed on a permanent basis by including
the appropriate change to the ``ANSIBLE_FORKS`` in your ``.bashrc`` file.
Alternatively it can be changed for a particular playbook execution by using
the ``--forks`` CLI parameter. For example, the following executes the nova
playbook against the control plane with 10 forks, then against the compute
nodes with 50 forks.

.. code-block:: shell-session

    # openstack-ansible --forks 10 os-nova-install.yml --limit compute_containers
    # openstack-ansible --forks 50 os-nova-install.yml --limit compute_hosts

For more information about forks, please see the following references:

* Ansible `forks`_ entry for ansible.cfg

.. _forks: https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html#cmdoption-ansible-playbook-f
