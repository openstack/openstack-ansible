`Home <index.html>`_ OpenStack-Ansible Installation Guide

Installation requirements
-------------------------

The minimum software requirements for OpenStack-Ansible are well defined, but
hardware requirements will vary based on the size of the OpenStack deployment.

CPU requirements
~~~~~~~~~~~~~~~~

Compute hosts should have multi-core processors that have `hardware-assisted
virtualization extensions`_ available. These extensions provide a significant
performance boost and improve security in virtualized environments.

Infrastructure hosts should have multi-core processors for the best
performance. Some services, such as MySQL, greatly benefit from additional CPU
cores and other technologies, such as `Hyper-threading`_.

.. _hardware-assisted virtualization extensions: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization
.. _Hyper-threading: https://en.wikipedia.org/wiki/Hyper-threading

Disk requirements
~~~~~~~~~~~~~~~~~

Different hosts will have different disk space requirements based on the
services running on each host:

Deployment hosts
  10GB of disk space is sufficient for holding the OpenStack-Ansible
  repository content and additional required software.

Compute hosts
  Disk space requirements will vary depending on the total number of instances
  running on each host and the amount of disk space allocated to each instance.
  Compute hosts should have at least 100GB of disk space available at an
  absolute minimum. Deployers should consider disks that provide higher
  throughput with lower latency, such as SSD drives in a RAID array.

Storage hosts
  Hosts running the Block Storage (cinder) service often consume the most disk
  space in OpenStack environments. As with compute hosts, deployers should
  choose disks that provide the highest I/O throughput with the lowest latency
  for storage hosts. Storage hosts should contain 1TB of disk space at a
  minimum.

Infrastructure hosts
  The OpenStack control plane contains storage-intensive services, such as
  the Image (glance) service as well as MariaDB. These control plane hosts
  should have 100GB of disk space available at a minimum.

Logging hosts
  An OpenStack-Ansible deployment generates a significant amount of logging.
  Logs come from a variety of sources, including services running in
  containers, the containers themselves, and the physical hosts. Logging hosts
  need additional disk space to hold live and rotated (historical) log files.
  In addition, the storage performance must be enough to keep pace with the
  log traffic coming from various hosts and containers within the OpenStack
  environment. Deployers should reserve at least 50GB of disk space for storing
  logs on the logging hosts, but this minimum will grow as additional hosts are
  deployed.

Hosts that provide Block Storage (cinder) volumes should have logical volume
manager (LVM) support. Those hosts must have a *cinder-volumes* volume group
that OpenStack-Ansible can configure for use with cinder.

Each control plane host will run services inside LXC containers. By default,
the container filesystems are deployed onto the root filesystem of each control
plane hosts. Deployers have the option to deploy those container filesystems
into logical volumes by creating a volume group called *lxc*. OpenStack-Ansible
will create a 5GB logical volume for the filesystem of each container running
on the host.

Network requirements
~~~~~~~~~~~~~~~~~~~~

It is possible to deploy an OpenStack environment with only one physical
network interface. This works for small environments but it will cause problems
when the environment grows.

For the best performance, reliability and scalability, deployers should
consider a network configuration that contains the following features:

* Bonded network interfaces: Increases performance and/or reliability
  (dependent on bonding architecture)

* VLAN offloading: Increases performance by adding and removing VLAN tags in
  hardware, rather than in the server's main CPU

* Gigabit or 10 Gigabit Ethernet: Supports higher network speeds, which can
  also improve storage performance when using the Block Storage (cinder)
  service

* Jumbo frames: Increases network performance by allowing more data to be sent
  in each packet

Software requirements
~~~~~~~~~~~~~~~~~~~~~

All hosts within an OpenStack-Ansible environment must meet the following
minimum requirements:

* Ubuntu 14.04 LTS (Trusty Tahr)

  * OSA is tested regularly against the latest Ubuntu 14.04 LTS point
    releases
  * Linux kernel version ``3.13.0-34-generic`` or later
  * For swift storage hosts, you must enable the ``trusty-backports``
    repositories in ``/etc/apt/sources.list`` or ``/etc/apt/sources.list.d/``
    See the `Ubuntu documentation
    <https://help.ubuntu.com/community/UbuntuBackports#Enabling_Backports_Manually>`_ for more detailed instructions.

* Secure Shell (SSH) client and server that supports public key
  authentication

* Network Time Protocol (NTP) client for time synchronization (such as
  ``ntpd`` or ``chronyd``)

* Python 2.7 or later

* en_US.UTF-8 as locale

--------------

.. include:: navigation.txt
