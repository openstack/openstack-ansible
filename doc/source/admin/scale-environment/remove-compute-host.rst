Remove a compute host
~~~~~~~~~~~~~~~~~~~~~

The `OpenStack-Ansible Operator Tooling <https://opendev.org/openstack/openstack-ansible-ops>`_
repository contains a playbook for removing a compute host from an
OpenStack-Ansible environment.
To remove a compute host, follow the below procedure.

.. note::

   This guide describes how to remove a compute node from an OpenStack-Ansible
   environment completely. Perform these steps with caution, as the compute node will no
   longer be in service after the steps have been completed. This guide assumes
   that all data and instances have been properly migrated.

#. Disable all OpenStack services running on the compute node.
   This can include, but is not limited to, the ``nova-compute`` service
   and the neutron agent service:

   .. note::

     Ensure this step is performed first.

   .. code-block:: console

     # Run these commands on the compute node to be removed
     # systemctl stop nova-compute
     # systemctl stop neutron-openvswitch-agent

#. Clone the ``openstack-ansible-ops`` repository to your deployment host:

   .. code-block:: console

     $ git clone https://opendev.org/openstack/openstack-ansible-ops \
       /opt/openstack-ansible-ops

#. Run the ``remove_compute_node.yml`` Ansible playbook with the
   ``host_to_be_removed`` user variable set:

   .. code-block:: console

     $ cd /opt/openstack-ansible-ops/ansible_tools/playbooks
     openstack-ansible remove_compute_node.yml \
     -e host_to_be_removed="<name-of-compute-host>"

#. After the playbook completes, remove the compute node from the
   OpenStack-Ansible configuration file in
   ``/etc/openstack_deploy/openstack_user_config.yml``.
