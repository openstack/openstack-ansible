`Home <index.html>`__ OpenStack Ansible Installation Guide

Configuring HAProxy (optional)
------------------------------

For evaluation, testing, and development, HAProxy can temporarily
provide load balancing services in lieu of hardware load balancers. The
default HAProxy configuration does not provide highly-available load
balancing services. For production deployments, deploy a hardware load
balancer prior to deploying OSA.

-  In the ``/etc/openstack_deploy/openstack_user_config.yml`` file, add
   the ``haproxy_hosts`` section with one or more infrastructure target
   hosts, for example:

   .. code-block:: yaml

       haproxy_hosts:
         123456-infra01:
           ip: 172.29.236.51
         123457-infra02:
           ip: 172.29.236.52
         123458-infra03:
           ip: 172.29.236.53

SSL certificates for HAProxy
----------------------------

There are two options for deploying SSL certificates with HAProxy: self-signed
and user-provided certificates.  Auto-generated self-signed certificates are
currently the default.

Self-signed SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For self-signed certificates, users can configure the subject of the
certificate using the ``haproxy_ssl_self_signed_subject`` variable.

By default, the playbook won't regenerate a self-signed SSL certificate if one
already exists on the target.  To force the certificate to be regenerated
the next time the playbook runs, set ``haproxy_ssl_self_signed_regen`` to
``true``.  To do a one-time SSL certificate regeneration, you can run:

   .. code-block:: bash

    openstack-ansible -e 'haproxy_ssl_self_signed_regen=True' haproxy-install.yml

Keep in mind that regenerating self-signed certificates will overwrite any
existing certificates and keys, including ones that were previously
user-provided (see the following section).

The playbook will then use memcached to distribute the certificates and keys to
each HAProxy host.

User-provided SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can provide their own trusted certificates in a two step process:

#. Copy the SSL certificate, key, and CA certificate to the deployment host
#. Specify the path to those files on the deployment host

The path to the SSL certificate, key and CA certificate on the `deployment
host` must be specified in ``/etc/openstack_deploy/user_variables.yml``:

* ``haproxy_user_ssl_cert`` - path to the SSL certificate
* ``haproxy_user_ssl_key`` - path to the key
* ``haproxy_user_ssl_ca_cert`` - path to the CA certificate

If those three variables are provided, the playbook will deploy the files to
each HAProxy host.

--------------

.. include:: navigation.txt
