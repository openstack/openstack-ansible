`Home <index.html>`_ OpenStack-Ansible Installation Guide

====================
Storage architecture
====================

OpenStack-Ansible supports Block Storage (cinder), Ephemeral storage
(nova), Image service (glance) and Object Storage (swift).


Block Storage (cinder)
~~~~~~~~~~~~~~~~~~~~~~

 .. important::

    The Block Storage used by each service is typically on a storage system, not
    a server. An exception to this is the LVM-backed storage store which is a
    reference implementation and is used primarily for test environments but not
    for production environments. For non-server storage systems, the cinder-volume
    service interacts with the Block Storage system through an API which
    is implemented in the appropriate driver.

When using the cinder LVM driver, you have separate physical hosts with the
volume groups that cinder volumes will use.
Most of the other external cinder storage (For example: Ceph, EMC, NAS, and
NFS) set up a container inside one of the infra hosts.

 .. note::

    The ``cinder_volumes`` service cannot run in a highly available configuration.
    This is not to be set up on multiple hosts. If you have multiple storage
    backends, set up one per volumes container.
    For more information: `<https://specs.openstack.org/openstack/cinder-specs/specs/mitaka/cinder-volume-active-active-support.html>`_.


Configuring the Block Storage service (cinder)
----------------------------------------------

Configure ``cinder-api`` infra hosts with ``br-storage`` and ``br-mgmt``.
Configure ``cinder-volumes`` hosts with ``br-storage`` and ``br-mgmt``.

* ``br-storage`` bridge carries Block Storage traffic to compute host.
* ``br-mgmt`` bridge carries Block Storage API requests traffic.

 .. note::

    It is recommended for production environment that the traffic (storage and
    API request) from the hosts be segregated onto its own network.


Object Storage (swift)
~~~~~~~~~~~~~~~~~~~~~~

The swift proxy service container resides on one of the infra hosts whereas the
actual swift objects are stored on separate physical hosts.

 .. important::

    The swift proxy service is responsible for storage, retrieval, encoding and
    decoding of objects from an object server.

Configuring the Object Storage (swift)
--------------------------------------

Ensure the swift proxy hosts are configured with ``br-mgmt`` and
``br-storage``. Ensure storage hosts are on ``br-storage``. When using
dedicated replication, also ensure storage hosts are on ``br-repl``.

``br-storage`` handles the retrieval and upload of objects to the storage
nodes. ``br-mgmt`` handles the API requests.

* ``br-storage`` handles the transfer of objects from the storage hosts to
  the proxy and vice-versa.
* ``br-repl`` handles the replication of objects between storage hosts,
  and is not needed by the proxy containers.

 .. note::

    ``br-repl`` is optional. Replication occurs over the ``br-storage``
    interface when there is no ``br-repl`` replication bridge.


Ephemeral storage (nova)
~~~~~~~~~~~~~~~~~~~~~~~~

The ``nova-scheduler`` container resides on the infra host. The
``nova-scheduler`` service determines on which host (node on
which ``nova-compute`` service is running) a particular VM
should launch.

The ``nova-api-os-compute`` container resides on the infra host. The
``nova-compute`` service resides on the compute host. The
``nova-api-os-compute`` container handles the client API requests and
passes messages to the ``nova-scheduler``. The API requests may
involve operations that requires scheduling (For example: instance
creation or deletion). These messages are then sent to
``nova-conductor`` which in turn pushes messages to ``nova-compute``
on the compute host.

Configuring the ephemeral storage (nova)
----------------------------------------

All nova containers on the infra hosts communicate using the AMQP service over
the management network ``br-mgmt``.

Configure the ``nova-compute`` host with ``br-mgmt`` for it to
communicate with the ``nova-conductor`` and ``br-storage`` for it to
carry traffic to the storage host. Configure the
``nova-api-os-compute`` host with the ``br-mgmt``.

* ``br-mgmt`` bridge handles the client interaction for API requests.
* ``br-storage`` bridge handles the transfer of data from the storage
  hosts to the compute host and vice-versa.

 .. note::

    It is recommended for production environment that the traffic (storage
    and API request) from the hosts be segregated onto its own network.


Image service (glance)
~~~~~~~~~~~~~~~~~~~~~~

The glance API and volume service runs in the glance container on
infra hosts.

Configuring the Image service (glance)
--------------------------------------
Configure glance-volume container to use the ``br-storage`` and
``br-mgmt`` interfaces.

* ``br-storage`` bridge carries image traffic to compute host.
* ``br-mgmt`` bridge carries Image Service API request traffic.


--------------

.. include:: navigation.txt
