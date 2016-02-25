`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring Keystone (optional)
-------------------------------

Customizing the Keystone deployment is done within
``/etc/openstack_deploy/user_variables.yml``.

Securing Keystone communication with SSL certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The OpenStack-Ansible project provides the ability to secure Keystone
communications with self-signed or user-provided SSL certificates. By default,
self-signed certificates are used with Keystone.  However, deployers can
provide their own certificates by using the following Ansible variables in
``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

    keystone_user_ssl_cert:          # Path to certificate
    keystone_user_ssl_key:           # Path to private key
    keystone_user_ssl_ca_cert:       # Path to CA certificate

Refer to `Securing services with SSL certificates`_ for more information on
these configuration options and how deployers can provide their own
certificates and keys to use with Keystone.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Implementing LDAP (or Active Directory) Back ends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deployers that already have LDAP or Active Directory (AD) infrastructure
deployed can use the built-in Keystone support for those identity services.
Keystone can use the existing users, groups and user-group relationships to
handle authentication and access control in an OpenStack deployment.

.. note::

   Although deployers can configure the default domain in Keystone to use LDAP
   or AD identity back ends, **this is not recommended**. Deployers should
   create an additional domain in Keystone and configure an LDAP/AD back end
   for that domain.

   This is critical in situations where the identity back end cannot
   be reached due to network issues or other problems. In those situations,
   the administrative users in the default domain would still be able to
   authenticate to keystone using the default domain which is not backed by
   LDAP or AD.

Deployers can add domains with LDAP back ends by adding variables in
``/etc/openstack_deploy/user_variables.yml``. For example, this dictionary will
add a new Keystone domain called ``Users`` that is backed by an LDAP server:

.. code-block:: yaml

    keystone_ldap:
      Users:
        url: "ldap://10.10.10.10"
        user: "root"
        password: "secrete"

Adding the YAML block above will cause the Keystone playbook to create a
``/etc/keystone/domains/keystone.Users.conf`` file within each Keystone service
container that configures the LDAP-backed domain called ``Users``.

Deployers can create more complex configurations that use LDAP filtering and
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

In the *MyCorporation* example above, Keystone will use the LDAP server as a
read-only resource. The configuration also ensures that Keystone filters the
list of possible users to the ones that exist in the
``cn=openstack-users,ou=Users,o=MyCorporation`` group.

Horizon offers multi-domain support that can be enabled with an Ansible
variable during deployment:

.. code-block:: yaml

    horizon_keystone_multidomain_support: True

Enabling multi-domain support in Horizon will add the ``Domain`` input field on
the Horizon login page and it will add other domain-specific features in the
*Identity* section.

More details regarding valid configuration for the LDAP Identity Back-End can
be found in the `Keystone Developer Documentation`_ and the
`OpenStack Admin Guide`_.

.. _Keystone Developer Documentation: http://docs.openstack.org/developer/keystone/configuration.html#configuring-the-ldap-identity-provider
.. _OpenStack Admin Guide: http://docs.openstack.org/admin-guide-cloud/keystone_integrate_identity_backend_ldap.html

.. include:: navigation.txt
