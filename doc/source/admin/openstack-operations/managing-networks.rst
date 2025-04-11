Managing networks
=================

Operational considerations, like compliance, can make it necessary to
manage networks. For example, adding new provider networks to the
OpenStack-Ansible managed cloud. The following sections are the most
common administrative tasks outlined to complete those tasks.

For more generic information on troubleshooting your network,
see the
`Network Troubleshooting chapter <https://wiki.openstack.org/wiki/OpsGuide/Network_Troubleshooting>`_
in the Operations Guide.

For more in-depth information on Networking, see the
`Networking Guide <https://docs.openstack.org/neutron/latest/admin/>`_.

Add provider bridges using new network interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add each provider network to your cloud to be made known
to OpenStack-Ansible and the operating system before you
can execute the necessary playbooks to complete the configuration.

OpenStack-Ansible configuration
-------------------------------

All provider networks need to be added to the OpenStack-Ansible
configuration.

Edit the file ``/etc/openstack_deploy/openstack_user_config.yml`` and
add a new block underneath the ``provider_networks`` section:

.. code-block: yaml

    - network:
        container_bridge: "br-examplenetwork"
        container_type: "veth"
        container_interface: "eth12"
        type: "vlan"
        range: "2:4094"
        net_name: "physnet2"
        group_binds:
          - neutron_openvswitch_agent

The ``container_bridge`` setting defines the physical network bridge used
to connect the veth pair from the physical host to the container.
Inside the container, the ``container_interface`` setting defines the name
at which the physical network will be made available. The
``container_interface`` setting is not required when Neutron agents are
deployed on bare metal.
Make sure that both settings are uniquely defined across their provider
networks and that the network interface is correctly configured inside your
operating system.
``group_binds`` define where this network need to attached to, to either
containers or physical hosts and is ultimately dependent on the network
stack in use. For example, Linuxbridge versus OVS.
The configuration ``range`` defines Neutron physical segmentation IDs which are
automatically used by end users when creating networks via mainly horizon and
the Neutron API.
Similar is true for the ``net_name`` configuration which defines the
addressable name inside the Neutron configuration.
This configuration also need to be unique across other provider networks.

For more information, see
:deploy_guide:`Configure the deployment <configure.html>`
in the OpenStack-Ansible Deployment Guide.

Updating the node with the new configuration
--------------------------------------------

Run the appropriate playbooks depending on the ``group_binds`` section.

For example, if you update the networks requiring a change in all
nodes with a linux bridge agent, assuming you have infra nodes named
**infra01**, **infra02**, and **infra03**, run:

.. code-block:: console

   # openstack-ansible containers-deploy.yml --limit localhost,infra01,infra01-host_containers
   # openstack-ansible containers-deploy.yml --limit localhost,infra02,infra02-host_containers
   # openstack-ansible containers-deploy.yml --limit localhost,infra03,infra03-host_containers

Then update the neutron configuration.

.. code-block:: console

   # openstack-ansible os-neutron-install.yml --limit localhost,infra01,infra01-host_containers
   # openstack-ansible os-neutron-install.yml --limit localhost,infra02,infra02-host_containers
   # openstack-ansible os-neutron-install.yml --limit localhost,infra03,infra03-host_containers

Then update your compute nodes if necessary.


Remove provider bridges from OpenStack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to adding a provider network, the removal process uses the same
procedure but in a reversed order. The Neutron ports will need to be
removed, prior to the removal of the OpenStack-Ansible configuration.

#. Unassign all Neutron floating IPs:

   .. note::

      Export the Neutron network that is about to be removed as single
      UUID.

   .. code-block:: console

      export NETWORK_UUID=<uuid>
      for p in $( neutron port-list -c id --device_owner compute:nova --network_id=${NETWORK_UUID}| awk '/([A-Fa-f0-9]+-){3}/ {print $2}' ); do
        floatid=$( neutron floatingip-list -c id --port_id=$p | awk '/([A-Fa-z0-9]+-){3}/ { print $2 }' )
        if [ -n "$floatid" ]; then
          echo "Disassociating floating IP $floatid from port $p"
          neutron floatingip-disassociate $floatid
        fi
      done

#. Remove all Neutron ports from the instances:

   .. code-block:: console

       export NETWORK_UUID=<uuid>
       for p in $( neutron port-list -c id -c device_id --device_owner compute:nova --network_id=${NETWORK_UUID}| awk '/([A-Fa-f0-9]+-){3}/ {print $2}' ); do
         echo "Removing Neutron compute port $p"
         neutron port-delete $p
       done

#. Remove Neutron router ports and DHCP agents:

   .. code-block:: console

      export NETWORK_UUID=<uuid>
      for line in $( neutron port-list -c id -c device_id --device_owner network:router_interface --network_id=${NETWORK_UUID}| awk '/([A-Fa-f0-9]+-){3}/ {print $2 "+" $4}' ); do
        p=$( echo "$line"| cut -d'+' -f1 ); r=$( echo "$line"| cut -d'+' -f2 )
        echo "Removing Neutron router port $p from $r"
        neutron router-interface-delete $r port=$p
      done

      for agent in $( neutron agent-list -c id --agent_type='DHCP Agent' --network_id=${NETWORK_UUID}| awk '/([A-Fa-f0-9]+-){3}/ {print $2}' ); do
        echo "Remove network $NETWORK_UUID from Neutron DHCP Agent $agent"
        neutron dhcp-agent-network-remove "${agent}" $NETWORK_UUID
      done

#. Remove the Neutron network:

   .. code-block:: console

      export NETWORK_UUID=<uuid>
      neutron net-delete $NETWORK_UUID

#. Remove the provider network from the ``provider_networks`` configuration
   of the OpenStack-Ansible configuration
   ``/etc/openstack_deploy/openstack_user_config.yml`` and re-run the
   following playbooks:


   .. code-block:: console

      # openstack-ansible lxc-containers-create.yml --limit infra01:infra01-host_containers
      # openstack-ansible lxc-containers-create.yml --limit infra02:infra02-host_containers
      # openstack-ansible lxc-containers-create.yml --limit infra03:infra03-host_containers
      # openstack-ansible os-neutron-install.yml --tags neutron-config

Restart a Networking agent container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Under some circumstances, configuration or temporary issues, one specific
or all neutron agents container need to be restarted.

This can be accomplished with multiple commands:

#. Example of rebooting still accessible containers.

   This example will issue a reboot to the container named with
   ``neutron_agents_container_hostname_name`` from inside:

   .. code-block:: console

      # ansible -m shell neutron_agents_container_hostname_name -a 'reboot'

#. Example of rebooting one container at a time, 60 seconds apart:

   .. code-block:: console

      # ansible -m shell neutron_agents_container -a 'sleep 60; reboot' --forks 1

#. If the container does not respond, it can be restarted from the
   physical network host:

   .. code-block:: console

      # ansible -m shell network_hosts -a 'for c in $(lxc-ls -1 |grep neutron_agents_container); do lxc-stop -n $c && lxc-start -d -n $c; done' --forks 1

