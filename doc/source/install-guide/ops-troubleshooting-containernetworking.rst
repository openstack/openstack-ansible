`Home <index.html>`_ OpenStack-Ansible Installation Guide

Container networking issues
---------------------------

All LXC containers on the host have two virtual ethernet interfaces:

* `eth0` in the container connects to `lxcbr0` on the host
* `eth1` in the container connects to `br-mgmt` on the host

.. note::
   Some containers, such as cinder, glance, neutron_agents, and swift_proxy, have
   more than two interfaces to support their functions.`

Predictable interface naming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the host, all virtual ethernet devices are named based on their container
as well as the name of the interface inside the container:

   .. code-block:: shell-session

    ${CONTAINER_UNIQUE_ID}_${NETWORK_DEVICE_NAME}

As an example, an all-in-one (AIO) build might provide a utility container
called `aio1_utility_container-d13b7132`.  That container will have two
network interfaces: `d13b7132_eth0` and `d13b7132_eth1`.

Another option would be to use LXC's tools to retrieve information about the
utility container:

   .. code-block:: shell-session

    # lxc-info -n aio1_utility_container-d13b7132

    Name:           aio1_utility_container-d13b7132
    State:          RUNNING
    PID:            8245
    IP:             10.0.3.201
    IP:             172.29.237.204
    CPU use:        79.18 seconds
    BlkIO use:      678.26 MiB
    Memory use:     613.33 MiB
    KMem use:       0 bytes
    Link:           d13b7132_eth0
     TX bytes:      743.48 KiB
     RX bytes:      88.78 MiB
     Total bytes:   89.51 MiB
    Link:           d13b7132_eth1
     TX bytes:      412.42 KiB
     RX bytes:      17.32 MiB
     Total bytes:   17.73 MiB

The ``Link:`` lines will show the network interfaces that are attached to the
utility container.

Reviewing container networking traffic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can dump traffic on the ``br-mgmt`` bridge with ``tcpdump`` to see all
communications between various containers, but you can narrow your focus by
running ``tcpdump`` only on the network interfaces of the containers which are
experiencing a problem.

--------------

.. include:: navigation.txt
