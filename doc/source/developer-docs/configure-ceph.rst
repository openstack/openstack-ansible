`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Ceph client (optional)
======================================

Ceph is a massively scalable, open source, distributed storage system.

These links provide details on how to use Ceph with OpenStack:

* `Ceph Block Devices and OpenStack`_
* `Ceph - The De Facto Storage Backend for OpenStack`_ *(Hong Kong Summit
  talk)*
* `OpenStack Config Reference - Ceph RADOS Block Device (RBD)`_
* `OpenStack-Ansible and Ceph Working Example`_


.. _Ceph Block Devices and OpenStack: http://docs.ceph.com/docs/master/rbd/rbd-openstack/
.. _Ceph - The De Facto Storage Backend for OpenStack: https://www.openstack.org/summit/openstack-summit-hong-kong-2013/session-videos/presentation/ceph-the-de-facto-storage-backend-for-openstack
.. _OpenStack Config Reference - Ceph RADOS Block Device (RBD): http://docs.openstack.org/liberty/config-reference/content/ceph-rados.html
.. _OpenStack-Ansible and Ceph Working Example: https://www.openstackfaq.com/openstack-ansible-ceph/

.. note::

   Configuring Ceph storage servers is outside the scope of this documentation.

Authentication
~~~~~~~~~~~~~~

We recommend the ``cephx`` authentication method in the `Ceph
config reference`_. OpenStack-Ansible enables ``cephx`` by default for
the Ceph client. You can choose to override this setting by using the
``cephx`` Ansible variable:

.. code-block:: yaml

    cephx: False

Deploy Ceph on a trusted network if disabling ``cephx``.

.. _Ceph config reference: http://docs.ceph.com/docs/master/rados/configuration/auth-config-ref/

Configuration file overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible provides the ``ceph_conf_file`` variable. This allows
you to specify configuration file options to override the default
Ceph configuration:

.. code-block:: console

 ceph_conf_file: |
   [global]
   fsid = 4037aa5f-abde-4378-9470-f73dbd6ceaba
   mon_initial_members = mon1.example.local,mon2.example.local,mon3.example.local
   mon_host = 172.29.244.151,172.29.244.152,172.29.244.153
   auth_cluster_required = cephx
   auth_service_required = cephx
   auth_client_required = cephx

The use of the ``ceph_conf_file`` variable is optional. By default, OpenStack-Ansible
obtains a copy of ``ceph.conf`` from one of your Ceph monitors. This
transfer of ``ceph.conf`` requires the OpenStack-Ansible deployment host public key
to be deployed to all of the Ceph monitors. More details are available
here: `Deploying SSH Keys`_.

The following minimal example configuration sets nova and glance
to use ceph pools: ``ephemeral-vms`` and ``images`` respectively.
The example uses ``cephx`` authentication, and requires existing ``glance`` and
``cinder`` accounts for ``images`` and ``ephemeral-vms`` pools.

.. code-block:: console

    glance_default_store: rbd
    nova_libvirt_images_rbd_pool: ephemeral-vms

.. _Deploying SSH Keys: targethosts-prepare.html#deploying-ssh-keys

Monitors
~~~~~~~~

The `Ceph Monitor`_ maintains a master copy of the cluster map.
OpenStack-Ansible provides the ``ceph_mons`` variable and expects a list of
IP addresses for the Ceph Monitor servers in the deployment:

.. code-block:: yaml

  ceph_mons:
      - 172.29.244.151
      - 172.29.244.152
      - 172.29.244.153


.. _Ceph Monitor: http://docs.ceph.com/docs/master/rados/configuration/mon-config-ref/

--------------

.. include:: navigation.txt
