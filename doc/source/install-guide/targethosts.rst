`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 4. Target hosts
-----------------------

.. toctree:: 

   targethosts-os.rst
   targethosts-sshkeys.rst
   targethosts-add.rst
   targethosts-configlvm.rst
   targethosts-network.rst
   targethosts-networkrefarch.rst
   targethosts-networkexample.rst


**Figure 4.1. Installation workflow**

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
