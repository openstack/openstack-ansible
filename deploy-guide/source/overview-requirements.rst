Software requirements
~~~~~~~~~~~~~~~~~~~~~

Ensure that all hosts within the OpenStack-Ansible (OSA) environment meet the
following minimum requirements:

* Debian

  * Debian 12 (bookworm)

* Ubuntu

  * Ubuntu 24.04 LTS (Noble Numbat)

* Secure Shell (SSH) client and server that support public key
  authentication

* Python 3.11.*x* or 3.12.*x*

* en_US.UTF-8 as the locale

CPU recommendations
~~~~~~~~~~~~~~~~~~~

* Compute hosts should have multicore processors with `hardware-assisted
  virtualization extensions`_. These extensions provide a
  significant performance boost and improve security in virtualized
  environments.

* Infrastructure (control plane) hosts should have multicore processors for
  best performance. Some services, such as MariaDB, benefit from
  additional CPU cores and other technologies, such as `Hyper-threading`_.

.. _hardware-assisted virtualization extensions: https://en.wikipedia.org/wiki/Hardware-assisted_virtualization
.. _Hyper-threading: https://en.wikipedia.org/wiki/Hyper-threading

Storage/disk recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Different hosts have different disk space requirements based on the
services running on each host:

Deployment hosts
----------------

A minimum of ``10 GB`` of disk space is sufficient for holding the
OpenStack-Ansible repository content and additional required software.

Compute hosts
-------------

Disk space requirements depend on the total number of instances
running on each host and the amount of disk space allocated to each instance.

.. tip ::

   Consider disks that provide higher I/O throughput with lower latency,
   such as SSD drives in a RAID array.

Storage hosts
-------------

Hosts running the Block Storage (cinder) service often consume the most disk
space in OpenStack environments.

.. tip ::

   As with Compute hosts, choose disks that provide the highest
   I/O throughput with the lowest latency.

OpenStack-Ansible is able to deploy Cinder with a series of different
backends and uses Logical Volume Manager (LVM), by default.
Hosts that provide Block Storage volumes with LVM are recommended to
have a large disk space available allocated to a ``cinder-volume``
volume group, which OpenStack-Ansible can configure for use with Block Storage.

Infrastructure (control plane) hosts
------------------------------------

The OpenStack control plane contains storage-intensive services, such as the
Image service (glance), and MariaDB. These hosts must have a minimum of
``100 GB`` of disk space.

Each infrastructure (control plane) host runs services inside machine containers.
The container file systems are deployed by default on the root file system of
each control plane host. You have the option to deploy those container file
systems into logical volumes by creating a volume group called lxc.
OpenStack-Ansible creates a 5 GB logical volume for the file system of each
container running on the host.

.. tip ::

   Other technologies leveraging copy-on-write can be used to reduce
   the disk space requirements on machine containers.


Network recommendations
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   You can deploy an OpenStack environment with only one physical
   network interface. This works for small environments, but it can cause
   problems when your environment grows.

For the best performance, reliability, and scalability in a production
environment, consider a network configuration that contains
the following features:

* Bonded network interfaces, which increase performance, reliability, or both
  (depending on the bonding architecture)

* VLAN offloading, which increases performance by adding and removing VLAN tags
  in hardware, rather than in the server's main CPU

* Gigabit or 10 Gigabit Ethernet, which supports higher network speeds and can
  also improve storage performance when using the Block Storage service

* Jumbo frames, which increase network performance by allowing more data to
  be sent in each packet
