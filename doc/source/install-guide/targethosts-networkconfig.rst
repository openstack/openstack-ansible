=====================
Network configuration
=====================

Production environment
~~~~~~~~~~~~~~~~~~~~~~

This example allows you to use your own parameters for the deployment.

If you followed the previously proposed design, the following table shows
bridges that are to be configured on hosts.


+-------------+-----------------------+-------------------------------------+
| Bridge name | Best configured on    | With a static IP                    |
+=============+=======================+=====================================+
| br-mgmt     | On every node         | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every storage node | When component is deployed on metal |
+ br-storage  +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | When component is deployed on metal |
+ br-vxlan    +-----------------------+-------------------------------------+
|             | On every compute node | Always                              |
+-------------+-----------------------+-------------------------------------+
|             | On every network node | Never                               |
+ br-vlan     +-----------------------+-------------------------------------+
|             | On every compute node | Never                               |
+-------------+-----------------------+-------------------------------------+


Example for 3 controller nodes and 2 compute nodes
--------------------------------------------------

* VLANs:

  * Host management: Untagged/Native
  * Container management: 10
  * Tunnels: 30
  * Storage: 20

* Networks:

  * Host management: 10.240.0.0/22
  * Container management: 172.29.236.0/22
  * Tunnel: 172.29.240.0/22
  * Storage: 172.29.244.0/22

* Addresses for the controller nodes:

  * Host management: 10.240.0.11 - 10.240.0.13
  * Host management gateway: 10.240.0.1
  * DNS servers: 69.20.0.164 69.20.0.196
  * Container management: 172.29.236.11 - 172.29.236.13
  * Tunnel: no IP (because IP exist in the containers, when the components
    are not deployed directly on metal)
  * Storage: no IP (because IP exist in the containers, when the components
    are not deployed directly on metal)

* Addresses for the compute nodes:

  * Host management: 10.240.0.21 - 10.240.0.22
  * Host management gateway: 10.240.0.1
  * DNS servers: 69.20.0.164 69.20.0.196
  * Container management: 172.29.236.21 - 172.29.236.22
  * Tunnel: 172.29.240.21 - 172.29.240.22
  * Storage: 172.29.244.21 - 172.29.244.22


.. TODO Update this section. Should this information be moved to the overview
   chapter / network architecture section?

Modifying the network interfaces file
-------------------------------------

After establishing initial host management network connectivity using
the ``bond0`` interface, modify the ``/etc/network/interfaces`` file.
An example is provided on this `Link to Production Environment`_ based
on the production environment described in `host layout for production
environment`_.

Reboot your servers after modifying the network interfaces file.

.. _host layout for production environment: overview-host-layout.html#production-environment
.. _Link to Production Environment: app-targethosts-networkexample.html#production-environment

Test environment
~~~~~~~~~~~~~~~~

This example uses the following parameters to configure networking on a
single target host. See `Figure 3.2`_ for a visual representation of these
parameters in the architecture.

* VLANs:

  * Host management: Untagged/Native
  * Container management: 10
  * Tunnels: 30
  * Storage: 20

* Networks:

   * Host management: 10.240.0.0/22
   * Container management: 172.29.236.0/22
   * Tunnel: 172.29.240.0/22
   * Storage: 172.29.244.0/22

* Addresses:

   * Host management: 10.240.0.11
   * Host management gateway: 10.240.0.1
   * DNS servers: 69.20.0.164 69.20.0.196
   * Container management: 172.29.236.11
   * Tunnel: 172.29.240.11
   * Storage: 172.29.244.11

.. _Figure 3.2: targethosts-networkconfig.html#fig_hosts-target-network-containerexample

**Figure 3.2. Target host for infrastructure, networking, compute, and
storage services**

.. image:: figures/networkarch-container-external-example.png

Modifying the network interfaces file
-------------------------------------

After establishing initial host management network connectivity using
the ``bond0`` interface, modify the ``/etc/network/interfaces`` file.
An example is provided below on this `link to Test Environment`_ based
on the test environment described in `host layout for testing
environment`_.

.. _Link to Test Environment: app-targethosts-networkexample.html#test-environment
.. _host layout for testing environment: overview-host-layout.html#test-environment
