.. _service-architecture:

====================
Service architecture
====================

Introduction
~~~~~~~~~~~~
OpenStack-Ansible has a flexible deployment configuration model that
can deploy all services in separate LXC containers or on designated hosts
without using LXC containers, and all network traffic either on a single
network interface or on many network interfaces.

This flexibility enables deployers to choose how to deploy OpenStack in the
appropriate way for the specific use case.

The following sections describe the services that OpenStack-Ansible deploys.

Infrastructure services
~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible deploys the following infrastructure components:

* MariaDB with Galera

  All OpenStack services require an underlying database. MariaDB with Galera
  implements a multimaster database configuration, which simplifies its use
  as a highly available database with a simple failover model.

* RabbitMQ

  OpenStack services use RabbitMQ for Advanced Message Queuing Protocol (AMQP).
  OSA deploys RabbitMQ in a clustered configuration with all
  queues mirrored between the cluster nodes. Because Telemetry (ceilometer)
  message queue traffic is quite heavy, for large environments we recommend
  separating Telemetry notifications into a separate RabbitMQ cluster.

* Memcached

  OpenStack services use Memcached for in-memory caching, which accelerates
  transactions. For example, the OpenStack Identity service (keystone) uses
  Memcached for caching authentication tokens, which ensures that token
  validation does not have to complete a disk or database transaction every
  time the service is asked to validate a token.

* Repository

  The repository holds the reference set of artifacts that are used for
  the installation of the environment. The artifacts include:

  * A Git repository that contains a copy of the source code that is used
    to prepare the packages for all OpenStack services
  * Python wheels for all services that are deployed in the environment
  * An apt/yum proxy cache that is used to cache distribution packages
    installed in the environment

* Load balancer

  At least one load balancer is required for a deployment. OSA
  provides a deployment of `HAProxy`_, but we recommend using a physical
  load balancing appliance for production environments.

* Utility container

  If a tool or object does not require a dedicated container, or if it is
  impractical to create a new container for a single tool or object, it is
  installed in the utility container. The utility container is also used when
  tools cannot be installed directly on a host. The utility container is
  prepared with the appropriate credentials and clients to administer the
  OpenStack environment. It is set to automatically use the internal service
  endpoints.

* Log aggregation host

  A rsyslog service is optionally set up to receive rsyslog traffic from all
  hosts and containers. You can replace rsyslog with any alternative log
  receiver.

* Unbound DNS container

  Containers running an `Unbound DNS`_ caching service can optionally be
  deployed to cache DNS lookups and to handle internal DNS name resolution.
  We recommend using this service for large-scale production environments
  because the deployment will be significantly faster. If this service is not
  used, OSA modifies ``/etc/hosts`` entries for all hosts in the environment.

.. _HAProxy: http://www.haproxy.org/
.. _Unbound DNS: https://www.unbound.net/

OpenStack services
~~~~~~~~~~~~~~~~~~

OSA is able to deploy the following OpenStack services:

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

