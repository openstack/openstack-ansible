.. _network-appendix:

================================
Appendix E: Container networking
================================

OpenStack-Ansible deploys LXC machine containers and uses linux bridging
between the container interfaces and the host interfaces to ensure that
all traffic from containers flow over multiple host interfaces. This is
to avoid traffic flowing through the default LXC bridge which is a single
host interface (and therefore could become a bottleneck), and which is
interfered with by iptables.

This appendix intends to describe how the interfaces are connected and
how traffic flows.

For more details about how the OpenStack Networking service (neutron) uses
the interfaces for instance traffic, please see the
`OpenStack Networking Guide`_.

.. _OpenStack Networking Guide: http://docs.openstack.org/networking-guide/

Bonded network interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~

A typical production environment uses multiple physical network interfaces
in a bonded pair for better redundancy and throughput. We recommend avoiding
the use of two ports on the same multi-port network card for the same bonded
interface. This is because a network card failure affects both physical
network interfaces used by the bond.

Linux bridges
~~~~~~~~~~~~~

The combination of containers and flexible deployment options require
implementation of advanced Linux networking features, such as bridges and
namespaces.

Bridges provide layer 2 connectivity (similar to switches) among
physical, logical, and virtual network interfaces within a host. After
creating a bridge, the network interfaces are virtually plugged in to
it.

OpenStack-Ansible uses bridges to connect physical and logical network
interfaces on the host to virtual network interfaces within containers.

Namespaces provide logically separate layer 3 environments (similar to
routers) within a host. Namespaces use virtual interfaces to connect
with other namespaces, including the host namespace. These interfaces,
often called ``veth`` pairs, are virtually plugged in between
namespaces similar to patch cables connecting physical devices such as
switches and routers.

Each container has a namespace that connects to the host namespace with
one or more ``veth`` pairs. Unless specified, the system generates
random names for ``veth`` pairs.

The following image demonstrates how the container network interfaces are
connected to the host's bridges and to the host's physical network interfaces:

.. image:: figures/networkcomponents.png

Network diagrams
~~~~~~~~~~~~~~~~

The following image shows how all of the interfaces and bridges interconnect
to provide network connectivity to the OpenStack deployment:

.. image:: figures/networkarch-container-external.png

OpenStack-Ansible deploys the Compute service on the physical host rather than
in a container. The following image shows how to use bridges for
network connectivity:

.. image:: figures/networkarch-bare-external.png

The following image shows how the neutron agents work with the bridges
``br-vlan`` and ``br-vxlan``. Neutron is configured to use a DHCP agent, L3
agent, and Linux Bridge agent within a ``networking-agents`` container. The
image shows how DHCP agents provide information (IP addresses and DNS servers)
to the instances, and how routing works on the image:

.. image:: figures/networking-neutronagents.png

The following image shows how virtual machines connect to the ``br-vlan`` and
``br-vxlan`` bridges and send traffic to the network outside the host:

.. image:: figures/networking-compute.png

