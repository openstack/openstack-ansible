===========
Conventions
===========

To avoid extra configuration, a series of conventions are set into code.

Default folders locations
=========================

Ansible roles
~~~~~~~~~~~~~

The ansible roles are stored under ``/etc/ansible/roles``.

OpenStack-Ansible directory checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code is generally located into ``/opt/openstack-ansible``.

OpenStack-Ansible wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~

Our ``openstack-ansible`` cli is located in ``/usr/local/bin/openstack-ansible``.
It sources an environment variable file located in:
``/usr/local/bin/openstack-ansible.rc``.

Userspace configurations
~~~~~~~~~~~~~~~~~~~~~~~~~

All the userspace configurations are expected to be in
``/etc/openstack_deploy/``.

Ansible configuration
=====================

Ansible.cfg
~~~~~~~~~~~

There is no ``ansible.cfg`` provided with OpenStack-Ansible.
Environment variables are used to alter the default
Ansible behavior if necessary.

Ansible roles fetching
~~~~~~~~~~~~~~~~~~~~~~

Any roles defined in ``openstack-ansible/ansible-role-requirements.yml``
will be installed by the
``openstack-ansible/scripts/bootstrap-ansible.sh`` script, and fetched
into the ansible roles folder.

Inventory conventions
~~~~~~~~~~~~~~~~~~~~~

Please confer to the inventory section of this reference.
