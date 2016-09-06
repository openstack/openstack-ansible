=======================
About OpenStack-Ansible
=======================

OpenStack-Ansible (OSA) uses the `Ansible IT <https://www.ansible.com/how-ansible-works>`_
automation engine to deploy an OpenStack environment on Ubuntu Linux.
For isolation and ease of maintenance, you can install OpenStack components
into Linux containers (LXC).

This documentation is intended for deployers, and walks through an
OpenStack-Ansible installation for a test and production environments.

Ansible
~~~~~~~

Ansible provides an automation platform to simplify system and application
deployment. Ansible manages systems using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses playbooks written in the YAML language for orchestration.
For more information, see `Ansible - Intro to
Playbooks <http://docs.ansible.com/playbooks_intro.html>`_.

In this guide, we refer to two types of hosts:

* The host running Ansible playbooks is the `deployment host`.
* The hosts where Ansible installs OpenStack services and infrastructure
  components are the `target host`.

Linux containers (LXC)
~~~~~~~~~~~~~~~~~~~~~~

Containers provide operating-system level virtualization by enhancing
the concept of ``chroot`` environments. These isolate resources and file
systems for a particular group of processes without the overhead and
complexity of virtual machines. They access the same kernel, devices,
and file systems on the underlying host and provide a thin operational
layer built around a set of rules.

The LXC project implements operating system level
virtualization on Linux using kernel namespaces and includes the
following features:

* Resource isolation including CPU, memory, block I/O, and network
  using ``cgroups``.
* Selective connectivity to physical and virtual network devices on the
  underlying physical host.
* Support for a variety of backing stores including LVM.
* Built on a foundation of stable Linux technologies with an active
  development and support community.


Installation workflow
~~~~~~~~~~~~~~~~~~~~~

This diagram shows the general workflow associated with an
OpenStack-Ansible installation.


.. figure:: figures/installation-workflow-overview.png
   :width: 100%

   **Installation workflow**

#. :doc:`Prepare deployment host <deploymenthost>`
#. :doc:`Prepare target hosts <targethosts>`
#. :doc:`Configure deployment <configure>`
#. :doc:`Run playbooks <installation#run-playbooks>`
#. :doc:`Verify OpenStack operation <installation>`
