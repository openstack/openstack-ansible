.. _service-architecture:

====================
Service architecture
====================

Introduction
~~~~~~~~~~~~
OpenStack-Ansible has a flexible deployment configuration model that is
capable of deploying:

* All services in separate LXC machine containers, or on designated hosts
  without using LXC containers.
* All network traffic on a single network interface, or on many network
  interfaces.

This flexibility enables deployers to choose how to deploy OpenStack in a
way that makes the most sense for the specific use-case.

The following sections describe the services deployed by OpenStack-Ansible.

Infrastructure services
~~~~~~~~~~~~~~~~~~~~~~~

The following infrastructure components are deployed by OpenStack-Ansible:

* MariaDB/Galera

  All OpenStack services require an underlying database. MariaDB/Galera
  implements a multi-master database configuration which simplifies the
  ability to use it as a highly available database with a simple failover
  model.

* RabbitMQ

  OpenStack services make use of RabbitMQ for Remote Procedure Calls (RPC).
  OpenStack-Ansible deploys RabbitMQ in a clustered configuration with all
  queues mirrored between the cluster nodes. As Telemetry (ceilometer) message
  queue traffic is quite heavy, for large environments we recommended
  separating Telemetry notifications to a separate RabbitMQ cluster.

* MemcacheD

  OpenStack services use MemcacheD for in-memory caching, speeding up
  transactions. For example, the OpenStack Identity service (keystone) uses
  MemcacheD for caching authentication tokens. This is to ensure that token
  validation does not have to complete a disk or database transaction every
  time the service is asked to validate a token.

* Repository

  The repository holds the reference set of artifacts which are used for
  the installation of the environment. The artifacts include:

  * A git repository containing a copy of the source code which is used
    to prepare the packages for all OpenStack services.
  * Python wheels for all services that are deployed in the environment.
  * An apt/yum proxy cache that is used to cache distribution packages
    installed in the environment.

* Load Balancer

  At least one load balancer is required for a deployment. OpenStack-Ansible
  provides a deployment of `HAProxy`_, but we recommend using a physical
  load balancing appliance for production deployments.

* Utility Container

  The utility container is prepared with the appropriate credentials and
  clients in order to administer the OpenStack environment. It is set to
  automatically use the internal service endpoints.

* Log Aggregation Host

  A rsyslog service is optionally setup to receive rsyslog traffic from all
  hosts and containers. You can replace this with any alternative log
  receiver.

* Unbound DNS Container

  Containers running an `Unbound DNS`_ caching service can optionally be
  deployed to cache DNS lookups and to handle internal DNS name resolution.
  We recommend using this service for large scale production environments as
  the deployment will be significantly faster. If this option is not used,
  OpenStack-Ansible will fall back to modifying ``/etc/hosts`` entries for
  all hosts in the environment.

.. _HAProxy: http://www.haproxy.org/
.. _Unbound DNS: https://www.unbound.net/

OpenStack services
~~~~~~~~~~~~~~~~~~

OpenStack-Ansible is able to deploy the following OpenStack services:

* Bare Metal (`ironic`_)
* Block Storage (`cinder`_)
* Compute (`nova`_)
* Container Infrastructure Management (`magnum`_)
* Dashboard (`horizon`_)
* Data Processing (`sahara`_)
* Identity (`keystone`_)
* Image (`glance`_)
* Networking (`neutron`_)
* Object Storage (`swift`_)
* Orchestration (`heat`_)
* Telemetry (`aodh`_, `ceilometer`_, `gnocchi`_)

.. _ironic: http://docs.openstack.org/developer/ironic
.. _cinder: http://docs.openstack.org/developer/cinder
.. _nova: http://docs.openstack.org/developer/nova
.. _magnum: http://docs.openstack.org/developer/magnum
.. _horizon: http://docs.openstack.org/developer/horizon
.. _sahara: http://docs.openstack.org/developer/sahara
.. _keystone: http://docs.openstack.org/developer/keystone
.. _glance: http://docs.openstack.org/developer/glance
.. _neutron: http://docs.openstack.org/developer/neutron
.. _swift: http://docs.openstack.org/developer/swift
.. _heat: http://docs.openstack.org/developer/heat
.. _aodh: http://docs.openstack.org/developer/aodh
.. _ceilometer: http://docs.openstack.org/developer/ceilometer
.. _gnocchi: http://docs.openstack.org/developer/gnocchi

