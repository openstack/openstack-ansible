.. _production-network-archs:

=====================
Network architectures
=====================

OpenStack-Ansible supports a number of different network architectures,
and can be deployed using a single network interface for non-production
workloads or using multiple network interfaces or bonded interfaces for
production workloads.

The OpenStack-Ansible reference architecture segments traffic using VLANs
across multiple network interfaces or bonds. Common networks used in an
OpenStack-Ansible deployment can be observed in the following table:

+-----------------------+-----------------+------+
| Network               | CIDR            | VLAN |
+=======================+=================+======+
| Management Network    | 172.29.236.0/22 |  10  |
+-----------------------+-----------------+------+
| Overlay Network       | 172.29.240.0/22 |  30  |
+-----------------------+-----------------+------+
| Storage Network       | 172.29.244.0/22 |  20  |
+-----------------------+-----------------+------+

The ``Management Network``, also referred to as the ``container network``,
provides management of and communication between the infrastructure
and OpenStack services running in containers or on metal. The
``management network`` uses a dedicated VLAN typically connected to the
``br-mgmt`` bridge, and may also be used as the primary interface used
to interact with the server via SSH.

The ``Overlay Network``, also referred to as the ``tunnel network``,
provides connectivity between hosts for the purpose of tunnelling
encapsulated traffic using VXLAN, GENEVE, or other protocols. The
``overlay network`` uses a dedicated VLAN typically connected to the
``br-vxlan`` bridge.

The ``Storage Network`` provides segregated access to Block Storage from
OpenStack services such as Cinder and Glance. The ``storage network`` uses
a dedicated VLAN typically connected to the ``br-storage`` bridge.

.. note::

  The CIDRs and VLANs listed for each network are examples and may
  be different in your environment.

Additional VLANs may be required for the following purposes:

* External provider networks for Floating IPs and instances
* Self-service project/tenant networks for instances
* Other OpenStack services

Network interfaces
~~~~~~~~~~~~~~~~~~

Single interface or bond
------------------------

OpenStack-Ansible supports the use of a single interface or set of bonded
interfaces that carry traffic for OpenStack services as well as instances.

The following diagram demonstrates hosts using a single interface:

.. image:: ../figures/network-arch-single-interface.png
   :width: 100%
   :alt: Network Interface Layout - Single Interface

The following diagram demonstrates hosts using a single bond:

.. image:: ../figures/network-arch-single-bond.png
   :width: 100%
   :alt: Network Interface Layout - Single Bond

Each host will require the correct network bridges to be implemented.
The following is the ``/etc/network/interfaces`` file for ``infra1``
using a single bond.

.. note::

  If your environment does not have ``eth0``, but instead has ``p1p1`` or some
  other interface name, ensure that all references to ``eth0`` in all
  configuration files are replaced with the appropriate name. The same applies
  to additional network interfaces.

.. literalinclude:: ../../../../etc/network/interfaces.d/openstack_interface.cfg.singlebond.example

Multiple interfaces or bonds
----------------------------

OpenStack-Ansible supports the use of a multiple interfaces or sets of bonded
interfaces that carry traffic for OpenStack services and instances.

The following diagram demonstrates hosts using multiple interfaces:

.. image:: ../figures/network-arch-multiple-interfaces.png
   :width: 100%
   :alt: Network Interface Layout - Multiple Interfaces

The following diagram demonstrates hosts using multiple bonds:

.. image:: ../figures/network-arch-multiple-bonds.png
   :width: 100%
   :alt: Network Interface Layout - Multiple Bonds

Each host will require the correct network bridges to be implemented. The
following is the ``/etc/network/interfaces`` file for ``infra1`` using
multiple bonded interfaces.

.. note::

   If your environment does not have ``eth0``, but instead has ``p1p1`` or
   some other interface name, ensure that all references to ``eth0`` in all
   configuration files are replaced with the appropriate name. The same
   applies to additional network interfaces.

.. literalinclude:: ../../../../etc/network/interfaces.d/openstack_interface.cfg.multibond.example

Additional resources
~~~~~~~~~~~~~~~~~~~~

For more information on how to properly configure network interface files
and OpenStack-Ansible configuration files for different deployment scenarios,
please refer to the following:

* :dev_docs:`Configuring a test environment
  <user/test/example.html>`
* :dev_docs:`Configuring a homogeneous production environment
  <user/prod/example.html>`
* :dev_docs:`Using provider network groups for a heterogeneous environment
  <user/prod/provnet_groups.html>`

For network agent and container networking toplogies, please refer to the
following:

* :dev_docs:`Container networking architecture
  <reference/architecture/container-networking.html>`
