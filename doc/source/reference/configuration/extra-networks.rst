Adding extra network to container
=================================

In some cases it may be useful to have an ability to add extra network
interface for some container group (or just a single container). As an example
this can be used for applying known fixed IP address from another network for
Designate service. We will show futher configuration based on this example.
Let's assume, that this network is 10.0.20.0/24 which is reachable through
`br-dns` interface.

To add new interface with that network into dessignate containers, we need to
do several actions in ``openstack_user_config.yml``.

.. note::

   You may find detailed example of `openstack_user_config.yml` configuration
   in section :ref:`openstack-user-config-reference`.

* Add this network in ``cidr_networks``:

    .. code-block:: yaml

      cidr_networks:
        container: 172.29.236.0/22
        tunnel: 172.29.240.0/22
        storage: 172.29.244.0/22
        designate: 10.0.20.0/24

* Describe network in ``provider_networks``:

    .. code-block:: yaml

        global_overrides:
          provider_networks:
            - network:
              container_bridge: "br-dns"
              container_type: "veth"
              container_interface: "eth5"
              ip_from_q: "designate"
              type: "veth"
              group_binds:
                - dnsaas_hosts

* Define override for containers

    .. note::

      Adding gateway key will create default route inside container through it

    .. code-block:: yaml

        dnsaas_hosts:
          aio1:
            ip: 172.29.236.100
            container_vars:
              container_extra_networks:
                dns_address:
                  bridge: br-dns
                  interface: eth5
                  address: 10.0.20.100
                  netmask: 255.255.255.0
                  gateway: 10.0.20.1


Using SR-IOV interfaces in containers
=====================================

For some deployments it might be required to passthrough devices directly to
containers, for example, when SR-IOV is used or devices can't be bridged
(ie with `IPoIB <https://www.kernel.org/doc/html/latest/infiniband/ipoib.html>`)

You would need to manually map physical interfaces to specific containers.
This also assumes, that same interface name is present on all containers and
it is consistent and present before LXC startup.

Below as an example we will try using IB interfaces for storage network
and pass them inside containers that require storage connectivity.
For that you need describe connections in ``provider_networks``
inside `openstack_user_config.yml` configuration:

    .. code-block:: yaml

      global_overrides:
        provider_networks:
          - network:
              container_bridge: "ib1"
              container_type: "phys"
              container_interface: "ib1"
              ip_from_q: "storage"
              type: "raw"
              group_binds:
                - cinder_volume
          - network:
              container_bridge: "ib3"
              container_type: "phys"
              container_interface: "ib3"
              ip_from_q: "storage"
              type: "raw"
              group_binds:
               - glance_api
          - network:
              container_bridge: "ib5"
              container_type: "phys"
              container_interface: "ib5"
              ip_from_q: "storage"
              type: "raw"
              group_binds:
                - gnocchi_api
