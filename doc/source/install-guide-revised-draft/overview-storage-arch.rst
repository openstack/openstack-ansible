`Home <index.html>`_ OpenStack-Ansible Installation Guide

====================
Storage architecture
====================

OpenStack Ansible supports Block Storage (cinder) and Object Storage (swift).


Block storage (cinder)
~~~~~~~~~~~~~~~~~~~~~~

.. Suggestion: Document the location of the cinder-api service (containers on
   the infra hosts)
.. Suggestion: Document the location of the cinder-volumes service

.. important::

   The actual Block Storage service is not handled by OpenStack Ansible. The
   exception to this is the LVM backend storage on physical hosts.

When using LVM, you have separate physical hosts with the volume groups
that cinder volumes will use.
For any other external cinder storage including Ceph, EMC, NAS, and NFS,
set up a container inside one of the infra hosts.

.. note::

   ``cinder_volumes`` do not run in HA `active/active` mode.
   This is not to be set up on multiple hosts. If you have multiple storage
   backends, set up one per volumes container.
   For more information: `<https://specs.openstack.org/openstack/cinder-specs/specs/mitaka/cinder-volume-active-active-support.html>`_.


Networking for Block Storage (cinder)
-------------------------------------

Configure ``cinder-api`` infra hosts with ``br-storage`` for storage requests
and ``br-mgmt`` for API requests. ``cinder-volumes`` hosts require
``br-storage``.


Object Storage (swift)
~~~~~~~~~~~~~~~~~~~~~~

.. Suggestion: Document the location of the swift-proxy hosts (containers on
   the infra hosts).
.. Suggestion: Document the location of the swift account/object/container
   services (on separate physical hosts)

Networking for Object Storage (swift)
-------------------------------------

Ensure the proxy hosts for swift are on ``br-mgmt`` and ``br-storage``.
``br-storage`` handles the retrieval and upload of objects to the storage
nodes. ``br-mgmt`` handles the API requests.

Ensure storage hosts are on ``br-storage``. When using dedicated
replication, also ensure storage hosts are on ``br-repl``.
``br-storage`` handles the transfer of objects from the storage hosts to
the proxy and vice-versa.
``br-repl`` handles the replication of objects between storage hosts,
and is not needed by the proxy containers.

``br-repl`` is optional. Replication occurs over the ``br-storage``
interface when there is no ``br-repl`` replication bridge.

--------------

.. include:: navigation.txt
