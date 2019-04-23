.. _security-design:

Security
========

Security is one of the top priorities within OpenStack-Ansible (OSA), and many
security enhancements for OpenStack clouds are available in deployments by
default. This section provides a detailed overview of the most important
security enhancements.

.. note::

   Every deployer has different security requirements.
   The `OpenStack Security Guide`_ has instructions and advice on how to
   operate and consume an OpenStack cloud by using the most secure methods.

Encrypted communication
~~~~~~~~~~~~~~~~~~~~~~~

Any OpenStack cloud has sensitive information transmitted between
services, including user credentials, service credentials or
information about resources being created. Encrypting this traffic is critical
in environments where the network cannot be trusted. (For more information
about securing the network, see the :ref:`least-access-openstack-services`
section.)

Many of the services deployed with OpenStack-Ansible are encrypted by default
or offer encryption as an option. The playbooks generate self-signed
certificates by default, but deployers have the option to use their existing
certificates, keys, and CA certificates.

To learn more about how to customize the deployment of encrypted
communications, see
`Securing services with SSL certificates </user/security/index.html>`_.

Host security hardening
~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible provides a comprehensive `security hardening role`_ that
applies over 200 security configurations as recommended by the `Security
Technical Implementation Guide`_ (STIG) provided by the Defense Information
Systems Agency (DISA). These security configurations are widely used and are
distributed in the public domain by the United States government.

Host security hardening is required by several compliance and regulatory
programs, such as the `Payment Card Industry Data Security Standard`_ (PCI
DSS) (Requirement 2.2).

By default, OpenStack-Ansible automatically applies the ansible-hardening role
to all deployments. The role has been carefully designed to perform as follows:

* Apply nondisruptively to a production OpenStack environment
* Balance security with OpenStack performance and functionality
* Run as quickly as possible

For more information about the security configurations, see the
`security hardening role`_ documentation.

.. _security hardening role: http://docs.openstack.org/developer/ansible-hardening/
.. _Security Technical Implementation Guide: https://en.wikipedia.org/wiki/Security_Technical_Implementation_Guide
.. _Payment Card Industry Data Security Standard: https://www.pcisecuritystandards.org/pci_security/

Isolation
~~~~~~~~~

By default, OpenStack-Ansible provides isolation by default between the
containers that run the OpenStack infrastructure (control plane) services and
also between the virtual machines that end users spawn within the deployment.
This isolation is critical because it can prevent container or virtual machine
breakouts, or at least reduce the damage that breakouts might cause.

The `Linux Security Modules`_ (LSM) framework allows administrators to set
`mandatory access controls`_ (MAC) on a Linux system. MAC is different than
`discretionary access controls`_ (DAC) because the kernel enforces strict
policies that no user can bypass.  Although any user might be able to
change a DAC policy (such as ``chown bob secret.txt``), only the ``root`` user
can alter a MAC policy.

OpenStack-Ansible currently uses `AppArmor`_ to provide MAC policies on
infrastructure servers and hypervisors. The AppArmor configuration sets the
access policies to prevent one container from accessing the data of another
container. For virtual machines, ``libvirtd`` uses the `sVirt`_ extensions to
ensure that one virtual machine cannot access the data or devices from another
virtual machine.

These policies are applied and governed at the kernel level. Any process that
violates a policy is denied access to the resource. All denials are logged
in ``auditd`` and are available at ``/var/log/audit/audit.log``.

.. _Linux Security Modules: https://en.wikipedia.org/wiki/Linux_Security_Modules
.. _mandatory access controls: https://en.wikipedia.org/wiki/Mandatory_access_control
.. _discretionary access controls: https://en.wikipedia.org/wiki/Discretionary_access_control
.. _AppArmor: https://en.wikipedia.org/wiki/AppArmor
.. _sVirt: https://fedoraproject.org/wiki/Features/SVirt_Mandatory_Access_Control

Least privilege
~~~~~~~~~~~~~~~

The `principle of least privilege`_ is used throughout OpenStack-Ansible to
limit the damage that could be caused if an attacker gains access to any
credentials.

OpenStack-Ansible configures unique username and password combinations for
each service that interacts with RabbitMQ and Galera/MariaDB. Each service that
connects to RabbitMQ uses a separate virtual host for publishing and consuming
messages. The MariaDB users for each service are only granted access only to
the databases that they need to query.

.. _principle of least privilege: https://en.wikipedia.org/wiki/Principle_of_least_privilege

.. _least-access-openstack-services:

Securing network access to OpenStack services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack clouds provide many services to end users, that enable them to build
instances, provision storage, and create networks. Each of these services
exposes one or more service ports and API endpoints to the network.

However, some of the services within an OpenStack cloud are accessible to
all end users, while others are accessible only to administrators or
operators on a secured network.

* Services that *all end users* can access

  * These services include Compute (nova), Object Storage (swift), Networking
    (neutron), and Image (glance).
  * These services should be offered on a sufficiently restricted network that
    still allows all end users to access the services.
  * A firewall must be used to restrict access to the network.

* Services that *only administrators or operators* can access

  * These services include MariaDB, Memcached, RabbitMQ, and the admin
    API endpoint for the Identity (keystone) service.
  * These services *must* be offered on a highly restricted network that is
    available only to administrative users.
  * A firewall must be used to restrict access to the network.

Limiting access to these networks has several benefits:

* Allows for network monitoring and alerting
* Prevents unauthorized network surveillance
* Reduces the chance of credential theft
* Reduces damage from unknown or unpatched service vulnerabilities

OpenStack-Ansible deploys HAProxy back ends for each service and restricts
access for highly sensitive services by making them available only on the
management network. Deployers with external load balancers must ensure that the
back ends are configured securely and that firewalls prevent traffic from
crossing between networks.

For more information about recommended network policies for OpenStack clouds,
see the `API endpoint process isolation and policy`_ section of the
`OpenStack Security Guide`_

.. _API endpoint process isolation and policy: http://docs.openstack.org/security-guide/api-endpoints/api-endpoint-configuration-recommendations.html#network-policy
.. _OpenStack Security Guide: http://docs.openstack.org/security-guide
