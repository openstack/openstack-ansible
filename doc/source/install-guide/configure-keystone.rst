`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Identity service (keystone) (optional)
======================================================

Customize your keystone deployment in ``/etc/openstack_deploy/user_variables.yml``.


Securing keystone communication with SSL certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OpenStack-Ansible project provides the ability to secure keystone
communications with self-signed or user-provided SSL certificates. By default,
self-signed certificates are in use. However, you can
provide your own certificates by using the following Ansible variables in
``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    keystone_user_ssl_cert:          # Path to certificate
    keystone_user_ssl_key:           # Path to private key
    keystone_user_ssl_ca_cert:       # Path to CA certificate

.. note:: If the deployer is providing certificate, key, and ca files
    for a CA without chain of trust (or an invalid/self-generated ca),
    the variables `keystone_service_internaluri_insecure` and
    `keystone_service_adminuri_insecure` should be set to True.

Refer to `Securing services with SSL certificates`_ for more information on
these configuration options and how you can provide your own
certificates and keys to use with keystone.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Implementing LDAP (or Active Directory) backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the built-in keystone support for services if you already have
LDAP or Active Directory (AD) infrastructure on your deployment. 
Keystone uses the existing users, groups, and user-group relationships to
handle authentication and access control in an OpenStack deployment.

.. note::

   We do not recommend configuring the default domain in keystone to use
   LDAP or AD identity backends. Create additional domains
   in keystone and configure either LDAP or active directory backends for
   that domain. 
  
   This is critical in situations where the identity backend cannot
   be reached due to network issues or other problems. In those situations,
   the administrative users in the default domain would still be able to
   authenticate to keystone using the default domain which is not backed by
   LDAP or AD.

You can add domains with LDAP backends by adding variables in
``/etc/openstack_deploy/user_variables.yml``. For example, this dictionary
adds a new keystone domain called ``Users`` that is backed by an LDAP server:

.. code-block:: yaml

    keystone_ldap:
      Users:
        url: "ldap://10.10.10.10"
        user: "root"
        password: "secrete"

Adding the YAML block above causes the keystone playbook to create a
``/etc/keystone/domains/keystone.Users.conf`` file within each keystone service
container that configures the LDAP-backed domain called ``Users``.

You can create more complex configurations that use LDAP filtering and
consume LDAP as a read-only resource. The following example shows how to apply
these configurations:

.. code-block:: yaml

    keystone_ldap:
      MyCorporation:
          url: "ldaps://ldap.example.com"
          user_tree_dn: "ou=Users,o=MyCorporation"
          group_tree_dn: "cn=openstack-users,ou=Users,o=MyCorporation"
          user_objectclass: "inetOrgPerson"
          user_allow_create: "False"
          user_allow_update: "False"
          user_allow_delete: "False"
          group_allow_create: "False"
          group_allow_update: "False"
          group_allow_delete: "False"
          user_id_attribute: "cn"
          user_name_attribute: "uid"
          user_filter: "(groupMembership=cn=openstack-users,ou=Users,o=MyCorporation)"

In the `MyCorporation` example above, keystone uses the LDAP server as a
read-only resource. The configuration also ensures that keystone filters the
list of possible users to the ones that exist in the
``cn=openstack-users,ou=Users,o=MyCorporation`` group.

Horizon offers multi-domain support that can be enabled with an Ansible
variable during deployment:

.. code-block:: yaml

    horizon_keystone_multidomain_support: True

Enabling multi-domain support in horizon adds the ``Domain`` input field on
the horizon login page and it adds other domain-specific features in the
keystone section.

More details regarding valid configuration for the LDAP Identity backend can
be found in the `Keystone Developer Documentation`_ and the
`OpenStack Admin Guide`_.

.. _Keystone Developer Documentation: http://docs.openstack.org/developer/keystone/configuration.html#configuring-the-ldap-identity-provider
.. _OpenStack Administrator Guide: http://docs.openstack.org/admin-guide/keystone_integrate_identity_backend_ldap.html

--------------

.. include:: navigation.txt
