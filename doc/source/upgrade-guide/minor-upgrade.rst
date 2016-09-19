.. _minor-upgrades:

==============
Minor upgrades
==============

.. note:: To avoid issues and simplify troubleshooting during an upgrade,
          first disable the security hardening role by setting your
          variable ``apply_security_hardening`` to ``False`` in the
          :file:`user_variables.yml` file.

A minor upgrade typically requires the following steps:

#. Change directory into the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Ensure your OpenStack-Ansible code is on the latest
   |current_release_formal_name| tagged release:

   .. parsed-literal::

      # git checkout |latest_tag|

#. Update all the dependent roles to the latest version:

   .. code-block:: console

      # ./scripts/bootstrap-ansible.sh

#. Change into the playbooks directory:

   .. code-block:: console

      # cd playbooks

#. Update the hosts:

   .. code-block:: console

      # openstack-ansible setup-hosts.yml

#. Update the infrastructure:

   .. code-block:: console

      # openstack-ansible -e rabbitmq_upgrade=true \
      setup-infrastructure.yml

#. Update all OpenStack services:

   .. code-block:: console

      # openstack-ansible setup-openstack.yml

.. note::

   Scope upgrades to specific OpenStack components by
   executing each of the component playbooks using groups.

For example:

#. Update only the Compute hosts:

   .. code-block:: console

      # openstack-ansible os-nova-install.yml --limit nova_compute

#. Update only a single Compute host:

   .. note::

      Skipping the ``nova-key`` tag is necessary as the keys on
      all Compute hosts will not be gathered.

   .. code-block:: console

      # openstack-ansible os-nova-install.yml --limit <node-name> \
          --skip-tags 'nova-key'

To see which hosts belong to which groups, the
``inventory-manage.py`` script shows all groups and their hosts.
For example:

#. Change directory into the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Show all groups and which hosts belong to them:

   .. code-block:: console

      # ./scripts/inventory-manage.py -G

#. Show all hosts and which groups they belong:

   .. code-block:: console

      # ./scripts/inventory-manage.py -g

To see which hosts a playbook will execute against, and to see which
tasks will execute.

#. Change directory into the repository clone playbooks directory:

   .. code-block:: console

      # cd /opt/openstack-ansible/playbooks

#. See the hosts in the ``nova_compute`` group which a playbook executes
   against:

   .. code-block:: console

      # openstack-ansible os-nova-install.yml --limit nova_compute \
                                              --list-hosts

#. See the tasks which will be executed on hosts in the ``nova_compute`` group:

   .. code-block:: console

     # openstack-ansible os-nova-install.yml --limit nova_compute \
                                             --skip-tags 'nova-key' \
                                             --list-tasks
