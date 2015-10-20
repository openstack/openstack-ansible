`Home <index.html>`__ OpenStack Ansible Installation Guide

Security
--------

The openstack-ansible project provides several security features for
OpenStack deployments.  This section of documentation covers some of those
features and how they can benefit deployers of various sizes.

Security requirements will always differ between deployers.  For deployers
that need additional security measures in place, please refer to the official
`OpenStack Security Guide`_ for additional resources.

.. _OpenStack Security Guide: http://docs.openstack.org/sec/

AppArmor
~~~~~~~~

The Linux kernel offers multiple `security modules`_ (LSMs) that that set
`mandatory access controls`_ (MAC) on Linux systems.  The openstack-ansible
project configures `AppArmor`_, a Linux security module, to provide additional
security on LXC container hosts.  AppArmor allows administrators to set
specific limits and policies around what resources a particular application
can access.  Any activity outside the allowed policies is denied at the kernel
level.

In openstack-ansible, AppArmor profiles are applied that limit the actions
that each LXC container may take on a system.  This is done within the
`lxc_hosts role`_.

.. _security modules: https://en.wikipedia.org/wiki/Linux_Security_Modules
.. _mandatory access controls: https://en.wikipedia.org/wiki/Mandatory_access_control
.. _AppArmor: https://en.wikipedia.org/wiki/AppArmor
.. _lxc_hosts role: https://github.com/openstack/openstack-ansible/blob/master/playbooks/roles/lxc_hosts/templates/lxc-openstack.apparmor.j2

Encrypted communication
~~~~~~~~~~~~~~~~~~~~~~~

Data is encrypted while in transit between some OpenStack services in
openstack-ansible deployments.  Not all communication between all services is
currently encrypted.  For more details on what traffic is encrypted, and how
to configure SSL certificates, refer to the documentation section titled
`Securing services with SSL certificates`_.

.. _Securing services with SSL certificates: configure-sslcertificates.html

--------------

.. include:: navigation.txt
