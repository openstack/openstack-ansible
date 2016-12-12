========================
Scaling your environment
========================

This is a draft environment scaling page for the proposed OpenStack-Ansible
operations guide.

Add a new infrastructure node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While three infrastructure hosts are recommended, if further hosts are
needed in an environment, it is possible to create additional nodes.

.. warning::

   Make sure you back up your current OpenStack environment
   before adding any new nodes. See :ref:`backing-up` for more
   information.

#. Add the node to the ``infra_hosts`` stanza of the
   ``/etc/openstack_deploy/openstack_user_config.yml``

   .. code:: console

      infra_hosts:
      [...]
      NEW_infra<node-ID>:
        ip: 10.17.136.32
      NEW_infra<node-ID>:
        ip: 10.17.136.33

#. Run the ``add_host`` playbook on the deployment host.

   .. code:: console

      # cd /opt/openstack-ansible/playbooks

#. Update the inventory to add new hosts. Make sure new rsyslog
   container names are updated. Send the updated results to ``dev/null``.

   .. code:: console

      # /opt/rpc-openstack/openstack-ansible/playbooks/inventory/dynamic_inventory.py > /dev/null

#. Create the ``/root/add_host.limit`` file, which contains all new node
   host names.

   .. code:: console

      # /opt/rpc-openstack/openstack-ansible/scripts/inventory-manage.py  \
        -f /opt/rpc-openstack/openstack-ansible/playbooks/inventory/dynamic_inventory.py  \
        -l |awk -F\| '/<NEW COMPUTE NODE>/ {print $2}' |sort -u | tee /root/add_host.limit

#. Run the ``setup-everything.yml`` playbook with the
   ``limit`` argument.

   .. warning::

      Do not run the ``setup-everything.yml`` playbook
      without the ``--limit`` argument. Without ``--limit``, the
      playbook will restart all containers inside your environment.

   .. code:: console

      # openstack-ansible setup-everything.yml --limit @/root/add_host.limit
      # openstack-ansible --tags=openstack-host-hostfile setup-hosts.yml

#. Run the rpc-support playbooks.

   .. code:: console

      #  ( cd /opt/rpc-openstack/rpcd/playbooks ; openstack-ansible rpc-support.yml )

#. Generate a new impersonation token, and add that token after the
   `maas_auth_token` variable in the ``user_rpco_variables_overrides.yml``
   file.

   .. code:: console

      - Update maas_auth_token /etc/openstack_deploy/user_rpco_variables_overrides.yml

#. Run the MaaS playbook on the deployment host.

   .. code:: console

      # ( cd /opt/rpc-openstack/rpcd/playbooks ; openstack-ansible setup-maas.yml
        --limit @/root/add_host.limit )

Test new nodes
~~~~~~~~~~~~~~

After creating a new node, test that the node runs correctly by
launching a new instance. Ensure that the new node can respond to
a networking connection test through the :command:`ping` command.
Log in to your monitoring system, and verify that the monitors
return a green signal for the new node.

Add a compute host
~~~~~~~~~~~~~~~~~~

Use the following procedure to add a compute host to an operational
cluster.

#. Configure the host as a target host. See `Prepare target hosts
   <http://docs.openstack.org/developer/openstack-ansible/install-guide/targethosts.html>`_
   for more information.

#. Edit the ``/etc/openstack_deploy/openstack_user_config.yml`` file and
   add the host to the ``compute_hosts`` stanza.

   If necessary, also modify the ``used_ips`` stanza.

#. If the cluster is utilizing Telemetry/Metering (Ceilometer),
   edit the ``/etc/openstack_deploy/conf.d/ceilometer.yml`` file and add the
   host to the ``metering-compute_hosts`` stanza.

#. Run the following commands to add the host. Replace
   ``NEW_HOST_NAME`` with the name of the new host.

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible setup-hosts.yml --limit NEW_HOST_NAME
       # openstack-ansible setup-openstack.yml --skip-tags nova-key-distribute --limit NEW_HOST_NAME
       # openstack-ansible setup-openstack.yml --tags nova-key --limit compute_hosts

Remove a compute host
~~~~~~~~~~~~~~~~~~~~~

The `openstack-ansible-ops <https://git.openstack.org/cgit/openstack/openstack-ansible-ops>`_
repository contains a playbook for removing a compute host from an
OpenStack-Ansible environment.
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

Recover a Compute node failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following procedure addresses Compute node failure if shared storage
is used.

   .. note::

      If shared storage is not used, data can be copied from the
      ``/var/lib/nova/instances`` directory on the failed Compute node
      ``${FAILED_NODE}`` to another node ``${RECEIVING_NODE}``\ before
      performing the following procedure. Please note this method is
      not supported.

   #. Re-launch all instances on the failed node.

   #. Invoke the MySQL command line tool

   #. Generate a list of instance UUIDs hosted on the failed node:

      .. code::

         mysql> select uuid from instances where host = '${FAILED_NODE}' and deleted = 0;

   #. Set instances on the failed node to be hosted on a different node:

      .. code::

         mysql> update instances set host ='${RECEIVING_NODE}' where host = '${FAILED_NODE}' \
         and deleted = 0;

   #. Reboot each instance on the failed node listed in the previous query
      to regenerate the XML files:

      .. code::

         # nova reboot —hard $INSTANCE_UUID

      #. Find the volumes to check the instance has successfully booted and is
         at the login  :

      .. code::

         mysql> select nova.instances.uuid as instance_uuid, cinder.volumes.id \
         as voume_uuid, cinder.volumes.status, cinder.volumes.attach_status, \
         cinder.volumes.mountpoint, cinder.volumes,display_name from \
         cinder.volumes inner join nova.instances on cinder.volumes.instance_uuid=nova.instances.uuid \
         where nova.instances.host = '${FAILED_NODE}';

      #. If rows are found, detach and re-attach the volumes using the values
         listed in the previous query:

      .. code::

         # nova volume-detach $INSTANCE_UUID $VOLUME_UUID && \
         nova volume-attach $INSTANCE_UUID $VOLUME_UUID $VOLUME_MOUNTPOINT

      #. Rebuild or replace the failed node as described in `Adding a Compute
         node <compute-add-node.html>`_
