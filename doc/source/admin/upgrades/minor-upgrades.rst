=====================
Minor version upgrade
=====================

Upgrades between minor versions of OpenStack-Ansible require
updating the repository clone to the latest minor release tag, updating
the ansible roles, and then running playbooks against the target hosts.
This section provides instructions for those tasks.

Prerequisites
~~~~~~~~~~~~~

To avoid issues and simplify troubleshooting during the upgrade, disable the
security hardening role by setting the ``apply_security_hardening`` variable
to ``False`` in the :file:`user_variables.yml` file, and
backup your openstack-ansible installation.

Execute a minor version upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A minor upgrade typically requires the following steps:

#. Change directory to the cloned repository's root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Ensure that your OpenStack-Ansible code is on the latest
   |current_release_formal_name| tagged release:

   .. parsed-literal::

      # git checkout |latest_tag|

#. Update all the dependent roles to the latest version:

   .. code-block:: console

      # ./scripts/bootstrap-ansible.sh

#. Change to the playbooks directory:

   .. code-block:: console

      # cd playbooks

#. Update the hosts:

   .. code-block:: console

      # openstack-ansible setup-hosts.yml -e package_state=latest

#. Update the infrastructure:

   .. code-block:: console

      # openstack-ansible -e rabbitmq_upgrade=true \
      setup-infrastructure.yml

#. Update all OpenStack services:

   .. code-block:: console

      # openstack-ansible setup-openstack.yml -e package_state=latest

.. note::

   You can limit upgrades to specific OpenStack components. See the following
   section for details.

Upgrade specific components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can limit upgrades to specific OpenStack components by running each of the
component playbooks against groups.

For example, you can update only the Compute hosts by running the following
command:

.. code-block:: console

   # openstack-ansible os-nova-install.yml --limit nova_compute

To update only a single Compute host, run the following command:

.. code-block:: console

   # openstack-ansible os-nova-install.yml --limit <node-name>

.. note::

   Skipping the ``nova-key`` tag is necessary so that the keys on
   all Compute hosts are not gathered.

To see which hosts belong to which groups, use the ``inventory-manage.py``
script to show all groups and their hosts. For example:

#. Change directory to the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Show all groups and which hosts belong to them:

   .. code-block:: console

      # ./scripts/inventory-manage.py -G

#. Show all hosts and the groups to which they belong:

   .. code-block:: console

      # ./scripts/inventory-manage.py -g

To see which hosts a playbook runs against, and to see which tasks are
performed, run the following commands (for example):

#. Change directory to the repository clone playbooks directory:

   .. code-block:: console

      # cd /opt/openstack-ansible/playbooks

#. See the hosts in the ``nova_compute`` group that a playbook runs against:

   .. code-block:: console

      # openstack-ansible os-nova-install.yml --limit nova_compute \
                                              --list-hosts

#. See the tasks that are executed on hosts in the ``nova_compute`` group:

   .. code-block:: console

     # openstack-ansible os-nova-install.yml --limit nova_compute \
                                             --skip-tags 'nova-key' \
                                             --list-tasks
