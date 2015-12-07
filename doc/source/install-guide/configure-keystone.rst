`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring Keystone (optional)
-------------------------------

Customizing the Keystone deployment is done within
``/etc/openstack_deploy/user_variables.yml``.

Securing Keystone communication with SSL certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The openstack-ansible project provides the ability to secure Keystone
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Special considerations when using LDAP or AD backends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuring LDAP or Active Directory (AD) backends for keystone can make
deployment easier, but there are special considerations for these types of
deployments.

Creating users
""""""""""""""

During an OpenStack-Ansible deployment, the individual roles that deploy
various OpenStack services will attempt to create users in keystone. For
deployments where keystone uses LDAP as an authentication backend, these users
must be created **prior** to the running the OpenStack-Ansible playbooks. The
tasks for adding keystone users within individual role playbooks will be
skipped.

Stacked authentication
""""""""""""""""""""""

Some deployers may prefer to use "stacked" authentication where some users
exist in a SQL backend while other users exist in an LDAP or Active Directory
(AD) backend. This can be useful for deploys who want to reduce the number of
service accounts that must exist in LDAP or AD.

For more details on stacked authentication, see `Matt Fischer's blog post`_ or
review IBM's documentation titled `Configure OpenStack Keystone support for
domain-specific corporate directories`_.

.. _Matt Fischer's blog post: http://www.mattfischer.com/blog/?p=576
.. _Configure OpenStack Keystone support for domain-specific corporate directories: http://www.ibm.com/developerworks/cloud/library/cl-configure-keystone-ldap-and-active-directory/index.html

--------------

.. include:: navigation.txt
