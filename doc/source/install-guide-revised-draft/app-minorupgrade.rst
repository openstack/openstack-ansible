`Home <index.html>`__ OpenStack-Ansible Installation Guide

==========================
Appendix C: Minor upgrades
==========================

Upgrades between minor versions of OpenStack-Ansible are handled by
updating the repository clone to the latest tag, then executing playbooks
against the target hosts.

.. note:: In order to avoid issues and ease the troubleshooting if an
          issue appears during the upgrade, disable the security
          hardening role before running the following steps. Set your
          variable ``apply_security_hardening`` to ``False``.

A minor upgrade typically requires the execution of the following:

#. Change directory into the repository clone root directory:

   .. code-block:: shell-session

      # cd /opt/openstack-ansible

#. Update the git remotes:

   .. code-block:: shell-session

      # git fetch --all

#. Checkout the latest tag (the below tag is an example):

   .. code-block:: shell-session

      # git checkout 13.0.1

#. Update all the dependent roles to the latest versions:

   .. code-block:: shell-session

      # ./scripts/bootstrap-ansible.sh

#. Change into the playbooks directory:

   .. code-block:: shell-session

      # cd playbooks

#. Update the hosts:

   .. code-block:: shell-session

      # openstack-ansible setup-hosts.yml

#. Update the infrastructure:

   .. code-block:: shell-session

      # openstack-ansible -e rabbitmq_upgrade=true \
          setup-infrastructure.yml

#. Update all OpenStack services:

   .. code-block:: shell-session

      # openstack-ansible setup-openstack.yml

.. note::
   
   Scope upgrades to specific OpenStack components by
   executing each of the component playbooks using groups.

For example:

#. Update only the Compute hosts:

   .. code-block:: shell-session

      # openstack-ansible os-nova-install.yml --limit nova_compute

#. Update only a single Compute host:

   .. note::
   
      Skipping the ``nova-key`` tag is necessary as the keys on
      all Compute hosts will not be gathered.

   .. code-block:: shell-session

      # openstack-ansible os-nova-install.yml --limit <node-name> \
          --skip-tags 'nova-key'

To see which hosts belong to which groups, the
``inventory-manage.py`` script shows all groups and their hosts.
For example:

#. Change directory into the repository clone root directory:

   .. code-block:: shell-session

      # cd /opt/openstack-ansible

#. Show all groups and which hosts belong to them:

   .. code-block:: shell-session

      # ./scripts/inventory-manage.py -G

#. Show all hosts and which groups they belong:

   .. code-block:: shell-session

      # ./scripts/inventory-manage.py -g

To see which hosts a playbook will execute against, and to see which
tasks will execute.

#. Change directory into the repository clone playbooks directory:

   .. code-block:: shell-session

      # cd /opt/openstack-ansible/playbooks

#. See the hosts in the ``nova_compute`` group which a playbook executes against:

   .. code-block:: shell-session

      # openstack-ansible os-nova-install.yml --limit nova_compute \
                                              --list-hosts

#. See the tasks which will be executed on hosts in the ``nova_compute`` group:

   .. code-block:: shell-session

     # openstack-ansible os-nova-install.yml --limit nova_compute \
                                             --skip-tags 'nova-key' \
                                             --list-tasks

--------------

.. include:: navigation.txt
