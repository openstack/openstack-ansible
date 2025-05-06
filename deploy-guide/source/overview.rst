========
Overview
========

.. note::

   For essential background reading to help understand the service and storage
   architecture, please read the
   :dev_docs:`OpenStack-Ansible Architecture section of its reference guide <reference/architecture/index.html>`
   If you'd like to understand when OpenStack-Ansible would be a good fit for your
   organisation, please read :dev_docs:`About OpenStack-Ansible <reference/aboutosa.html>`.

This guide refers to the following types of hosts:

* `Deployment host`, which runs the Ansible playbooks
* `Target hosts`, where Ansible installs OpenStack services and infrastructure
  components

Installation workflow
=====================

The following diagram shows the general workflow of an OpenStack-Ansible
installation.

.. figure:: figures/installation-workflow-overview.png
   :width: 100%

Installation requirements and recommendations
=============================================

.. include:: overview-requirements.rst
