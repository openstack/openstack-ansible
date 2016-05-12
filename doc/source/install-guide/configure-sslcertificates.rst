`Home <index.html>`_ OpenStack-Ansible Installation Guide

Securing services with SSL certificates
=======================================

The `OpenStack Security Guide`_ recommends providing secure communication
between various services in an OpenStack deployment.

.. _OpenStack Security Guide: http://docs.openstack.org/security-guide/secure-communication.html

The OpenStack-Ansible project currently offers the ability to configure SSL
certificates for secure communication with the following services:

* HAProxy
* Horizon
* Keystone
* RabbitMQ

For each service, you have the option to use self-signed certificates
generated during the deployment process or provide SSL certificates,
keys, and CA certificates from your own trusted certificate authority. Highly
secured environments use trusted, user-provided, certificates for as
many services as possible.

.. note::

   Conduct all SSL certificate configuration in
   ``/etc/openstack_deploy/user_variables.yml`` and not in the playbook
   roles themselves.

Self-signed certificates
~~~~~~~~~~~~~~~~~~~~~~~~

Self-signed certificates ensure you are able to start quickly and you are able to
encrypt data in transit. However, they do not provide a high level of trust
for highly secure environments. The use of self-signed certificates is
currently the default in OpenStack-Ansible. When self-signed certificates are
being used, certificate verification must be disabled using the following
user variables depending on your configuration. Add these variables
in ``/etc/openstack_deploy/user_variables.yml``.

.. code-block:: yaml

    keystone_service_adminuri_insecure: true
    keystone_service_internaluri_insecure: true

Setting self-signed certificate subject data
--------------------------------------------

Change the subject data of any self-signed certificate using
configuration variables. The configuration variable for each service is
``<servicename>_ssl_self_signed_subject``. To change the SSL certificate
subject data for HAProxy, adjust ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    haproxy_ssl_self_signed_subject: "/C=US/ST=Texas/L=San Antonio/O=IT/CN=haproxy.example.com"

For more information about the available fields in the certificate subject,
refer to OpenSSL's documentation on the `req subcommand`_.

.. _req subcommand: https://www.openssl.org/docs/manmaster/apps/req.html

Generating and regenerating self-signed certificates
----------------------------------------------------

Generate self-signed certificates for each service during the first run
of the playbook.

.. note::

   Subsequent runs of the playbook do not generate new SSL
   certificates unless you set ``<servicename>_ssl_self_signed_regen`` to
   ``true``.

To force a self-signed certificate to regenerate, you can pass the variable to
``openstack-ansible`` on the command line:

.. code-block:: shell-session

    # openstack-ansible -e "horizon_ssl_self_signed_regen=true" os-horizon-install.yml

To force a self-signed certificate to regenerate with every playbook run,
set the appropriate regeneration option to ``true``.  For example, if
you have already run the ``os-horizon`` playbook, but you want to regenerate the
self-signed certificate, set the ``horizon_ssl_self_signed_regen`` variable to
``true`` in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    horizon_ssl_self_signed_regen: true

.. note::

   Regenerating self-signed certificates replaces the existing
   certificates whether they are self-signed or user-provided.


User-provided certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can provide your own SSL certificates, keys, and CA certificates
for added trust in highly secure environments. Acquiring certificates from a
trusted certificate authority is outside the scope of this document, but the
 `Certificate Management`_  section of the Linux Documentation Project explains
how to create your own certificate authority and sign certificates.

.. _Certificate Management: http://www.tldp.org/HOWTO/SSL-Certificates-HOWTO/c118.html

Deploying user-provided SSL certificates is a three step process:

#. Copy your SSL certificate, key, and CA certificate to the deployment host.
#. Specify the path to your SSL certificate, key, and CA certificate in
   ``/etc/openstack_deploy/user_variables.yml``.
#. Run the playbook for that service.

For example, to deploy user-provided certificates for RabbitMQ,
copy the certificates to the deployment host, edit
``/etc/openstack_deploy/user_variables.yml`` and set the following three
variables:

.. code-block:: yaml

    rabbitmq_user_ssl_cert:    /tmp/example.com.crt
    rabbitmq_user_ssl_key:     /tmp/example.com.key
    rabbitmq_user_ssl_ca_cert: /tmp/ExampleCA.crt

Run the playbook to apply the certificates:

.. code-block:: shell-session

    # openstack-ansible rabbitmq-install.yml

The playbook deploys your user-provided SSL certificate, key, and CA
certificate to each RabbitMQ container.

The process is identical to the other services. Replace
``rabbitmq`` in the configuration variables shown above with ``horizon``,
``haproxy``, or ``keystone`` to deploy user-provided certificates to those
services.

--------------

.. include:: navigation.txt
