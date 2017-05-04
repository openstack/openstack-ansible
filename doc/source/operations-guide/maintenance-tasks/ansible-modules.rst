============================
Running ad-hoc Ansible plays
============================

Being familiar with running ad-hoc Ansible commands is helpful when
operating your OpenStack-Ansible deployment. For example, if we look at the
structure of the following ansible command:

.. code-block:: console

   $ ansible example_group -m shell -a 'hostname'

This command calls on Ansible to run the ``example_group`` using
the ``-m`` shell module with the ``-a`` argument being the hostname command.
You can substitute the group for any other groups you may have defined. For
example, if you had ``compute_hosts`` in one group and
``infra_hosts`` in  another, supply either group name and run the
commands. You can also use the ``*`` wild card if you only know the first part
of the group name, for example,  ``compute_h*``. The ``-m`` argument is for
module.

Modules can be used to control system resources, or handle the execution of
system commands. For a more information about modules , see
`Module Index <http://docs.ansible.com/ansible/modules_by_category.html>`_ and
`About Modules <http://docs.ansible.com/ansible/modules.html>`_.

If you need to run a particular command against a subset of a group, you
could use the limit flag ``-l``. For example, if a ``compute_hosts`` group
contained ``compute1``, ``compute2``, ``compute3``, and ``compute4``, and you
only needed to execute a command on ``compute1`` and ``compute4``:

.. code-block:: console

   $ ansible example_group -m shell -a 'hostname' -l compute1,compute4

.. note::

   Each host is comma-separated with no spaces.

.. note::

   Run the ad-hoc Ansible commands from the ``openstack-ansible/playbooks``
   directory.

For more information, see `Inventory <http://docs.ansible.com/ansible/intro_inventory.html>`_
and `Patterns <http://docs.ansible.com/ansible/intro_patterns.html>`_.

Running the shell module
~~~~~~~~~~~~~~~~~~~~~~~~

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

   $ ansible galera_container -m shell -a "mysql -h 127.0.0.1\
   -e 'show status like \"%wsrep_cluster_%\";'"

When a module is being used as an ad-hoc command, there are a few parameters
that are not required. For example, for the ``chdir`` command, there is no need
to :option:`chdir=/home/user ls` when running Ansible from the CLI:

.. code-block:: console

   $ ansible compute_hosts -m shell -a 'ls -la /home/user'

For more information, see `shell - Execute commands in nodes
<http://docs.ansible.com/ansible/shell_module.html>`_.

Running the copy module
~~~~~~~~~~~~~~~~~~~~~~~

The copy module copies a file on a local machine to remote locations. Use the
fetch module to copy files from remote locations to the local machine. If you
need variable interpolation in copied files, use the template module. For more
information, see `copy - Copies files to remote locations
<http://docs.ansible.com/ansible/copy_module.html>`_.

The following example shows how to move a file from your deployment host to the
``/tmp`` directory on a set of remote machines:

.. code-block:: console

   $ ansible remote_machines -m copy -a 'src=/root/FILE \
   dest=/tmp/FILE'

If you want to gather files from remote machines, use the fetch module. The
fetch module stores files locally in a file tree, organized by the hostname
from remote machines and stores them locally in a file tree, organized by
hostname.

.. note::

    This module transfers log files that might not be present, so a missing
    remote file will not be an error unless :option:`fail_on_missing` is set to
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
~~~~~~~~~~

Tags are similar to the limit flag for groups except tags are used to only run
specific tasks within a playbook. For more information on tags, see
`Tags <http://ansible-docs.readthedocs.io/zh/stable-2.0/rst/playbooks_tags.html>`_
and `Understanding ansible tags
<http://www.caphrim.net/ansible/2015/05/24/understanding-ansible-tags.html>`_.
