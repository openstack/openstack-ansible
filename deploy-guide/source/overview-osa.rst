=======================
About OpenStack-Ansible
=======================

OpenStack-Ansible (OSA) uses the `Ansible <https://www.ansible.com/how-ansible-works>`_
IT automation engine to deploy an OpenStack environment on Ubuntu Linux.
For isolation and ease of maintenance, you can install OpenStack components
into Linux containers (LXC).

Why choose OpenStack-Ansible?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Supports the major Linux distributions Ubuntu, CentOS (WIP) and OpenSUSE
  (WIP).
* Supports the major CPU architectures x86, ppc64, s390x (WIP).
* Offers automation for upgrades between major OpenStack releases.
* Uses OpenStack defaults for each of the project roles, and provides
  extra wiring and optimised configuration when combining projects
  together.
* Does not implement its own DSL, and uses wherever possible Ansible
  directly. All the experience acquired using Ansible can be used in
  openstack-ansible, and the other way around.
* You like to use reliable, proven technology. We try to run OpenStack
  with a minimum amount of packages that are not provided by distributions
  or the OpenStack community. Less dependencies and distribution tested
  software make the project more reliable.
* You want to be able to select how to deploy on your hardware: deploy
  partially on metal, fully on metal, or fully in machine containers.

When **not** to choose OpenStack-Ansible?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If your company is already invested with other configuration management
  systems, Puppet or Chef, and does not want to use Ansible we recommend
  re-using your knowledge and experimenting with a different
  OpenStack deployment project.
* You want to deploy OpenStack with 100% application containers.
  We currently support machine containers, with lxc and we will support
  *systemd-nspawn* in the future (WIP). If you want to go 100% Docker,
  there are other projects in the OpenStack community that can
  help you.

Ansible
~~~~~~~

Ansible provides an automation platform to simplify system and application
deployment. Ansible manages systems by using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses playbooks written in the YAML language for orchestration.
For more information, see `Ansible - Intro to
Playbooks <http://docs.ansible.com/playbooks_intro.html>`_.

This guide refers to the following types of hosts:

* `Deployment host`, which runs the Ansible playbooks
* `Target hosts`, where Ansible installs OpenStack services and infrastructure
  components

Linux containers (LXC)
~~~~~~~~~~~~~~~~~~~~~~

Containers provide operating-system level virtualization by enhancing
the concept of ``chroot`` environments. Containers isolate resources and file
systems for a particular group of processes without the overhead and
complexity of virtual machines. They access the same kernel, devices,
and file systems on the underlying host and provide a thin operational
layer built around a set of rules.

The LXC project implements operating-system-level
virtualization on Linux by using kernel namespaces, and it includes the
following features:

* Resource isolation including CPU, memory, block I/O, and network, by
  using ``cgroups``
* Selective connectivity to physical and virtual network devices on the
  underlying physical host
* Support for a variety of backing stores, including Logical Volume Manager
  (LVM)
* Built on a foundation of stable Linux technologies with an active
  development and support community

Installation workflow
~~~~~~~~~~~~~~~~~~~~~

The following diagram shows the general workflow of an OpenStack-Ansible
installation.

.. figure:: figures/installation-workflow-overview.png
   :width: 100%

#. :ref:`deployment-host`
#. :ref:`target-hosts`
#. :ref:`configure`
#. :ref:`run-playbooks`
#. :ref:`verify-operation`
