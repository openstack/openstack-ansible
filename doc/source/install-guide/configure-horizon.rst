`Home <index.html>`__ OpenStack Ansible Installation Guide

Configuring Horizon (optional)
------------------------------

Customizing the Horizon deployment is done within the ``os-horizon`` role in
``playbooks/roles/os-horizon/defaults.main.yml``.

SSL certificates
----------------

There are two options for deploying SSL certificates with Horizon: self-signed
and user-provided certificates.  Auto-generated self-signed certificates are
currently the default.

Self-signed SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For self-signed certificates, users can configure the subject of the
certificate using the ``horizon_ssl_self_signed_subject`` variable.  By
default, the playbook won't regenerate a self-signed SSL certificate if one
already exists in the container.  To force the certificate to be regenerated
the next time the playbook runs, set ``horizon_ssl_self_signed_regen`` to
``true``.

The playbook will then use memcached to distribute the certificates and keys to
each horizon container.

User-provided SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can provide their own trusted certificates by setting three variables:

* ``horizon_user_ssl_cert`` - path to the SSL certificate in the container
* ``horizon_user_ssl_key`` - path to the key in the container
* ``horizon_user_ssl_ca_cert`` - path to the CA certificate in the container

If those three variables are provided, self-signed certificate generation and
usage will be disabled.  However, it's up to the user to deploy those
certificates and keys within each container.

--------------

.. include:: navigation.txt
