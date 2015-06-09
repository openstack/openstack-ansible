`Home <index.html>`__ OpenStack Ansible Installation Guide

Chapter 3. Deployment host
--------------------------

.. toctree:: 

   deploymenthost-os.rst
   deploymenthost-add.rst
   deploymenthost-osad.rst
   deploymenthost-sshkeys.rst


**Figure 3.1. Installation work flow**

.. image:: figures/workflow-deploymenthost.png

The OSAD installation process recommends one deployment host. The
deployment host contains Ansible and orchestrates the OSAD installation
on the target hosts. One of the target hosts, preferably one of the
infrastructure variants, can be used as the deployment host. To use a
deployment host as a target host, follow the steps in `Chapter 4,
*Target hosts* <targethosts.html>`__ on the deployment host. This
guide assumes separate deployment and target hosts.

--------------

.. include:: navigation.txt
