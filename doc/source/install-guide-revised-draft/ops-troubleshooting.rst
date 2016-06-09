`Home <index.html>`_ OpenStack-Ansible Installation Guide

===============
Troubleshooting
===============

Host kernel upgrade from version 3.13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ubuntu kernel packages newer than version 3.13 contain a change in
module naming from ``nf_conntrack`` to ``br_netfilter``. After
upgrading the kernel, re-run the ``openstack-hosts-setup.yml``
playbook against those hosts. See `OSA bug 157996`_ for more
information.

.. _OSA bug 157996: https://bugs.launchpad.net/openstack-ansible/+bug/1579963



Container networking issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All LXC containers on the host have two virtual Ethernet interfaces:

* `eth0` in the container connects to `lxcbr0` on the host
* `eth1` in the container connects to `br-mgmt` on the host

.. note::

   Some containers, such as ``cinder``, ``glance``, ``neutron_agents``, and
   ``swift_proxy``, have more than two interfaces to support their
   functions.

Predictable interface naming
----------------------------

On the host, all virtual Ethernet devices are named based on their
container as well as the name of the interface inside the container:

   .. code-block:: shell-session

      ${CONTAINER_UNIQUE_ID}_${NETWORK_DEVICE_NAME}

As an example, an all-in-one (AIO) build might provide a utility
container called `aio1_utility_container-d13b7132`. That container
will have two network interfaces: `d13b7132_eth0` and `d13b7132_eth1`.

Another option would be to use the LXC tools to retrieve information
about the utility container:

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

The ``Link:`` lines will show the network interfaces that are attached
to the utility container.

Reviewing container networking traffic
--------------------------------------

To dump traffic on the ``br-mgmt`` bridge, use ``tcpdump`` to see all
communications between the various containers. To narrow the focus,
run ``tcpdump`` only on the desired network interface of the
containers.

Cached Ansible facts issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the beginning of a playbook run, information about each host is gathered.
Examples of the information gathered are:

    * Linux distribution
    * Kernel version
    * Network interfaces

To improve performance, particularly in large deployments, you can
cache host facts and information.

OpenStack-Ansible enables fact caching by default. The facts are
cached in JSON files within ``/etc/openstack_deploy/ansible_facts``.

Fact caching can be disabled by commenting out the ``fact_caching``
parameter in ``playbooks/ansible.cfg``. Refer to the Ansible
documentation on `fact caching`_ for more details.

.. _fact caching: http://docs.ansible.com/ansible/playbooks_variables.html#fact-caching

Forcing regeneration of cached facts
------------------------------------

Cached facts may be incorrect if the host receives a kernel upgrade or new network
interfaces. Newly created bridges also disrupt cache facts.

This can lead to unexpected errors while running playbooks, and
require that the cached facts be regenerated.

Run the following command to remove all currently cached facts for all hosts:

.. code-block:: shell-session

   # rm /etc/openstack_deploy/ansible_facts/*

New facts will be gathered and cached during the next playbook run.

To clear facts for a single host, find its file within
``/etc/openstack_deploy/ansible_facts/`` and remove it. Each host has
a JSON file that is named after its hostname. The facts for that host
will be regenerated on the next playbook run.

--------------

.. include:: navigation.txt
