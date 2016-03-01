`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Ceph client (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ceph is a massively scalable, open source, distributed storage system.

These links provide more details around how to use Ceph with OpenStack:

* `Ceph Block Devices and OpenStack`_
* `Ceph - The De Facto Storage Backend for OpenStack`_ *(Hong Kong Summit
  talk)*
* `OpenStack Config Reference - Ceph RADOS Block Device (RBD)`_


.. _Ceph Block Devices and OpenStack: http://docs.ceph.com/docs/master/rbd/rbd-openstack/
.. _Ceph - The De Facto Storage Backend for OpenStack: https://www.openstack.org/summit/openstack-summit-hong-kong-2013/session-videos/presentation/ceph-the-de-facto-storage-backend-for-openstack
.. _OpenStack Config Reference - Ceph RADOS Block Device (RBD): http://docs.openstack.org/liberty/config-reference/content/ceph-rados.html

Configuring Ceph storage servers is outside the scope of this documentation.

Authentication
--------------

The ``cephx`` authentication method is strongly recommended in the `Ceph
config reference`_ and OpenStack-Ansible enables ``cephx`` by default for
the Ceph client.  Deployers may choose to override this setting by using the
``cephx`` Ansible variable:

.. code-block:: yaml

    cephx: False

Ceph **must** be deployed on a trusted network if ``cephx`` is disabled.

.. _Ceph config reference: http://docs.ceph.com/docs/master/rados/configuration/auth-config-ref/

Configuration file overrides
----------------------------

OpenStack-Ansible provides the ``ceph_conf_file`` variable that allows
deployers to specify configuration file options to override the default
Ceph configuration:

.. code-block:: console

    ceph_conf_file: |
      [global]
      fsid = 4037aa5f-abde-4378-9470-f73dbd6ceaba
      mon_initial_members = mon1.example.local,mon2.example.local,mon3.example.local
      mon_host = 10.16.5.40,10.16.5.41,10.16.5.42
      auth_cluster_required = cephx
      auth_service_required = cephx
      auth_client_required = cephx

Monitors
--------

The `Ceph Monitor`_ maintains a master copy of the cluster map.
OpenStack-Ansible provides the ``ceph_mons`` variable and expects a list of
IP addresses for the Ceph Monitor servers in the deployment:

.. code-block:: yaml

    ceph_mons: ['192.168.1.10', '192.168.1.11', '192.168.1.12']

.. _Ceph Monitor: http://docs.ceph.com/docs/master/rados/configuration/mon-config-ref/

--------------

.. include:: navigation.txt
