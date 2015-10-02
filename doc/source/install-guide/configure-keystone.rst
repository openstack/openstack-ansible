`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring Keystone (optional)
-------------------------------

Customizing the Keystone deployment is done within
``/etc/openstack_deploy/user_variables.yml``.

Securing Keystone communication with SSL certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The openstack-ansible project provides the ability to secure Keystone
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

--------------

.. include:: navigation.txt
