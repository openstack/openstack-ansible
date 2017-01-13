`Home <index.html>`_ OpenStack-Ansible Installation Guide

=======================
About OpenStack-Ansible
=======================

OpenStack-Ansible (OSA) uses the Ansible IT automation framework to
deploy an OpenStack environment on Ubuntu Linux. OpenStack components are
installed into Linux Containers (LXC) for isolation and ease of
maintenance.

This documentation is intended for deployers of the OpenStack-Ansible
deployment system who are interested in installing an OpenStack environment.

Third-party trademarks and tradenames appearing in this document are the
property of their respective owners. Such third-party trademarks have
been printed in caps or initial caps and are used for referential
purposes only. We do not intend our use or display of other companies'
tradenames, trademarks, or service marks to imply a relationship with,
or endorsement or sponsorship of us by, these other companies.

Ansible
~~~~~~~

OpenStack-Ansible Deployment uses a combination of Ansible and
Linux Containers (LXC) to install and manage OpenStack. Ansible
provides an automation platform to simplify system and application
deployment. Ansible manages systems using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses playbooks written in the YAML language for orchestration.
For more information, see `Ansible - Intro to
Playbooks <http://docs.ansible.com/playbooks_intro.html>`_.

In this guide, we refer to the host running Ansible playbooks as
the deployment host and the hosts on which Ansible installs OSA as the
target hosts.

A recommended minimal layout for deployments involves five target
hosts in total: three infrastructure hosts, one compute host, and one
logging host. All hosts will need at least one networking interface, but
we recommend multiple bonded interfaces. More information on setting up
target hosts can be found in `Host layout <http://docs.openstack.org/developer/openstack-ansible/mitaka/install-guide/overview-hostlayout.html>`_.

For more information on physical, logical, and virtual network
interfaces within hosts see `Host
networking <http://docs.openstack.org/developer/openstack-ansible/mitaka/install-guide/configure-networking.html>`_.


Linux Containers (LXC)
~~~~~~~~~~~~~~~~~~~~~~

Containers provide operating-system level virtualization by enhancing
the concept of ``chroot`` environments, which isolate resources and file
systems for a particular group of processes without the overhead and
complexity of virtual machines. They access the same kernel, devices,
and file systems on the underlying host and provide a thin operational
layer built around a set of rules.

The Linux Containers (LXC) project implements operating system level
virtualization on Linux using kernel namespaces and includes the
following features:

-  Resource isolation including CPU, memory, block I/O, and network
   using ``cgroups``.

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
