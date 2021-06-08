Securing services with SSL certificates
=======================================

The `OpenStack Security Guide`_ recommends providing secure communication
between various services in an OpenStack deployment. The OpenStack-Ansible
project currently offers the ability to configure SSL certificates for secure
communication between services:

.. _OpenStack Security Guide: https://docs.openstack.org/security-guide/secure-communication.html

All public endpoints reside behind haproxy, resulting in the only certificate
management for externally visible https services are those for haproxy.
Certain internal services such as RabbitMQ also require proper SSL configuration.

When deploying with OpenStack-Ansible, you can either use self-signed
certificates that are generated during the deployment process or provide
SSL certificates, keys, and CA certificates from your own trusted
certificate authority. Highly secured environments use trusted,
user-provided certificates for as many services as possible.

.. note::

   Perform all SSL certificate configuration in
   ``/etc/openstack_deploy/user_variables.yml`` file. Do not edit the playbooks
   or roles themselves.

Openstack-Ansible uses an ansible role `ansible_role_pki`_ as a general tool to
manage and install self-signed and user provided certificates.

.. _ansible_role_pki: https://opendev.org/openstack/ansible-role-pki

Self-signed certificates
~~~~~~~~~~~~~~~~~~~~~~~~

Self-signed certificates enable you to start quickly and encrypt data in
transit. However, they do not provide a high level of trust for public
endpoints in highly secure environments. By default, self-signed certificates
are used in OpenStack-Ansible. When self-signed certificates are used,
certificate verification is automatically disabled.

Self-signed certificates can play an important role in securing internal
services within the Openstack-Ansible deployment, as they can only be issued
by the private CA associated with the deployment. Using mutual TLS between
backend services such as RabbitMQ and MariaDB with self-signed certificates
and a robust CA setup can ensure that only correctly authenticated clients
can connect to these internal services.

Generating and regenerating self-signed certificate authorities
---------------------------------------------------------------

A self-signed certificate authority is generated on the deploy host
during the first run of the playbook.

To regenerate the certificate authority you must set the
``openstack_pki_regen_ca`` variable to either the name of the root CA
or intermediate CA you wish or regenerate, or to ``true`` to regenerate
all self-signed certificate authorities.

  .. code-block:: shell-session

     # openstack-ansible -e "openstack_pki_regen_ca=ExampleCorpIntermediate" certificate-authority.yml

Take particular care not to regenerate Root or Intermediate certificate
authorities in a way that may invalidate existing server certificates in the
deployment. It may be preferable to create new Intermediate CA certificates
rather than regenerate existing ones in order to maintain existing chains of
trust.

Generating and regenerating self-signed certificates
----------------------------------------------------

Self-signed certificates are generated for each service during the first
run of the playbook.

To generate a new self-signed certificate for a service, you must set
the ``<servicename>_pki_regen_cert`` variable to true in one of the
following ways:

* To force a self-signed certificate to regenerate, you can pass the variable
  to ``openstack-ansible`` on the command line:

  .. code-block:: shell-session

     # openstack-ansible -e "haproxy_pki_regen_cert=true" haproxy-install.yml

* To force a self-signed certificate to regenerate with every playbook run,
  set the appropriate regeneration option to ``true``.  For example, if
  you have already run the ``haproxy`` playbook, but you want to regenerate
  the self-signed certificate, set the ``haproxy_pki_regen_cert``
  variable to ``true`` in the ``/etc/openstack_deploy/user_variables.yml``
  file:

  .. code-block:: yaml

     haproxy_pki_regen_cert: true


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

HAProxy example
---------------

The variables to set which provide the path on the deployment
node to the certificates for HAProxy configuration are:

.. code-block:: yaml

   haproxy_user_ssl_cert: /etc/openstack_deploy/ssl/example.com.crt
   haproxy_user_ssl_key: /etc/openstack_deploy/ssl/example.com.key
   haproxy_user_ssl_ca_cert: /etc/openstack_deploy/ssl/ExampleCA.crt

RabbitMQ example
----------------

To deploy user-provided certificates for RabbitMQ,
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

LetsEncrypt certificates
~~~~~~~~~~~~~~~~~~~~~~~~

The HAProxy ansible role supports using LetsEncrypt to automatically deploy
trusted SSL certificates for the public endpoint. Each HAProxy server will
individually request a LetsEncrypt certificate.

The http-01 type challenge is used by certbot to deploy certificates so
it is required that the public endpoint is accessible directly on the
internet.

Deployment of certificates using LetsEncrypt has been validated for
openstack-ansible using Ubuntu Bionic. Other distributions should work
but are not tested.

To deploy certificates with LetsEncrypt, add the following to
``/etc/openstack_deploy/user_variables.yml`` to enable the
letsencrypt function in the haproxy ansible role, and to
create a new backend service called ``letsencrypt`` to service
http-01 challenge requests.

.. code-block:: shell-session

    haproxy_ssl: true
    haproxy_ssl_letsencrypt_enable: True
    haproxy_ssl_letsencrypt_install_method: "distro"
    haproxy_ssl_letsencrypt_email: "email.address@example.com"


If you don't have horizon deployed, you will need to define dummy service that
will listen on 80 and 443 ports and will be used for acme-challenge, whose
backend is certbot on the haproxy host:

.. code-block:: shell-session

  haproxy_extra_services:
    # the external facing service which serves the apache test site, with a acl for LE requests
    - service:
        haproxy_service_name: certbot
        haproxy_redirect_http_port: 80                         #redirect port 80 to port ssl
        haproxy_redirect_scheme: "https if !{ ssl_fc } !{ path_beg /.well-known/acme-challenge/ }"   #redirect all non-ssl traffic to ssl except acme-challenge
        haproxy_port: 443
        haproxy_frontend_acls: "{{ haproxy_ssl_letsencrypt_acl }}"       #use a frontend ACL specify the backend to use for acme-challenge
        haproxy_ssl: True
        haproxy_backend_nodes:                                 #apache is running on locally on 127.0.0.1:80 serving a dummy site
          - name: local-test-service
            ip_addr: 127.0.0.1
        haproxy_balance_type: http
        haproxy_backend_port: 80
        haproxy_backend_options:
          - "httpchk HEAD /"                                   # request to use for health check for the example service
