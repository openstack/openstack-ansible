.. _pod-environment-config:

============================================================
Appendix C: Example layer 3 routed environment configuration
============================================================

Introduction
~~~~~~~~~~~~

This appendix describes an example production environment for a working
OpenStack-Ansible (OSA) deployment with high availability services where
provider networks and connectivity between physical machines are routed
(layer 3).

This example environment has the following characteristics:

* Three infrastructure (control plane) hosts
* Two compute hosts
* One NFS storage device
* One log aggregation host
* Multiple Network Interface Cards (NIC) configured as bonded pairs for each
  host
* Full compute kit with the Telemetry service (ceilometer) included,
  with NFS configured as a storage backend for the Image (glance), and Block
  Storage (cinder) services
* Static routes are added to allow communication between the Management,
  Tunnel, and Storage Networks of each pod. The gateway address is the first
  usable address within each network's subnet.

.. image:: figures/arch-layout-production.png
   :width: 100%

Network configuration
~~~~~~~~~~~~~~~~~~~~~

Network CIDR/VLAN assignments
-----------------------------

The following CIDR assignments are used for this environment.

+-----------------------------+-----------------+------+
| Network                     | CIDR            | VLAN |
+=============================+=================+======+
| POD 1 Management Network    | 172.29.236.0/24 |  10  |
+-----------------------------+-----------------+------+
| POD 1 Tunnel (VXLAN) Network| 172.29.237.0/24 |  30  |
+-----------------------------+-----------------+------+
| POD 1 Storage Network       | 172.29.238.0/24 |  20  |
+-----------------------------+-----------------+------+
| POD 2 Management Network    | 172.29.239.0/24 |  10  |
+-----------------------------+-----------------+------+
| POD 2 Tunnel (VXLAN) Network| 172.29.240.0/24 |  30  |
+-----------------------------+-----------------+------+
| POD 2 Storage Network       | 172.29.241.0/24 |  20  |
+-----------------------------+-----------------+------+
| POD 3 Management Network    | 172.29.242.0/24 |  10  |
+-----------------------------+-----------------+------+
| POD 3 Tunnel (VXLAN) Network| 172.29.243.0/24 |  30  |
+-----------------------------+-----------------+------+
| POD 3 Storage Network       | 172.29.244.0/24 |  20  |
+-----------------------------+-----------------+------+
| POD 4 Management Network    | 172.29.245.0/24 |  10  |
+-----------------------------+-----------------+------+
| POD 4 Tunnel (VXLAN) Network| 172.29.246.0/24 |  30  |
+-----------------------------+-----------------+------+
| POD 4 Storage Network       | 172.29.247.0/24 |  20  |
+-----------------------------+-----------------+------+

IP assignments
--------------

The following host name and IP address assignments are used for this
environment.

+------------------+----------------+-------------------+----------------+
| Host name        | Management IP  | Tunnel (VxLAN) IP | Storage IP     |
+==================+================+===================+================+
| lb_vip_address   | 172.29.236.9   |                   |                |
+------------------+----------------+-------------------+----------------+
| infra1           | 172.29.236.10  |                   |                |
+------------------+----------------+-------------------+----------------+
| infra2           | 172.29.239.10  |                   |                |
+------------------+----------------+-------------------+----------------+
| infra3           | 172.29.242.10  |                   |                |
+------------------+----------------+-------------------+----------------+
| log1             | 172.29.236.11  |                   |                |
+------------------+----------------+-------------------+----------------+
| NFS Storage      |                |                   | 172.29.244.15  |
+------------------+----------------+-------------------+----------------+
| compute1         | 172.29.245.10  | 172.29.246.10     | 172.29.247.10  |
+------------------+----------------+-------------------+----------------+
| compute2         | 172.29.245.11  | 172.29.246.11     | 172.29.247.11  |
+------------------+----------------+-------------------+----------------+

Host network configuration
--------------------------

Each host will require the correct network bridges to be implemented. The
following is the ``/etc/network/interfaces`` file for ``infra1``.

.. note::

   If your environment does not have ``eth0``, but instead has ``p1p1`` or
   some other interface name, ensure that all references to ``eth0`` in all
   configuration files are replaced with the appropriate name. The same
   applies to additional network interfaces.

.. literalinclude:: ../../etc/network/interfaces.d/openstack_interface.cfg.pod.example

Deployment configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Environment layout
------------------

The ``/etc/openstack_deploy/openstack_user_config.yml`` file defines the
environment layout.

For each pod, a group will need to be defined containing all hosts within that
pod.

Within defined provider networks, ``address_prefix`` is used to override the
prefix of the key added to each host that contains IP address information. This
should usually be one of either ``container``, ``tunnel``, or ``storage``.
``reference_group`` contains the name of a defined pod group and is used to
limit the scope of each provider network to that group.

Static routes are added to allow communication of provider networks between
pods.

The following configuration describes the layout for this environment.

.. literalinclude:: ../../etc/openstack_deploy/openstack_user_config.yml.pod.example

Environment customizations
--------------------------

The optionally deployed files in ``/etc/openstack_deploy/env.d`` allow the
customization of Ansible groups. This allows the deployer to set whether
the services will run in a container (the default), or on the host (on
metal).

For this environment, the ``cinder-volume`` runs in a container on the
infrastructure hosts. To achieve this, implement
``/etc/openstack_deploy/env.d/cinder.yml`` with the following content:

.. literalinclude:: ../../etc/openstack_deploy/env.d/cinder-volume.yml.container.example

User variables
--------------

The ``/etc/openstack_deploy/user_variables.yml`` file defines the global
overrides for the default variables.

For this environment, implement the load balancer on the infrastructure
hosts. Ensure that keepalived is also configured with HAProxy in
``/etc/openstack_deploy/user_variables.yml`` with the following content.

.. literalinclude:: ../../etc/openstack_deploy/user_variables.yml.prod.example
