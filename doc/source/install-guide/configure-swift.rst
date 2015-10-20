`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Object Storage service (optional)
-------------------------------------------------

.. toctree::

   configure-swift-overview.rst
   configure-swift-devices.rst
   configure-swift-config.rst
   configure-swift-glance.rst
   configure-swift-add.rst
   configure-swift-policies.rst

Object Storage (swift) is a multi-tenant object storage system. It is
highly scalable, can manage large amounts of unstructured data, and
provides a RESTful HTTP API.

The following procedure describes how to set up storage devices and
modify the Object Storage configuration files to enable Object Storage
usage.

#. `The section called "Configure and mount storage
   devices" <configure-swift-devices.html>`_

#. `The section called "Configure an Object Storage
   deployment" <configure-swift-config.html>`_

#. Optionally, allow all Identity users to use Object Storage by setting
   ``swift_allow_all_users`` in the ``user_variables.yml`` file to
   ``True``. Any users with the ``_member_`` role (all authorized
   Identity (keystone) users) can create containers and upload objects
   to Object Storage.

   If this value is ``False``, then by default, only users with the
   admin or swiftoperator role are allowed to create containers or
   manage tenants.

   When the backend type for the Image Service (glance) is set to
   ``swift``, the Image Service can access the Object Storage cluster
   regardless of whether this value is ``True`` or ``False``.

--------------

.. include:: navigation.txt
