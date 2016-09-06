=====================
Appendix D: Security
=====================

Security is one of the top priorities within OpenStack-Ansible and many
security enhancements for OpenStack clouds are available in deployments by
default. This appendix serves as a detailed overview of the most important
security improvements.

Every deployer will have different security requirements based on their
business needs, regulatory requirements, or end user demands. The official
`OpenStack Security Guide`_ has plenty of instructions and advice on how to
operate and consume an OpenStack cloud via the most secure methods.

Encrypted communication
~~~~~~~~~~~~~~~~~~~~~~~

Any OpenStack cloud will have sensitive information transmitted between
services. This information includes user credentials, service credentials or
information about resources being created. Encrypting this traffic is critical
in environments where the network may not be trusted.
*(Review the :ref:`least-access-openstack-services` section below for more
details on securing the network.)*

Many of the services deployed with OpenStack-Ansible are encrypted by default
or offer encryption as an option. The playbooks generate self-signed
certificates by default, but deployers have the option to use their existing
certificates, keys, and CA certificates.

To learn more about how to customize the deployment of encrypted
communications, review the `Securing services with SSL certificates`_
documentation section.

.. _Securing services with SSL certificates: app-advanced-config-sslcertificates.html

Host security hardening
~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible offers a comprehensive `security hardening role`_ that
applies over 200 security configurations as recommended by the `Security
Technical Implementation Guide`_ (STIG) provided by the `Defense Information
Systems Agency`_ (DISA). These security configurations are widely uses and are
distributed in the public domain by the United States Government.

Host security hardening is required by several compliance and regulatory
programs, such as the `Payment Card Industry Data Security Standard`_ (PCI
DSS) *(see Requirement 2.2)*.

OpenStack-Ansible automatically applies the security hardening role to all
deployments by default, but this can be disabled via an Ansible variable. The
role has been carefully designed to:

* Apply non-disruptively to a production OpenStack environment
* Balance security with OpenStack performance and functionality
* Run as quickly as possible

Refer to the documentation on :ref:`security_hardening` for more information
on the role in OpenStack-Ansible.

.. _security hardening role: http://docs.openstack.org/developer/openstack-ansible-security/
.. _Security Technical Implementation Guide: https://en.wikipedia.org/wiki/Security_Technical_Implementation_Guide
.. _Defense Information Systems Agency: http://www.disa.mil/
.. _Payment Card Industry Data Security Standard: https://www.pcisecuritystandards.org/pci_security/

Isolation
~~~~~~~~~

OpenStack-Ansible provides isolation by default between the containers that run
the OpenStack control plane services and also between the virtual machines that
end users spawn within the deployment. This isolation is critical since it can
prevent container or virtual machine breakouts, or at least reduce the damage
that they may cause.

The `Linux Security Modules`_ (LSM) framework allows administrators to set
`mandatory access controls`_ (MAC) on a Linux system. This is different than
`discretionary access controls`_ (DAC) because the kernel enforces strict
policies that cannot be bypassed by any user.  Although a user may be able to
change a DAC (such as ``chown bob secret.txt``), they cannot alter a MAC
policy. This privilege is reserved for the ``root`` user.

OpenStack-Ansible currently uses `AppArmor`_ to provide MAC policies on control
plane servers as well as hypervisors. The AppArmor configuration sets the
access policies to prevent one container from accessing the data of another
container. For virtual machines, ``libvirtd`` uses the `sVirt`_ extensions to
ensure that one virtual machine cannot access the data or devices from another
virtual machine.

These policies are applied and governed at the kernel level. Any process that
violates a policy will be denied access to the resource. All denials are logged
within ``auditd`` and are available at ``/var/log/audit/audit.log``.

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
each service that talks to RabbitMQ and Galera/MariaDB. Each service that
connects to RabbitMQ uses a separate virtual host for publishing and consuming
messages. The MariaDB users for each service are only granted access to the
database(s) that they need to query.

.. _principle of least privilege: https://en.wikipedia.org/wiki/Principle_of_least_privilege

.. _least-access-openstack-services:

Securing network access to OpenStack services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack clouds offer many services to end users which allow them to build
instances, provision storage, and create networks. Each of these services
exposes one or more service ports and API endpoints to the network.

However, some of the services within an OpenStack clouds should be exposed to
all end users while others should only be available to administrators or
operators on a secured network.

OpenStack services fit into one of two criteria:

* Services that **all end users** can access

  * This includes services such as nova, swift, neutron, and glance.
  * These should be offered on a sufficiently restricted network that still
    allows all end users to access the services.
  * A firewall must be used to restrict access to the network.

* Services that **only administrators or operators** can access

  * This includes services such as MariaDB, memcached, RabbitMQ and the admin
    API endpoint for keystone.
  * These services **must** be offered on a highly restricted network that is
    available only to administrative users.
  * A firewall must be used to restrict access to the network.

Limiting access to these networks has several benefits:

* Allows for network monitoring and alerting
* Prevents unauthorized network surveillance
* Reduces the chance of credential theft
* Reduces damage from unknown or unpatched service vulnerabilities

OpenStack-Ansible deploys HAProxy backends for each service and restricts
access for highly sensitive services by making them available only on the
management network. Deployers with external load balancers must ensure that the
backends are configured securely and that firewalls prevent traffic from
crossing between networks.

For more details on recommended network policies for OpenStack clouds, refer
to the `API endpoint process isolation and policy`_ section from the
`OpenStack Security Guide`_

.. _API endpoint process isolation and policy: http://docs.openstack.org/security-guide/api-endpoints/api-endpoint-configuration-recommendations.html#network-policy
.. _OpenStack Security Guide: http://docs.openstack.org/security-guide
