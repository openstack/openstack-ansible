`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring target host networking
----------------------------------

Edit the ``/etc/openstack_deploy/openstack_user_config.yml`` file to
configure target host networking.

#. Configure the IP address ranges associated with each network in the
   ``cidr_networks`` section:

   .. code-block:: yaml

       cidr_networks:
       # Management (same range as br-mgmt on the target hosts)
       container: CONTAINER_MGMT_CIDR
       # Tunnel endpoints for VXLAN tenant networks
       # (same range as br-vxlan on the target hosts)
       tunnel: TUNNEL_CIDR
       #Storage (same range as br-storage on the target hosts)
       storage: STORAGE_CIDR

   Replace ``*_CIDR`` with the appropriate IP address range in CIDR
   notation. For example, 203.0.113.0/24.

   Use the same IP address ranges as the underlying physical network
   interfaces or bridges configured in `the section called "Configuring
   the network" <targethosts-network.html>`_. For example, if the
   container network uses 203.0.113.0/24, the ``CONTAINER_MGMT_CIDR``
   should also use 203.0.113.0/24.

   The default configuration includes the optional storage and service
   networks. To remove one or both of them, comment out the appropriate
   network name.

#. Configure the existing IP addresses in the ``used_ips`` section:

   .. code-block:: yaml

       used_ips:
         - EXISTING_IP_ADDRESSES

   Replace ``EXISTING_IP_ADDRESSES`` with a list of existing IP
   addresses in the ranges defined in the previous step. This list
   should include all IP addresses manually configured on target hosts
   in the `the section called "Configuring the
   network" <targethosts-network.html>`_, internal load balancers,
   service network bridge, deployment hosts and any other devices
   to avoid conflicts during the automatic IP address generation process.

   Add individual IP addresses on separate lines. For example, to
   prevent use of 203.0.113.101 and 201:

   .. code-block:: yaml

       used_ips:
         - 203.0.113.101
         - 203.0.113.201

   Add a range of IP addresses using a comma. For example, to prevent
   use of 203.0.113.101-201:

   .. code-block:: yaml

       used_ips:
         - 203.0.113.101, 203.0.113.201

#. Configure load balancing in the ``global_overrides`` section:

   .. code-block:: yaml

       global_overrides:
         # Internal load balancer VIP address
         internal_lb_vip_address: INTERNAL_LB_VIP_ADDRESS
         # External (DMZ) load balancer VIP address
         external_lb_vip_address: EXTERNAL_LB_VIP_ADDRESS
         # Container network bridge device
         management_bridge: "MGMT_BRIDGE"
         # Tunnel network bridge device
         tunnel_bridge: "TUNNEL_BRIDGE"

   Replace ``INTERNAL_LB_VIP_ADDRESS`` with the internal IP address of
   the load balancer. Infrastructure and OpenStack services use this IP
   address for internal communication.

   Replace ``EXTERNAL_LB_VIP_ADDRESS`` with the external, public, or
   DMZ IP address of the load balancer. Users primarily use this IP
   address for external API and web interfaces access.

   Replace ``MGMT_BRIDGE`` with the container bridge device name,
   typically ``br-mgmt``.

   Replace ``TUNNEL_BRIDGE`` with the tunnel/overlay bridge device
   name, typically ``br-vxlan``.

#. Configure the management network in the ``provider_networks`` subsection:

   .. code-block:: yaml

         provider_networks:
           - network:
               group_binds:
                 - all_containers
                 - hosts
               type: "raw"
               container_bridge: "br-mgmt"
               container_interface: "eth1"
               container_type: "veth"
               ip_from_q: "container"
               is_container_address: true
               is_ssh_address: true

#. Configure optional networks in the ``provider_networks`` subsection. For
   example, a storage network:

   .. code-block:: yaml

         provider_networks:
           - network:
               group_binds:
                 - glance_api
                 - cinder_api
                 - cinder_volume
                 - nova_compute
               type: "raw"
               container_bridge: "br-storage"
               container_type: "veth"
               container_interface: "eth2"
               ip_from_q: "storage"

   The default configuration includes the optional storage and service
   networks. To remove one or both of them, comment out the entire
   associated stanza beginning with the *- network:* line.

#. Configure OpenStack Networking VXLAN tunnel/overlay networks in the
   ``provider_networks`` subsection:

   .. code-block:: yaml

         provider_networks:
           - network:
               group_binds:
                 - neutron_linuxbridge_agent
               container_bridge: "br-vxlan"
               container_type: "veth"
               container_interface: "eth10"
               ip_from_q: "tunnel"
               type: "vxlan"
               range: "TUNNEL_ID_RANGE"
               net_name: "vxlan"

   Replace ``TUNNEL_ID_RANGE`` with the tunnel ID range. For example,
   1:1000.

#. Configure OpenStack Networking flat (untagged) and VLAN (tagged) networks
   in the ``provider_networks`` subsection:

   .. code-block:: yaml

         provider_networks:
           - network:
               group_binds:
                 - neutron_linuxbridge_agent
               container_bridge: "br-vlan"
               container_type: "veth"
               container_interface: "eth12"
               host_bind_override: "PHYSICAL_NETWORK_INTERFACE"
               type: "flat"
               net_name: "flat"
           - network:
               group_binds:
                 - neutron_linuxbridge_agent
               container_bridge: "br-vlan"
               container_type: "veth"
               container_interface: "eth11"
               type: "vlan"
               range: VLAN_ID_RANGE
               net_name: "vlan"

   Replace ``VLAN_ID_RANGE`` with the VLAN ID range for each VLAN network.
   For example, 1:1000. Supports more than one range of VLANs on a particular
   network. For example, 1:1000,2001:3000. Create a similar stanza for each
   additional network.

   Replace ``PHYSICAL_NETWORK_INTERFACE`` with the network interface used for
   flat networking. This **must** be a physical interface on the same L2 network
   being used with the br-vlan devices. If no additional network interface is
   available, a veth pair plugged into the br-vlan bridge can provide the needed
   interface.

   Example creating a veth-pair within an existing bridge

   .. code-block:: text

         # Create veth pair, don't bomb if already exists
         pre-up ip link add br-vlan-veth type veth peer name PHYSICAL_NETWORK_INTERFACE || true
         # Set both ends UP
         pre-up ip link set br-vlan-veth up
         pre-up ip link set PHYSICAL_NETWORK_INTERFACE up
         # Delete veth pair on DOWN
         post-down ip link del br-vlan-veth || true
         bridge_ports br-vlan-veth

.. note::

   Optionally, you can add one or more static routes to interfaces within
   containers. Each route requires a destination network in CIDR notation
   and a gateway. For example:

   .. code-block:: yaml

      provider_networks:
        - network:
            group_binds:
              - glance_api
              - cinder_api
              - cinder_volume
              - nova_compute
            type: "raw"
            container_bridge: "br-storage"
            container_interface: "eth2"
            container_type: "veth"
            ip_from_q: "storage"
            static_routes:
              - cidr: 10.176.0.0/12
                gateway: 172.29.248.1

   This example adds the following content to the
   ``/etc/network/interfaces.d/eth2.cfg`` file in the appropriate
   containers:

   .. code-block:: shell-session

      post-up ip route add 10.176.0.0/12 via 172.29.248.1 || true

--------------

.. include:: navigation.txt
