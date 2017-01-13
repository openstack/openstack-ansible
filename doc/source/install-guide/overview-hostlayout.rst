`Home <index.html>`_ OpenStack-Ansible Installation Guide

===========
Host layout
===========

We recommend a layout that contains a minimum of five hosts (or servers):

-  Three control plane infrastructure hosts

-  One logging infrastructure host

-  One compute host

If using the optional Block Storage (cinder) service, we recommend
the use of a sixth host. Block Storage hosts require an LVM volume group named
``cinder-volumes``. See `Installation
requirements <http://docs.openstack.org/developer/openstack-ansible/mitaka/install-guide/overview-requirements.html>`_ and
`Configuring LVM <http://docs.openstack.org/developer/openstack-ansible/mitaka/install-guide/targethosts-prepare.html#configuring-lvm>`_
for more information.

The hosts are called target hosts because Ansible deploys the OSA
environment within these hosts. We recommend a
deployment host from which Ansible orchestrates the deployment
process. One of the target hosts can function as the deployment host.

Use at least one load balancer to manage the traffic among
the target hosts. You can use any type of load balancer such as a hardware
appliance or HAProxy. We recommend using physical load balancers for
production environments.

Infrastructure Control Plane target hosts contain the following
services:

-  Infrastructure:

   -  Galera

   -  RabbitMQ

   -  Memcached

   -  Logging

   -  Repository

-  OpenStack:

   -  Identity (keystone)

   -  Image service (glance)

   -  Compute management (nova)

   -  Networking (neutron)

   -  Orchestration (heat)

   -  Dashboard (horizon)

Infrastructure Logging target hosts contain the following services:

-  Rsyslog

Compute target hosts contain the following services:

-  Compute virtualization

-  Logging

(Optional) Storage target hosts contain the following services:

-  Block Storage scheduler

-  Block Storage volumes


**Figure 1.1. Host Layout Overview**

.. image:: figures/environment-overview.png

--------------

.. include:: navigation.txt
