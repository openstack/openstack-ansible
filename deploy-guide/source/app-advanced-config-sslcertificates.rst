=======================================
Securing services with SSL certificates
=======================================

The `OpenStack Security Guide`_ recommends providing secure communication
between various services in an OpenStack deployment. The OpenStack-Ansible
project currently offers the ability to configure SSL certificates for secure
communication between services:

.. _OpenStack Security Guide: http://docs.openstack.org/security-guide/secure-communication.html

All public endpoints reside behind haproxy, resulting in the only certificate
management most environments need are those for haproxy.

When deploying with OpenStack-Ansible, you can either use self-signed certificates
that are generated during the deployment process or provide SSL certificates,
keys, and CA certificates from your own trusted certificate authority. Highly
secured environments use trusted, user-provided certificates for as
many services as possible.

.. note::

   Perform all SSL certificate configuration in
   ``/etc/openstack_deploy/user_variables.yml`` file and not in the playbooks
   or roles themselves. The variables to set which provide the path on the deployment
   node to the certificates for HAProxy configuration are:

.. code-block:: yaml

   haproxy_user_ssl_cert: /etc/openstack_deploy/ssl/example.com.crt
   haproxy_user_ssl_key: /etc/openstack_deploy/ssl/example.com.key
   haproxy_user_ssl_ca_cert: /etc/openstack_deploy/ssl/ExampleCA.crt

Self-signed certificates
~~~~~~~~~~~~~~~~~~~~~~~~

Self-signed certificates enable you to start quickly and encrypt data in
transit. However, they do not provide a high level of trust for highly
secure environments. By default, self-signed certificates are used in
OpenStack-Ansible. When self-signed certificates are used, certificate
verification is automatically disabled.

Setting subject data for self-signed certificates
-------------------------------------------------

Change the subject data of any self-signed certificate by using
configuration variables. The configuration variable for each service
is formatted as ``<servicename>_ssl_self_signed_subject``. For example, to
change the SSL certificate subject data for HAProxy, adjust the
``/etc/openstack_deploy/user_variables.yml`` file as follows:

.. code-block:: yaml

    haproxy_ssl_self_signed_subject: "/C=US/ST=Texas/L=San Antonio/O=IT/CN=haproxy.example.com"


For more information about the available fields in the certificate subject,
see the OpenSSL documentation for the `req subcommand`_.

.. _req subcommand: https://www.openssl.org/docs/manmaster/apps/req.html

Generating and regenerating self-signed certificates
----------------------------------------------------

Self-signed certificates are generated for each service during the first
run of the playbook.

To generate a new self-signed certificate for a service, you must set
the ``<servicename>_ssl_self_signed_regen`` variable to true in one of the
following ways:

* To force a self-signed certificate to regenerate, you can pass the variable
  to ``openstack-ansible`` on the command line:

  .. code-block:: shell-session

     # openstack-ansible -e "horizon_ssl_self_signed_regen=true" os-horizon-install.yml

* To force a self-signed certificate to regenerate with every playbook run,
  set the appropriate regeneration option to ``true``.  For example, if
  you have already run the ``haproxy`` playbook, but you want to regenerate
  the self-signed certificate, set the ``haproxy_ssl_self_signed_regen``
  variable to ``true`` in the ``/etc/openstack_deploy/user_variables.yml``
  file:

  .. code-block:: yaml

     haproxy_ssl_self_signed_regen: true

.. note::

   Regenerating self-signed certificates replaces the existing
   certificates whether they are self-signed or user-provided.


User-provided certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~

For added trust in highly secure environments, you can provide your own SSL
certificates, keys, and CA certificates. Acquiring certificates from a
trusted certificate authority is outside the scope of this document, but the
`Certificate Management`_  section of the Linux Documentation Project explains
how to create your own certificate authority and sign certificates.

.. _Certificate Management: http://www.tldp.org/HOWTO/SSL-Certificates-HOWTO/c118.html

Use the following process to deploy user-provided SSL certificates in
OpenStack-Ansible:

#. Copy your SSL certificate, key, and CA certificate files to the deployment
   host.
#. Specify the path to your SSL certificate, key, and CA certificate in
   the ``/etc/openstack_deploy/user_variables.yml`` file.
#. Run the playbook for that service.

For example, to deploy user-provided certificates for RabbitMQ,
copy the certificates to the deployment host, edit
the ``/etc/openstack_deploy/user_variables.yml`` file and set the following
three variables:

.. code-block:: yaml

    rabbitmq_user_ssl_cert:    /etc/openstack_deploy/ssl/example.com.crt
    rabbitmq_user_ssl_key:     /etc/openstack_deploy/ssl/example.com.key
    rabbitmq_user_ssl_ca_cert: /etc/openstack_deploy/ssl/ExampleCA.crt

Then, run the playbook to apply the certificates:

.. code-block:: shell-session

    # openstack-ansible rabbitmq-install.yml

The playbook deploys your user-provided SSL certificate, key, and CA
certificate to each RabbitMQ container.

The process is identical for the other services. Replace `rabbitmq` in
the preceding configuration variables with `horizon`, `haproxy`, or `keystone`,
and then run the playbook for that service to deploy user-provided certificates
to those services.
