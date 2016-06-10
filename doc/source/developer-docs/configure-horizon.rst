`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Dashboard (horizon) (optional)
==============================================

Customize your horizon deployment in ``/etc/openstack_deploy/user_variables.yml``.

Securing horizon communication with SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OpenStack-Ansible project provides the ability to secure Dashboard (horizon)
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Configuring a horizon customization module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Openstack-Ansible supports deployment of a horizon `customization module`_.
After building your customization module, configure the ``horizon_customization_module`` variable
with a path to your module.

.. code-block:: yaml

   horizon_customization_module: /path/to/customization_module.py

.. _customization module: http://docs.openstack.org/developer/horizon/topics/customizing.html#horizon-customization-module-overrides

--------------

.. include:: navigation.txt
