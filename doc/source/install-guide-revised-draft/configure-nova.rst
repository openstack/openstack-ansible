`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Compute (nova) service (optional)
=================================================

The Compute service (nova) handles the creation of virtual machines within an
OpenStack environment. Many of the default options used by OpenStack-Ansible
are found within ``defaults/main.yml`` within the nova role.

Availability zones
~~~~~~~~~~~~~~~~~~

Deployers with multiple availability zones can set the
``nova_default_schedule_zone`` Ansible variable to specify an availability zone
for new requests. This is useful in environments with different types
of hypervisors, where builds are sent to certain hardware types based on
their resource requirements.

For example, if you have servers running on two racks without sharing the PDU.
These two racks can be grouped into two availability zones.
When one rack loses power, the other one still works. By spreading
your containers onto the two racks (availability zones), you will
improve your service availability.

Block device tuning for Ceph (RBD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enabling Ceph and defining ``nova_libvirt_images_rbd_pool`` changes two
libvirt configurations by default:

* hw_disk_discard: ``unmap``
* disk_cachemodes: ``network=writeback``

Setting ``hw_disk_discard`` to ``unmap`` in libvirt enables
discard (sometimes called TRIM) support for the underlying block device. This
allows reclaiming of unused blocks on the underlying disks.

Setting ``disk_cachemodes`` to ``network=writeback`` allows data to be written
into a cache on each change, but those changes are flushed to disk at a regular
interval. This can increase write performance on Ceph block devices.

You have the option to customize these settings using two Ansible
variables (defaults shown here):

.. code-block:: yaml

    nova_libvirt_hw_disk_discard: 'unmap'
    nova_libvirt_disk_cachemodes: 'network=writeback'

You can disable discard by setting ``nova_libvirt_hw_disk_discard`` to
``ignore``.  The ``nova_libvirt_disk_cachemodes`` can be set to an empty
string to disable ``network=writeback``.

The following minimal example configuration sets nova to use the
``ephemeral-vms`` Ceph pool. The following example uses cephx authentication, and
requires an existing ``cinder`` account for the ``ephemeral-vms`` pool:

.. code-block:: console

    nova_libvirt_images_rbd_pool: ephemeral-vms
    ceph_mons:
      - 172.29.244.151
      - 172.29.244.152
      - 172.29.244.153


If you have a different Ceph username for the pool, use it as:

.. code-block:: console

   cinder_ceph_client: <ceph-username>

* The `Ceph documentation for OpenStack`_ has additional information about these settings.
* `OpenStack-Ansible and Ceph Working Example`_


.. _Ceph documentation for OpenStack: http://docs.ceph.com/docs/master/rbd/rbd-openstack/
.. _OpenStack-Ansible and Ceph Working Example: https://www.openstackfaq.com/openstack-ansible-ceph/



Config drive
~~~~~~~~~~~~

By default, OpenStack-Ansible does not configure nova to force config drives
to be provisioned with every instance that nova builds. The metadata service
provides configuration information that is used by ``cloud-init`` inside the
instance. Config drives are only necessary when an instance does not have
``cloud-init`` installed or does not have support for handling metadata.

A deployer can set an Ansible variable to force config drives to be deployed
with every virtual machine:

.. code-block:: yaml

    nova_force_config_drive: True

Certain formats of config drives can prevent instances from migrating properly
between hypervisors. If you need forced config drives and the ability
to migrate instances, set the config drive format to ``vfat`` using
the ``nova_nova_conf_overrides`` variable:

.. code-block:: yaml

    nova_nova_conf_overrides:
      DEFAULT:
        config_drive_format: vfat
        force_config_drive: True

Libvirtd connectivity and authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, OpenStack-Ansible configures the libvirt daemon in the following
way:

* TLS connections are enabled
* TCP plaintext connections are disabled
* Authentication over TCP connections uses SASL

You can customize these settings using the following Ansible variables:

.. code-block:: yaml

    # Enable libvirtd's TLS listener
    nova_libvirtd_listen_tls: 1

    # Disable libvirtd's plaintext TCP listener
    nova_libvirtd_listen_tcp: 0

    # Use SASL for authentication
    nova_libvirtd_auth_tcp: sasl

Multipath
~~~~~~~~~

Nova supports multipath for iSCSI-based storage. Enable multipath support in
nova through a configuration override:

.. code-block:: yaml

    nova_nova_conf_overrides:
      libvirt:
          iscsi_use_multipath: true

Shared storage and synchronized UID/GID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify a custom UID for the nova user and GID for the nova group
to ensure they are identical on each host. This is helpful when using shared
storage on Compute nodes because it allows instances to migrate without
filesystem ownership failures.

By default, Ansible creates the nova user and group without specifying the
UID or GID. To specify custom values for the UID or GID, set the following
Ansible variables:

.. code-block:: yaml

    nova_system_user_uid = <specify a UID>
    nova_system_group_gid = <specify a GID>

.. warning::

   Setting this value after deploying an environment with
   OpenStack-Ansible can cause failures, errors, and general instability. These
   values should only be set once before deploying an OpenStack environment
   and then never changed.

--------------

.. include:: navigation.txt
