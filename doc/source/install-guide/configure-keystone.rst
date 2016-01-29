`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring Keystone (optional)
-------------------------------

Customizing the Keystone deployment is done within
``/etc/openstack_deploy/user_variables.yml``.

Securing Keystone communication with SSL certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OpenStack-Ansible project provides the ability to secure Keystone
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Implementing LDAP (or AD) Back-Ends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In many environments there may already be a LDAP (or Active Directory) service
available which already has Users, Groups and User-Group assignment data.
Keystone can be configured to make use of the LDAP service using
Domain-specific Back-End configuration.

While it is possible to set the Keystone Identity Back-End to use LDAP for
the Default domain, this is not recommended. It is a better practice to use
the Default domain for service accounts and to configure additional Domains
for LDAP services which provide general User/Group data.

Example implementation in user_variables.yml:

keystone_ldap:
  Users:
    url: "ldap://10.10.10.10"
    user: "root"
    password: "secrete"
    ...
  Admins:
    url: "ldap://20.20.20.20"
    user: "root"
    password: "secrete"
    ...

This will place two configuration files into /etc/keystone/domains/, both of
which will be configured to use the LDAP driver.

 - keystone.Users.conf
 - keystone.Admins.conf

Each first level key entry is a domain name. Each entry below that are
key-value pairs for the 'ldap' section in the configuration file.

More details regarding valid configuration for the LDAP Identity Back-End can
be found in the `Keystone Developer Documentation`_ and the
`OpenStack Admin Guide`_.

.. _Keystone Developer Documentation: http://docs.openstack.org/developer/keystone/configuration.html#configuring-the-ldap-identity-provider
.. _OpenStack Admin Guide: http://docs.openstack.org/admin-guide-cloud/keystone_integrate_identity_backend_ldap.html

.. include:: navigation.txt
