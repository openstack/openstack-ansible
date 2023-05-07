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

.. note::

   The openstack-ansible example configurations are designed to be minimal
   examples and in test or development use-cases will set ``external_lb_vip_address``
   to the IP address of the haproxy external endpoint. For a production
   deployment it is advised to set ``external_lb_vip_address`` to be
   the FQDN which resolves via DNS to the IP of the external endpoint.

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

To regenerate a new self-signed certificate for a service, you must set
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

Generating and regenerating self-signed user certificates
---------------------------------------------------------

Self-signed user certificates are generated but not installed for services
outside of Openstack ansible. These user certificates are signed by the same
self-signed certificate authority as is used by openstack services
but are intended to be used by user applications.

To generate user certificates, define a variable with the prefix
``user_pki_certificates_`` in the ``/etc/openstack_deploy/user_variables.yml``
file.

Example

.. code-block:: yaml

   user_pki_certificates_example:
      - name: "example"
        provider: ownca
        cn: "example.com"
        san: "DNS:example.com,IP:x.x.x.x"
        signed_by: "{{ openstack_pki_service_intermediate_cert_name }}"
        key_usage:
          - digitalSignature
          - keyAgreement
        extended_key_usage:
          - serverAuth

Generate the certificate with the following command:

.. code-block:: shell-session

   # openstack-ansible certificate-generate.yml

To regenerate a new self-signed certificate for a service, you must set
the ``user_pki_regen_cert`` variable to true in one of the
following ways:

* To force a self-signed certificate to regenerate, you can pass the variable
  to ``openstack-ansible`` on the command line:

  .. code-block:: shell-session

     # openstack-ansible -e "user_pki_regen_cert=true" certificate-generate.yml

* To force a self-signed certificate to regenerate with every playbook run,
  set the ``user_pki_regen_cert`` variable to ``true`` in the
  ``/etc/openstack_deploy/user_variables.yml`` file:

  .. code-block:: yaml

     user_pki_regen_cert: true


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

Certbot certificates
~~~~~~~~~~~~~~~~~~~~

The HAProxy ansible role supports using certbot to automatically deploy
trusted SSL certificates for the public endpoint. Each HAProxy server will
individually request a SSL certificate using certbot.

Certbot defaults to using LetsEncrypt as the Certificate Authority, other
Certificate Authorities can be used by setting the
``haproxy_ssl_letsencrypt_certbot_server`` variable in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   haproxy_ssl_letsencrypt_certbot_server: "https://acme-staging-v02.api.letsencrypt.org/directory"

The http-01 type challenge is used by certbot to deploy certificates so
it is required that the public endpoint is accessible directly by the
Certificate Authority.

Deployment of certificates using LetsEncrypt has been validated for
openstack-ansible using Ubuntu Focal. Other distributions should work
but are not tested.

To deploy certificates with certbot, add the following to
``/etc/openstack_deploy/user_variables.yml`` to enable the
certbot function in the haproxy ansible role, and to
create a new backend service called ``certbot`` to service
http-01 challenge requests.

.. code-block:: shell-session

    haproxy_ssl: true
    haproxy_ssl_letsencrypt_enable: True
    haproxy_ssl_letsencrypt_email: "email.address@example.com"

TLS for Haproxy Internal VIP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As well as load balancing public endpoints, haproxy is also used to load balance
internal connections.

By default, OpenStack-Ansible does not secure connections to the internal VIP.
To enable this you must set the following variables in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   openstack_service_adminuri_proto: https
   openstack_service_internaluri_proto: https

   haproxy_ssl_all_vips: true

Run all playbooks to configure haproxy and openstack services.

When enabled haproxy will use the same TLS certificate on all interfaces
(internal and external). It is not currently possible in OpenStack-Ansible to
use different self-signed or user-provided TLS certificates on different haproxy
interfaces.

The only way to use a different TLS certificates on the internal and external
VIP is to use certbot.

Enabling TLS on the internal VIP for existing deployments will cause some
downtime, this is because haproxy only listens on a single well known port for
each OpenStack service and OpenStack services are configured to use http or
https. This means once haproxy is updated to only accept HTTPS connections, the
OpenStack services will stop working until they are updated to use HTTPS.

For this reason it is recommended that TLS for haproxy internal VIP on existing
deployments is deployed at the same time as enabling TLS for Haproxy backends,
as this may also cause downtime. For new deployments this should be enabled from
the start.

TLS for Haproxy Backends
~~~~~~~~~~~~~~~~~~~~~~~~

Securing the internal communications from haproxy to backend services is
currently work in progress.

TLS for Live Migrations
~~~~~~~~~~~~~~~~~~~~~~~

Live migration of VM's using SSH is deprecated and the `OpenStack Nova Docs`_
recommends using the more secure native TLS method supported by QEMU. The
default live migration method used by OpenStack-Ansible has been updated to
use TLS migrations.

.. _OpenStack Nova Docs: https://docs.openstack.org/nova/latest/admin/secure-live-migration-with-qemu-native-tls.html

QEMU-native TLS requires all compute hosts to accept TCP connections on
port 16514 and port range 49152 to 49261.

It is not possible to have a mixed estate of some compute nodes using SSH and
some using TLS for live migrations, as this would prevent live migrations
between the compute nodes.

There are no issues enabling TLS live migration during an OpenStack upgrade, as
long as you do not need to live migrate instances during the upgrade. If you
you need to live migrate instances during an upgrade, enable TLS live migrations
before or after the upgrade.

To force the use of SSH instead of TLS for live migrations you must set the
``nova_libvirtd_listen_tls`` variable to ``0`` in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   nova_libvirtd_listen_tls: 0

TLS for VNC
~~~~~~~~~~~

When using VNC for console access there are 3 connections to secure, client to
haproxy, haproxy to noVNC Proxy and noVNC Proxy to Compute nodes. The `OpenStack
Nova Docs for remote console access`_ cover console security in much more
detail.

.. _OpenStack Nova Docs for remote console access: https://docs.openstack.org/nova/latest/admin/remote-console-access.html#vnc-proxy-security

In OpenStack-Ansible TLS to haproxy is configured in haproxy, TLS from
haproxy to noVNC is not currently enabled and TLS from nVNC to Compute nodes
is enabled by default.

Changes will not apply to any existing running guests on the compute node,
so this configuration should be done before launching any instances. For
existing deployments it is recommended that you migrate instances off the
compute node before enabling.

To help with the transition from unencrypted VNC to VeNCrypt,
initially noVNC proxy auth scheme allows for both encrypted and
unencrypted sessions using the variable `nova_vencrypt_auth_scheme`. This will
be restricted to VeNCrypt only in future versions of OpenStack-Ansible.

.. code-block:: yaml

   nova_vencrypt_auth_scheme: "vencrypt,none"

To not encrypt data from noVNC proxy to Compute nodes you must set the
``nova_qemu_vnc_tls`` variable to ``0`` in the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   nova_qemu_vnc_tls: 0
