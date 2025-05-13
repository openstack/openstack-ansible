Extending OpenStack-Ansible with additional Ansible content
===========================================================

Including OpenStack-Ansible in your project
-------------------------------------------

Including the OpenStack-Ansible repository within another project can be
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

Consider this directory structure:

.. code-block:: text

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

To completely override the ``ansible-role-requirement.yml`` file you can define
the environment variable ``ANSIBLE_ROLE_FILE`` before running the
``bootstrap-ansible.sh`` script. With this approach it is now the
responsibility of the deployer to maintain appropriate versions pins
of the Ansible roles if an upgrade is required.

If you want to extend or just partially override content of the
``ansible-role-requirements.yml`` file you can create a new config file
which path defaults to ``/etc/openstack_deploy/user-role-requirements.yml``.
This path can be overriden with another environment variable
``USER_ROLE_FILE`` which is expected to be relative to ``OSA_CONFIG_DIR``
(/etc/openstack_deploy) folder.

This file is in the same format as ``ansible-role-requirements.yml`` and can be
used to add new roles or selectively override existing ones. New roles
listed in ``user-role-requirements.yml`` will be merged with those
in ``ansible-role-requirements.yml``, and roles with matching ``name`` key
will override those in ``ansible-role-requirements.yml``. In case when
``src`` key is not defined bootstrap script will skip cloning such roles.

It is easy for a deployer to keep this file under their own version
control and out of the OpenStack-Ansible tree.

Adding new or overriding collections in your OpenStack-Ansible installation
---------------------------------------------------------------------------

Alike to roles, collections for installation are stored in
`ansible-collection-requirements`_ file. Path to this file can be overriden
through ``ANSIBLE_COLLECTION_FILE`` environmental variable.

The Victoria release of OpenStack-Ansible adds an optional new config
file which defaults to
``/etc/openstack_deploy/user-collection-requirements.yml``.

It should be in the native format of the ansible-galaxy requirements file
and can be used to add new collections to the deploy host or override versions
or source for collections defined in ``ansible-collection-requirements``.

``user-collection-requirements`` will be merged with
``ansible-collection-requirements`` using collection ``name`` as a key.
In case ``source`` is not defined in ``user-collection-requirements``,
collection installation will be skipped. This way you can skip installation
of unwanted collections.

You can override location of the ``user-collection-requirements.yml`` by
setting ``USER_COLLECTION_FILE`` environment variable before running the
``bootstrap-ansible.sh`` script. Though it is expected to be relative to
``OSA_CONFIG_DIR`` (/etc/openstack_deploy) folder.

Calling extra playbooks during the deployment
---------------------------------------------

If you install some additional deployment functionality as either a
collection or a git repository on the deploy host, it is possible
to automatically include extra playbooks at certain points during
the deployment.

The points where a hook exists to call an external playbook are as
follows:

 * ``pre_setup_hosts_hook``
 * ``post_setup_hosts_hook``
 * ``pre_setup_infrastructure_hook``
 * ``post_setup_infrastructure_hook``
 * ``pre_setup_openstack_hook``
 * ``post_setup_openstack_hook``

The hook variables should be configured in a suitable ``user_variables.yml``
file. An example calling a playbook from a collection (installed
using ``user-collection-requirements.yml``):

.. code-block:: bash

  pre_setup_hosts_hook: custom.collection.playbook

Installing extra playbooks using collections, and referencing the
playbook with its FQCN is the most robust approach to including
additional user defined playbooks.

Installing extra Python packages inside Ansible virtualenv
----------------------------------------------------------

Some Ansible collections may require presence of specific Python libraries
inside execution environment.
In order to accomplish that deployer can create ``/etc/openstack_deploy/user-ansible-venv-requirements.txt``
file with a list of Python libraries that should be installed inside virtual
environment along with Ansible during ``bootstrap-ansible.sh`` execution.

You can override the default path to ``user-ansible-venv-requirements.txt`` file
with ``USER_ANSIBLE_REQUIREMENTS_FILE`` environment variable before running the
``bootstrap-ansible.sh`` script.

Defining environment variables for deployment
---------------------------------------------

Throughout the documentation we talk a lot about different environment
variables that control behaviour of OpenStack-Ansible and Ansible iteself.

Starting with the Zed release a ``user.rc`` file can be placed in
``OSA_CONFIG_DIR`` (/etc/openstack_deploy) folder and contain any
environment variable definitions that might be needed to change the
default behaviour or any arbitrary `Ansible configuration`_ parameter.
These environment variables are general purpose and are not limited
to those understood by Ansible.

The path to this file can be changed by setting the ``OSA_USER_RC``
variable, but the ``OSA_CONFIG_DIR`` and ``OSA_USER_RC`` variables
cannot re-defined or controlled through the ``user.rc`` file.


.. _ansible-role-requirements: https://opendev.org/openstack/openstack-ansible/src/ansible-role-requirements.yml
.. _ansible-collection-requirements: https://opendev.org/openstack/openstack-ansible/src/ansible-collection-requirements.yml
.. _Ansible configuration: https://docs.ansible.com/ansible/latest/reference_appendices/config.html#environment-variables

.. _ansible-galaxy: https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#install-multiple-collections-with-a-requirements-file
