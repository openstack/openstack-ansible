Using OpenStack-Ansible within your project
===========================================

Including OpenStack-Ansible in your project
-------------------------------------------

Including the openstack-ansible repository within another project can be
done in several ways:

- A git submodule pointed to a released tag.
- A script to automatically perform a git checkout of OpenStack-Ansible.

When including OpenStack-Ansible in a project, consider using a parallel
directory structure as shown in the ``ansible.cfg`` files section.

Also note that copying files into directories such as ``env.d`` or
``conf.d`` should be handled via some sort of script within the extension
project.

Including OpenStack-Ansible with your Ansible structure
-------------------------------------------------------

You can create your own playbook, variable, and role structure while still
including the OpenStack-Ansible roles and libraries by setting environment
variables or by adjusting ``/usr/local/bin/openstack-ansible.rc``.

The relevant environment variables for OpenStack-Ansible are as follows:

``ANSIBLE_LIBRARY``
  This variable should point to
  ``/etc/ansible/plugins/library``. Doing so allows roles and
  playbooks to access OpenStack-Ansible's included Ansible modules.
``ANSIBLE_ROLES_PATH``
  This variable should point to
  ``/etc/ansible/roles`` by default. This allows Ansible to
  properly look up any OpenStack-Ansible roles that extension roles
  may reference.
``ANSIBLE_INVENTORY``
  This variable should point to
  ``openstack-ansible/inventory/dynamic_inventory.py``. With this setting,
  extensions have access to the same dynamic inventory that
  OpenStack-Ansible uses.

The paths to the ``openstack-ansible`` top level directory can be
relative in this file.

Consider this directory structure::

    my_project
    |
    |- custom_stuff
    |  |
    |  |- playbooks
    |- openstack-ansible
    |  |
    |  |- playbooks

The environment variables set would use
``../openstack-ansible/playbooks/<directory>``.

.. _extend_osa_roles:

Adding new or overriding roles in your OpenStack-Ansible installation
---------------------------------------------------------------------

By default OpenStack-Ansible uses its `ansible-role-requirements`_ file
to fetch the roles it requires for the installation process.

The roles will be fetched into the standard ``ANSIBLE_ROLES_PATH``,
which defaults to ``/etc/ansible/roles``.

``ANSIBLE_ROLE_FILE`` is an environment variable pointing to
the location of a YAML file which ansible-galaxy can consume,
specifying which roles to download and install.
The default value for this is ``ansible-role-requirements.yml``.

You can override the ansible-role-requirement file used by defining
the environment variable ``ANSIBLE_ROLE_FILE`` before running the
``bootstrap-ansible.sh`` script.

.. _ansible-role-requirements: https://opendev.org/openstack/openstack-ansible/src/ansible-role-requirements.yml


