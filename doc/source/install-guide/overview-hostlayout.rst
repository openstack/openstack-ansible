`Home <index.html>`_ OpenStack-Ansible Installation Guide

Host layout
-----------

The recommended layout contains a minimum of five hosts (or servers).

-  Three control plane infrastructure hosts

-  One logging infrastructure host

-  One compute host

To use the optional Block Storage (cinder) service, a sixth host is
recommended. Block Storage hosts require an LVM volume group named
*cinder-volumes*. See `the section called "Installation
requirements" <overview-requirements.html>`_ and `the section
called "Configuring LVM" <targethosts-configlvm.html>`_ for more information.

The hosts are called *target hosts* because Ansible deploys the OSA
environment within these hosts. The OSA environment also recommends a
*deployment host* from which Ansible orchestrates the deployment
process. One of the target hosts can function as the deployment host.

At least one load balancer **must** be used to manage the traffic among
the target hosts. This can be any load balance of any type (hardware, haproxy,
etc). While OpenStack-Ansible has playbooks and roles for deploying haproxy
it's recommended for deployers to use physical load balancers when moving to
production.

Infrastructure Control Plane target hosts contain the following
services:

-  Infrastructure:

   -  Galera

   -  RabbitMQ

   -  Memcached

   -  Logging

-  OpenStack:

   -  Identity (keystone)

   -  Image service (glance)

   -  Compute management (nova)

   -  Networking (neutron)

   -  Orchestration (heat)

   -  Dashboard (horizon)

Infrastructure Logging target hosts contain the following services:

-  Rsyslog

-  Logstash

-  Elasticsearch with Kibana

Compute target hosts contain the following services:

-  Compute virtualization

-  Logging

(Optional) Storage target hosts contain the following services:

-  Block Storage scheduler

-  Block Storage volumes


**Figure 2.1. Host Layout Overview**

.. image:: figures/environment-overview.png

--------------

.. include:: navigation.txt
