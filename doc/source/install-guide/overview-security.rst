`Home <index.html>`__ OpenStack-Ansible Installation Guide

Security
--------

The OpenStack-Ansible project provides several security features for
OpenStack deployments.  This section of documentation covers some of those
features and how they can benefit deployers of various sizes.

Security requirements will always differ between deployers.  For deployers
that need additional security measures in place, please refer to the official
`OpenStack Security Guide`_ for additional resources.

AppArmor
~~~~~~~~

The Linux kernel offers multiple `security modules`_ (LSMs) that that set
`mandatory access controls`_ (MAC) on Linux systems.  The OpenStack-Ansible
project configures `AppArmor`_, a Linux security module, to provide additional
security on LXC container hosts.  AppArmor allows administrators to set
specific limits and policies around what resources a particular application
can access.  Any activity outside the allowed policies is denied at the kernel
level.

In OpenStack-Ansible, AppArmor profiles are applied that limit the actions
that each LXC container may take on a system.  This is done within the
`lxc_hosts role`_.

.. _security modules: https://en.wikipedia.org/wiki/Linux_Security_Modules
.. _mandatory access controls: https://en.wikipedia.org/wiki/Mandatory_access_control
.. _AppArmor: https://en.wikipedia.org/wiki/AppArmor
.. _lxc_hosts role: https://github.com/openstack/openstack-ansible/blob/master/playbooks/roles/lxc_hosts/templates/lxc-openstack.apparmor.j2

Encrypted communication
~~~~~~~~~~~~~~~~~~~~~~~

Data is encrypted while in transit between some OpenStack services in
OpenStack-Ansible deployments.  Not all communication between all services is
currently encrypted.  For more details on what traffic is encrypted, and how
to configure SSL certificates, refer to the documentation section titled
`Securing services with SSL certificates`_.

.. _Securing services with SSL certificates: configure-sslcertificates.html

Host security hardening
~~~~~~~~~~~~~~~~~~~~~~~

Deployers can apply security hardening to OpenStack infrastructure and compute
hosts using the openstack-ansible-security role. The purpose of the role is to
apply as many security configurations as possible without disrupting the
operation of an OpenStack deployment.

Refer to the documentation on :ref:`security_hardening` for more information
on the role and how to enable it in OpenStack-Ansible.

Least privilege
~~~~~~~~~~~~~~~

The `principle of least privilege`_ is used throughout OpenStack-Ansible to
limit the damage that could be caused if an attacker gained access to a set of
credentials.

OpenStack-Ansible configures unique username and password combinations for
each service that talks to RabbitMQ and Galera/MariaDB.  Each service that
connects to RabbitMQ uses a separate virtual host for publishing and consuming
messages.  The MariaDB users for each service are only granted access to the
database(s) that they need to query.

.. _principle of least privilege: https://en.wikipedia.org/wiki/Principle_of_least_privilege

.. _least-access-openstack-services:

Securing network access to OpenStack services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack environments expose many service ports and API endpoints to the
network. **Deployers must limit access to these resources and expose them only
to trusted users and networks.**

The resources within an OpenStack environment can be divided into two groups:

1. Services that users must access directly to consume the OpenStack cloud.

   * Aodh
   * Cinder
   * Ceilometer
   * Glance
   * Heat
   * Horizon
   * Keystone *(excluding the admin API endpoint)*
   * Neutron
   * Nova
   * Swift

2. Services that are only utilized internally by the OpenStack cloud.

   * Keystone (admin API endpoint)
   * MariaDB
   * RabbitMQ

Users must be able to access certain public API endpoints, such as the Nova or
Neutron API, to manage instances. Deployers should configure firewalls to allow
access to these services, but that access should be limited to the fewest
networks possible.

Other services, such as MariaDB and RabbitMQ, **must be segmented away from
direct user access**. Deployers must configure a firewall to only allow
connectivity to these services within the OpenStack environment itself. This
reduces an attacker's ability to query or manipulate data in OpenStack's
critical database and queuing services, especially if one of these services has
a known vulnerability.

For more details on recommended network policies for OpenStack clouds, refer to
the `API endpoint process isolation and policy`_ section from the `OpenStack
Security Guide`_

.. _API endpoint process isolation and policy: http://docs.openstack.org/security-guide/api-endpoints/api-endpoint-configuration-recommendations.html#network-policy
.. _OpenStack Security Guide: http://docs.openstack.org/security-guide

--------------

.. include:: navigation.txt
