`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the network
-----------------------

Although Ansible automates most deployment operations, networking on
target hosts requires manual configuration because it can vary
dramatically per environment. For demonstration purposes, these
instructions use a reference architecture with example network interface
names, networks, and IP addresses. Modify these values as needed for the
particular environment.

The reference architecture for target hosts contains the following
mandatory components:

-  A ``bond0`` interface using two physical interfaces. For redundancy
   purposes, avoid using more than one port on network interface cards
   containing multiple ports. The example configuration uses ``eth0``
   and ``eth2``. Actual interface names can vary depending on hardware
   and drivers. Configure the ``bond0`` interface with a static IP
   address on the host management network.

-  A ``bond1`` interface using two physical interfaces. For redundancy
   purposes, avoid using more than one port on network interface cards
   containing multiple ports. The example configuration uses ``eth1``
   and ``eth3``. Actual interface names can vary depending on hardware
   and drivers. Configure the ``bond1`` interface without an IP address.

-  Container management network subinterface on the ``bond0`` interface
   and ``br-mgmt`` bridge with a static IP address.

-  The OpenStack Networking VXLAN subinterface on the ``bond1``
   interface and ``br-vxlan`` bridge with a static IP address.

-  The OpenStack Networking VLAN ``br-vlan`` bridge on the ``bond1``
   interface without an IP address.

The reference architecture for target hosts can also contain the
following optional components:

-  Storage network subinterface on the ``bond0`` interface and
   ``br-storage`` bridge with a static IP address.

For more information, see `OpenStack-Ansible
Networking <https://github.com/openstack/openstack-ansible/blob/master/etc/network/README.rst>`_.

--------------

.. include:: navigation.txt
