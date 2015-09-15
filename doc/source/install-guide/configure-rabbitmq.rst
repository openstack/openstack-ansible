`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring RabbitMQ (optional)
-------------------------------

RabbitMQ provides the messaging broker for various OpenStack services.  The
openstack-ansible project configures a plaintext listener on port 5672 and
a SSL/TLS encrypted listener on port 5671.

Customizing the RabbitMQ deployment is done within
``/etc/openstack_deploy/user_variables.yml``.

Securing RabbitMQ communication with SSL certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The openstack-ansible project provides the ability to secure RabbitMQ
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

--------------

.. include:: navigation.txt
