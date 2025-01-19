.. _haproxy-in-lxc:

========================================
HAProxy and Keepalived in LXC containers
========================================

There can be a usecase where you might want to run HAProxy and
Keepalived inside LXC containers. For instance, running these
services on bare metal assumes that a default route for hosts
should be set towards a public network. This scenario might be
un-preferable for some deployments, especially in cases where
you do not have standalone Load-Balancing hosts, but they're
co-located with other infra services instead.

Inventory overrides
~~~~~~~~~~~~~~~~~~~

In order to tell dynamic_inventory to generate a set of containers
for haproxy, you need to create a file
``/etc/openstack_deploy/env.d/haproxy.yml`` with the following content:

.. literalinclude:: ../../../../etc/openstack_deploy/env.d/haproxy.yml.container.example


Defining host networking
~~~~~~~~~~~~~~~~~~~~~~~~

In order to make a public network available, you need to ensure having a
corresponsive bridge on your hosts to which HAProxy containers will be plugged
in with one side of a veth pair.
The bridge should also contain a VLAN interface providing "public"
connectivity.

You can create a bridge manually or leverage our systemd_networkd role which
is capable of configuring required networking on hosts.

For the example below, let's name our bridge ``br-public-api`` and public vlan
with ID ``40``. In your ``user_variables.yml`` define the following variables:

.. code:: yaml


  _systemd_networkd_generic_devices:
    - NetDev:
        Name: bond0
        Kind: bond
      Bond:
        Mode: 802.3ad
        TransmitHashPolicy: layer3+4
        LACPTransmitRate: fast
        MIIMonitorSec: 100
      filename: 05-generic-bond0

  _systemd_networkd_public_api_devices:
    - NetDev:
        Name: vlan-public-api
        Kind: vlan
      VLAN:
        Id: 40
      filename: 10-openstack-vlan-public-api
    - NetDev:
        Name: br-public-api
        Kind: bridge
      Bridge:
        ForwardDelaySec: 0
        HelloTimeSec: 2
        MaxAgeSec: 12
        STP: off
      filename: 11-openstack-br-public-api

  openstack_hosts_systemd_networkd_devices: |-
    {% set devices = [] %}
    {% if is_metal %}
    {%   set _ = devices.extend(_systemd_networkd_generic_devices) %}
    {%   if inventory_hostname in groups['haproxy_hosts'] %}
    {%     set _ = devices.extend(_systemd_networkd_public_api_devices) %}
    {%   endif %}
    {% endif %}
    {{ devices }}

  _systemd_networkd_bonded_networks:
    - interface: ens3
      filename: 05-generic-ens3
      bond: bond0
      link_config_overrides:
        Match:
          MACAddress: df:25:83:e1:77:c8
    - interface: ens6
      filename: 05-generic-ens6
      bond: bond0
      link_config_overrides:
        Match:
          MACAddress: df:25:83:e1:77:c9
    - interface: bond0
      filename: 05-general-bond0
      vlan:
        - vlan-public-api

  _systemd_networkd_public_api_networks:
    - interface: "vlan-public-api"
      bridge: "br-public-api"
      filename: 10-openstack-vlan-public-api
    - interface: "br-public-api"
      filename: "11-openstack-br-public-api"

  openstack_hosts_systemd_networkd_networks: |-
    {% set networks = [] %}
    {% if is_metal %}
    {%   set _ = networks.extend(_systemd_networkd_bonded_networks) %}
    {%   if inventory_hostname in groups['haproxy_hosts'] %}
    {%     set _ = networks.extend(_systemd_networkd_public_api_networks) %}
    {%   endif %}
    {% endif %}
    {{ networks }}


Defining container networking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In case of deploying HAProxy inside LXC you need to ensure connectivity
with a public network and that ``haproxy_bind_external_lb_vip_address``
will be present inside the container as well as ``external_lb_vip_address``
is reachable.

For that we need to do the following series of changes in the
``openstack_user_config.yml`` file.

#. In ``cidr_networks`` add a network which should be used as "public" network
   for accessing APIs. For example we will be using `203.0.113.128/28`:

  .. code:: yaml

    cidr_networks:
      ...
      public_api: 203.0.113.128/28

#. In ``used_ips`` you need to reserve IP address for your gateway and
   ``haproxy_keepalived_external_vip_cidr``/``external_lb_vip_address``

    .. code:: yaml

      used_ips:
        ...
        - "203.0.113.129"
        - "203.0.113.140-203.0.113.142"


#. In ``provider_networks`` you need to define a new container network and
   assign it to HAproxy group.

    .. code:: yaml

      global_overrides:
        ...
        provider_networks:
          ...
          - network:
            group_binds:
              - haproxy
            type: "raw"
            container_bridge: "br-public-api"
            container_interface: "eth20"
            container_type: "veth"
            ip_from_q: public_api
            static_routes:
              - cidr: 0.0.0.0/0
                gateway: 203.0.113.129

While these are all changes, that need to be done in
``openstack_user_config.yml``, there is one more override that needs to be
applied.

As you might have spotted, we are defining a default route for the container
through eth20. However, by default all containers have their default route
through eth0, which is a local LXC bridge where address is recieved through
DHCP.
In order to avoid a conflict, you need to ensure that the default route will not
be set for eth0 inside the container. For that, create a file
`/etc/openstack_deploy/group_vars/haproxy` with the following content:

.. literalinclude:: ../../../../etc/openstack_deploy/group_vars/haproxy/lxc_network.yml.example


Configuring HAProxy binding inside containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As IP provisioning is quite random inside containers, it may not always be
handy to bind HAProxy to a specific IP address. If that's the case, you can
bind HAProxy to an interface instead, since we always know the interface names
inside containers. With that keepalived public/internal VIPs are supposed to
be added in ``used_ips``, so you still can define them freely.

Example bellow shows a possible content in ``user_variables.yml``:

.. code:: yaml

    haproxy_bind_external_lb_vip_interface: eth20
    haproxy_bind_internal_lb_vip_interface: eth1
    haproxy_bind_external_lb_vip_address: "*"
    haproxy_bind_internal_lb_vip_address: "*"
    haproxy_keepalived_external_vip_cidr: 203.0.113.140/32
    haproxy_keepalived_internal_vip_cidr: 172.29.236.9/32
    haproxy_keepalived_external_interface: "{{ haproxy_bind_external_lb_vip_interface }}"
    haproxy_keepalived_internal_interface: "{{ haproxy_bind_internal_lb_vip_interface }}"

Alternatively, you can detect IPs used inside your containers to configure
haproxy binds. This can be done by reffering to ``container_networks`` mapping:

.. code:: yaml

    haproxy_bind_external_lb_vip_address: "{{ container_networks['public_api_address']['address'] }}"
    haproxy_bind_internal_lb_vip_address: "{{ container_networks['management_address']['address'] }}"


Creating containers
~~~~~~~~~~~~~~~~~~~

Once all steps above are accomplished, it's time to create our new haproxy
containers. For that run the following command:

.. code:: shell

    # openstack-ansible playbooks/lxc-containers-create.yml --limit haproxy,lxc_hosts
