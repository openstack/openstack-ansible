`Home <index.html>`_ OpenStack-Ansible Installation Guide

=======================
About OpenStack-Ansible
=======================

OpenStack-Ansible (OSA) uses the Ansible IT automation engine to
deploy an OpenStack environment on Ubuntu Linux. OpenStack components may
be installed into Linux Containers (LXC) for isolation and ease of
maintenance.

This documentation is intended for deployers, and walks through an
OpenStack-Ansible installation for a test environment, and a production
environment.

Third-party trademarks and tradenames appearing in this document are the
property of their respective owners. Such third-party trademarks have
been printed in caps or initial caps and are used for referential
purposes only. We do not intend our use or display of other companies'
tradenames, trademarks, or service marks to imply a relationship with,
or endorsement or sponsorship of us by, these other companies.

Ansible
~~~~~~~

Ansible provides an automation platform to simplify system and application
deployment. Ansible manages systems using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses playbooks written in the YAML language for orchestration.
For more information, see `Ansible - Intro to
Playbooks <http://docs.ansible.com/playbooks_intro.html>`_.

In this guide, we refer to the host running Ansible playbooks as
the deployment host and the hosts on which Ansible installs OpenStack services
and infrastructure components as the target hosts.

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

--------------

.. include:: navigation.txt
