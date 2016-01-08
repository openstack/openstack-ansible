`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 3. Target hosts
-----------------------

.. toctree::

   targethosts-prepare.rst
   targethosts-network.rst
   targethosts-networkrefarch.rst
   targethosts-networkexample.rst


**Figure 3.1. Installation workflow**

.. image:: figures/workflow-targethosts.png

The OSA installation process recommends at least five target
hosts that will contain the OpenStack environment and supporting
infrastructure. On each target host, perform the following tasks:

-  Naming target hosts.

-  Install the operating system.

-  Generate and set up security measures.

-  Update the operating system and install additional software packages.

-  Create LVM volume groups.

-  Configure networking devices.

--------------

.. include:: navigation.txt
