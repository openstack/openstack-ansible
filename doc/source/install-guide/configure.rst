`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 5. Deployment configuration
-----------------------------------

.. toctree:: 

   configure-initial.rst
   configure-networking.rst
   configure-hostlist.rst
   configure-creds.rst
   configure-hypervisor.rst
   configure-glance.rst
   configure-cinder.rst
   configure-swift.rst
   configure-haproxy.rst
   configure-horizon.rst
   configure-rabbitmq.rst
   configure-ceilometer.rst
   configure-keystone.rst
   configure-openstack.rst
   configure-sslcertificates.rst
   configure-configurationintegrity.rst
   configure-federation.rst


**Figure 5.1. Installation work flow**

.. image:: figures/workflow-configdeployment.png

Ansible references a handful of files containing mandatory and optional
configuration directives. These files must be modified to define the
target environment before running the Ansible playbooks. Perform the
following tasks:

-  Configure Target host networking to define bridge interfaces and
   networks

-  Configure a list of target hosts on which to install the software

-  Configure virtual and physical network relationships for OpenStack
   Networking (neutron)

-  (Optional) Configure the hypervisor

-  (Optional) Configure Block Storage (cinder) to use the NetApp back
   end

-  (Optional) Configure Block Storage (cinder) backups.

-  (Optional) Configure Block Storage availability zones

-  Configure passwords for all services

--------------

.. include:: navigation.txt
