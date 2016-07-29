`Home <index.html>`_ OpenStack-Ansible Installation Guide

.. _configure-swift:

Configuring the Object Storage (swift) service (optional)
=========================================================

.. toctree::

   configure-swift-devices.rst
   configure-swift-config.rst
   configure-swift-glance.rst
   configure-swift-add.rst
   configure-swift-policies.rst

Object Storage (swift) is a multi-tenant Object Storage system. It is
highly scalable, can manage large amounts of unstructured data, and
provides a RESTful HTTP API.

The following procedure describes how to set up storage devices and
modify the Object Storage configuration files to enable swift
usage.

#. `The section called "Configure and mount storage
   devices" <configure-swift-devices.html>`_

#. `The section called "Configure an Object Storage
   deployment" <configure-swift-config.html>`_

#. Optionally, allow all Identity (keystone) users to use swift by setting
   ``swift_allow_all_users`` in the ``user_variables.yml`` file to
   ``True``. Any users with the ``_member_`` role (all authorized
   keystone users) can create containers and upload objects
   to Object Storage.

   If this value is ``False``, then by default, only users with the
   admin or ``swiftoperator`` role are allowed to create containers or
   manage tenants.

   When the backend type for the Image Service (glance) is set to
   ``swift``, glance can access the swift cluster
   regardless of whether this value is ``True`` or ``False``.


Overview
~~~~~~~~

Object Storage (swift) is configured using the
``/etc/openstack_deploy/conf.d/swift.yml`` file and the
``/etc/openstack_deploy/user_variables.yml`` file.

When installing swift, use the group variables in the
``/etc/openstack_deploy/conf.d/swift.yml`` file for the Ansible
playbooks. Some variables cannot
be changed after they are set, while some changes require re-running the
playbooks. The values in the ``swift_hosts`` section supersede values in
the ``swift`` section.

To view the configuration files, including information about which
variables are required and which are optional, see `Appendix A, *OSA
configuration files* <app-configfiles.html>`_.

--------------

.. include:: navigation.txt
