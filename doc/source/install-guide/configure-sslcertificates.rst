`Home <index.html>`_ OpenStack-Ansible Installation Guide

Securing services with SSL certificates
---------------------------------------

Providing secure communication between various services in an OpenStack
deployment is highly recommended in the `OpenStack Security Guide`_.

.. _OpenStack Security Guide: http://docs.openstack.org/security-guide/secure-communication.html

The openstack-ansible project currently offers the ability to configure SSL
certificates for secure communication with the following services:

* HAProxy
* Horizon
* Keystone
* RabbitMQ

For each service, deployers have the option to use self-signed certificates
generated during the deployment process or they can provide SSL certificates,
keys and CA certificates from their own trusted certificate authority.  Highly
secured environments should use trusted, user-provided, certificates for as
many services as possible.

All SSL certificate configuration should be done within
``/etc/openstack_deploy/user_variables.yml`` and not within the playbook
roles themselves.

Self-signed certificates
~~~~~~~~~~~~~~~~~~~~~~~~

Self-signed certificates make it easy to get started quickly and they ensure
data is encrypted in transit, but they don't provide a high level of trust
for highly secure environments.  The use of self-signed certificates is
currently the default in openstack-ansible.

Setting self-signed certificate subject data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The subject data of any self-signed certificate can be changed using
configuration variables.  The configuration variable for each service is
``<servicename>_ssl_self_signed_subject``.  To change the SSL certificate
subject data for HAProxy, simply make this adjustment in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    haproxy_ssl_self_signed_subject: "/C=US/ST=Texas/L=San Antonio/O=IT/CN=haproxy.example.com"

For more information about the available fields in the certificate subject,
refer to OpenSSL's documentation on the `req subcommand`_.

.. _req subcommand: https://www.openssl.org/docs/manmaster/apps/req.html

Generating and regenerating self-signed certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Self-signed certificates for each service are generated during the first run
of the playbook.  Subsequent runs of the playbook **will not** generate new SSL
certificates unless the user sets ``<servicename>_ssl_self_signed_regen`` to
``true``.

To force a self-signed certificate to regenerate you can pass the variable to
``openstack-ansible`` on the command line:

.. code-block:: shell-session

    # openstack-ansible -e "horizon_ssl_self_signed_regen=true" os-horizon-install.yml

To force a self-signed certificate to regenerate **with every playbook run**,
simply set the appropriate regeneration option to ``true``.  For example, if
you've already run the ``os-horizon`` playbook, but you want to regenerate the
self-signed certificate, set the ``horizon_ssl_self_signed_regen`` variable to
``true`` in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    horizon_ssl_self_signed_regen: true

Note that regenerating self-signed certificates will replace the existing
certificates whether they are self-signed or user-provided.


User-provided certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~

Deployers can provide their own SSL certificates, keys, and CA certificates
for added trust in highly secure environments.  Acquiring certificates from a
trusted certificate authority is outside the scope of this document, but `The
Linux Documentation Project`_ has a section called `Certificate Management`_
that explains to create your own certificate authority and sign certificates.

.. _The Linux Documentation Project: http://www.tldp.org/
.. _Certificate Management: http://www.tldp.org/HOWTO/SSL-Certificates-HOWTO/c118.html

Deploying user-provided SSL certificates is a three step process:

#. Copy your SSL certificate, key, and CA certificate to the *deployment host*
#. Specify the path to your SSL certificate, key and CA certificate in
   ``/etc/openstack_deploy/user_variables.yml``
#. Run the playbook for that service

As an example, if you wanted to deploy user-provided certificates for RabbitMQ,
start by copying those certificates to the deployment host.  Then, edit
``/etc/openstack_deploy/user_variables.yml`` and set the following three
variables:

.. code-block:: yaml

    rabbitmq_user_ssl_cert:    /tmp/example.com.crt
    rabbitmq_user_ssl_key:     /tmp/example.com.key
    rabbitmq_user_ssl_ca_cert: /tmp/ExampleCA.crt

Simply run the playbook to apply the certificates:

.. code-block:: shell-session

    # openstack-ansible rabbitmq-install.yml

The playbook will deploy your user-provided SSL certificate, key, and CA
certificate to each RabbitMQ container.

The process is identical with other services as well.  Simply replace
``rabbitmq`` in the configuration variables shown above with ``horizon``,
``haproxy``, or ``keystone``, to deploy user-provided certificates to those
services.

--------------

.. include:: navigation.txt
