`Home <index.html>`_ OpenStack-Ansible Installation Guide

========================
Deployment configuration
========================

.. toctree::
   :maxdepth: 2

   configure-initial.rst
   configure-user-config-examples.rst
   configure-creds.rst

.. figure:: figures/installation-workflow-configure-deployment.png
   :width: 100%

   Installation workflow

Ansible references a handful of files containing mandatory and optional
configuration directives. These files must be modified to define the
target environment before running the Ansible playbooks. Configuration
tasks include:

-  target host networking to define bridge interfaces and
   networks

-  a list of target hosts on which to install the software

-  virtual and physical network relationships for OpenStack
   Networking (neutron)

-  passwords for all services

--------------

.. include:: navigation.txt
