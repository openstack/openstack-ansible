===============
Troubleshooting
===============

This chapter is intended to help troubleshoot and resolve operational issues in
an OpenStack-Ansible deployment.

Networking
~~~~~~~~~~

Checking services
~~~~~~~~~~~~~~~~~

Restarting services
~~~~~~~~~~~~~~~~~~~

Troubleshooting Instance connectivity issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diagnose Image service issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The glance-registry handles the database operations for managing the storage
of the image index and properties. The glance-api handles the API interactions
and image store.

To troubleshoot problems or errors with the Image service, refer to
:file:`/var/log/glance-api.log` and :file:`/var/log/glance-registry.log` inside
the glance api container.

You can also conduct the following activities which may generate logs to help
identity problems:

#. Download an image to ensure that an image can be read from the store.
#. Upload an image to test whether the image is registering and writing to the
   image store.
#. Run the ``openstack image list`` command to ensure that the API and
   registry is working.

For an example and more information, see `Verify operation
<https://docs.openstack.org/newton/install-guide-ubuntu/glance-verify.html>_`.
and `Manage Images
<https://docs.openstack.org/user-guide/common/cli-manage-images.html>_`

RabbitMQ issues
~~~~~~~~~~~~~~~

Analyze RabbitMQ queues
-----------------------

.. The title should state what issue is being resolved? DC

Analyze OpenStack service logs and RabbitMQ logs
------------------------------------------------

.. The title should state what issue is being resolved? DC

Failed security hardening after host kernel upgrade from version 3.13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ubuntu kernel packages newer than version 3.13 contain a change in
module naming from ``nf_conntrack`` to ``br_netfilter``. After
upgrading the kernel, run the ``openstack-hosts-setup.yml``
playbook against those hosts. For more information, see
`OSA bug 157996 <https://bugs.launchpad.net/openstack-ansible/+bug/1579963>`_.

Cached Ansible facts issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the beginning of a playbook run, information about each host is gathered,
such as:

    * Linux distribution
    * Kernel version
    * Network interfaces

To improve performance, particularly in large deployments, you can
cache host facts and information.

OpenStack-Ansible enables fact caching by default. The facts are
cached in JSON files within ``/etc/openstack_deploy/ansible_facts``.

Fact caching can be disabled by running
``export ANSIBLE_CACHE_PLUGIN=memory``.
To set this permanently, set this variable in
``/usr/local/bin/openstack-ansible.rc``.
Refer to the Ansible documentation on `fact caching`_ for more details.

.. _fact caching: http://docs.ansible.com/ansible/playbooks_variables.html#fact-caching

Forcing regeneration of cached facts
------------------------------------

Cached facts may be incorrect if the host receives a kernel upgrade or new
network interfaces. Newly created bridges also disrupt cache facts.

This can lead to unexpected errors while running playbooks, and require cached
facts to be regenerated.

Run the following command to remove all currently cached facts for all hosts:

.. code-block:: shell-session

   # rm /etc/openstack_deploy/ansible_facts/*

New facts will be gathered and cached during the next playbook run.

To clear facts for a single host, find its file within
``/etc/openstack_deploy/ansible_facts/`` and remove it. Each host has
a JSON file that is named after its hostname. The facts for that host
will be regenerated on the next playbook run.


Failed ansible playbooks during an upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Container networking issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All LXC containers on the host have at least two virtual Ethernet interfaces:

* `eth0` in the container connects to `lxcbr0` on the host
* `eth1` in the container connects to `br-mgmt` on the host

.. note::

   Some containers, such as ``cinder``, ``glance``, ``neutron_agents``, and
   ``swift_proxy`` have more than two interfaces to support their
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
about the utility container. For example:

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

Review container networking traffic
-----------------------------------

To dump traffic on the ``br-mgmt`` bridge, use ``tcpdump`` to see all
communications between the various containers. To narrow the focus,
run ``tcpdump`` only on the desired network interface of the
containers.
