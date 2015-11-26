`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 7. Infrastructure playbooks
-----------------------------------

.. toctree:: 

   install-infrastructure-run.rst
   install-infrastructure-verify.rst


**Figure 7.1. Installation workflow**

.. image:: figures/workflow-infraplaybooks.png

The main Ansible infrastructure playbook installs infrastructure
services and performs the following operations:

-  Install Memcached

-  Install the repository server

-  Install Galera

-  Install RabbitMQ

-  Install Rsyslog

-  Configure Rsyslog

--------------

.. include:: navigation.txt
