.. _add-compute-host:

Add a compute host
~~~~~~~~~~~~~~~~~~

Use the following procedure to add a compute host to an operational
cluster.

#. Configure the host as a target host. See the
   :deploy_guide:`target hosts configuration section <targethosts.html>`
   of the deploy guide for more information.

#. Edit the ``/etc/openstack_deploy/openstack_user_config.yml`` file and
   add the host to the ``compute_hosts`` stanza.

   If necessary, also modify the ``used_ips`` stanza.

#. If the cluster is utilizing Telemetry/Metering (ceilometer),
   edit the ``/etc/openstack_deploy/conf.d/ceilometer.yml`` file and add the
   host to the ``metering-compute_hosts`` stanza.

#. Run the following commands to add the host. Replace
   ``NEW_HOST_NAME`` with the name of the new host.

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible openstack.osa.setup_hosts --limit localhost,NEW_HOST_NAME
       # openstack-ansible openstack.osa.openstack_hosts_setup -e openstack_hosts_group=nova_compute --tags openstack_hosts-file
       # openstack-ansible openstack.osa.setup_openstack --limit localhost,NEW_HOST_NAME

   Alternatively you can try using new compute nodes deployment script
   ``/opt/openstack-ansible/scripts/add-compute.sh``.

   You can provide this script with extra tasks that will be executed
   before or right after OpenStack-Ansible roles. To do so you should
   set environment variables ``PRE_OSA_TASKS`` or ``POST_OSA_TASKS``
   with plays to run devided with semicolon:

   .. code-block:: shell-session

      # export POST_OSA_TASKS="/opt/custom/setup.yml --limit HOST_NAME;/opt/custom/tasks.yml --tags deploy"
      # /opt/openstack-ansible/scripts/add-compute.sh HOST_NAME,HOST_NAME_2

Test new compute nodes
----------------------

After creating a new node, test that the node runs correctly by
launching an instance on the new node:

.. code-block:: shell-session

  $ openstack server create --image IMAGE --flavor m1.tiny \
  --key-name KEY --availability-zone ZONE:HOST:NODE \
  --nic net-id=UUID SERVER

Ensure that the new instance can respond to a networking connection
test through the :command:`ping` command. Log in to your monitoring
system, and verify that the monitors return a green signal for the
new node.
