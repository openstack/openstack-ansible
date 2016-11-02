`Home <index.html>`_ OpenStack-Ansible Installation Guide

=======================
Removing a compute host
=======================

The `openstack-ansible-ops <https://git.openstack.org/cgit/openstack/openstack-ansible-ops>`_
repository contains a playbook for removing a compute host from an
OpenStack-Ansible (OSA) environment.
To remove a compute host, follow the below procedure.

.. note::

   This guide describes how to remove a compute node from an OSA environment
   completely. Perform these steps with caution, as the compute node will no
   longer be in service after the steps have been completed. This guide assumes
   that all data and instances have been properly migrated.

#. Disable all OpenStack services running on the compute node.
   This can include, but is not limited to, the ``nova-compute`` service
   and the neutron agent service.

   .. note::

     Ensure this step is performed first

  .. code-block:: console

     # Run these commands on the compute node to be removed
     # stop nova-compute
     # stop neutron-linuxbridge-agent

#. Clone the ``openstack-ansible-ops`` repository to your deployment host:

  .. code-block:: console

     $ git clone https://git.openstack.org/openstack/openstack-ansible-ops \
       /opt/openstack-ansible-ops

#. Run the ``remove_compute_node.yml`` Ansible playbook with the
   ``node_to_be_removed`` user variable set:

  .. code-block:: console

     $ cd /opt/openstack-ansible-ops/ansible_tools/playbooks
     openstack-ansible remove_compute_node.yml \
     -e node_to_be_removed="<name-of-compute-host>"

#. After the playbook completes, remove the compute node from the
   OpenStack-Ansible configuration file in
   ``/etc/openstack_deploy/openstack_user_config.yml``.
