`Home <index.html>`_ OpenStack-Ansible Installation Guide

Linux Containers (LXC)
----------------------

Containers provide operating-system level virtualization by enhancing
the concept of **chroot** environments, which isolate resources and file
systems for a particular group of processes without the overhead and
complexity of virtual machines. They access the same kernel, devices,
and file systems on the underlying host and provide a thin operational
layer built around a set of rules.

The Linux Containers (LXC) project implements operating system level
virtualization on Linux using kernel namespaces and includes the
following features:

-  Resource isolation including CPU, memory, block I/O, and network
   using *cgroups*.

-  Selective connectivity to physical and virtual network devices on the
   underlying physical host.

-  Support for a variety of backing stores including LVM.

-  Built on a foundation of stable Linux technologies with an active
   development and support community.

Useful commands:

-  List containers and summary information such as operational state and
   network configuration:

   .. code-block:: shell-session

       # lxc-ls --fancy

-  Show container details including operational state, resource
   utilization, and ``veth`` pairs:

   .. code-block:: shell-session

       # lxc-info --name container_name

-  Start a container:

   .. code-block:: shell-session

       # lxc-start --name container_name

-  Attach to a container:

   .. code-block:: shell-session

       # lxc-attach --name container_name

-  Stop a container:

   .. code-block:: shell-session

       # lxc-stop --name container_name

--------------

.. include:: navigation.txt
