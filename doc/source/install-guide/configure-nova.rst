`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Compute (Nova) Service (optional)
-------------------------------------------------

The compute service (nova) handles the creation of virtual machines within an
OpenStack environment. Many of the default options used by OpenStack-Ansible
are found within `defaults/main.yml` within the nova role.

Availability zones
~~~~~~~~~~~~~~~~~~

Deployers with multiple availability zones (AZ's) can set the
``nova_default_schedule_zone`` Ansible variable to specify an AZ to use for
instance build requests where an AZ is not provided. This could be useful in
environments with different types of hypervisors where builds are sent to
certain hardware types based on their resource requirements.

For example, if a deployer has some servers with spinning hard disks and others
with SSDs, they can set the default AZ to one that uses only spinning disks (to
save costs). To build an instance using SSDs, users must select an AZ that
includes SSDs and provide that AZ in their instance build request.

Block device tuning for Ceph (RBD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Ceph is enabled and ``nova_libvirt_images_rbd_pool`` is defined, two
libvirt configurations will be changed by default:

* hw_disk_discard: ``unmap``
* disk_cachemodes: ``network=writeback``

Setting ``hw_disk_discard`` to ``unmap`` in libvirt will enable
discard (sometimes called TRIM) support for the underlying block device. This
allows for unused blocks to be reclaimed on the underlying disks.

Setting ``disk_cachemodes`` to ``network=writeback`` allows data to be written
into a cache on each change, but those changes are flushed to disk at a regular
interval.  This can increase write performance on Ceph block devices.

Deployers have the option to customize these settings using two Ansible
variables (defaults shown here):

.. code-block:: yaml

    nova_libvirt_hw_disk_discard: 'unmap'
    nova_libvirt_disk_cachemodes: 'network=writeback'

Deployers can disable discard by setting ``nova_libvirt_hw_disk_discard`` to
``ignore``.  The ``nova_libvirt_disk_cachemodes`` can be set to an empty
string to disable ``network=writeback``.

The `Ceph documentation for OpenStack`_ has additional information about these
settings.

.. _Ceph documentation for OpenStack: http://docs.ceph.com/docs/master/rbd/rbd-openstack/

Config Drive
~~~~~~~~~~~~

By default, OpenStack-Ansible will not configure Nova to force config drives
to be provisioned with every instance that Nova builds.  The metadata service
provides configuration information that can be used by cloud-init inside the
instance.  Config drives are only necessary when an instance doesn't have
cloud-init installed or doesn't have support for handling metadata.

A deployer can set an Ansible variable to force config drives to be deployed
with every virtual machine:

.. code-block:: yaml

    nova_force_config_drive: True

Certain formats of config drives can prevent instances from migrating properly
between hypervisors.  If a deployer needs forced config drives and the ability
to migrate instances, the config drive format should be set to ``vfat`` using
the ``nova_nova_conf_overrides`` variable:

.. code-block:: yaml

    nova_nova_conf_overrides:
      DEFAULT:
        config_drive_format: vfat
        force_config_drive: True

Libvirtd Connectivity and Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, OpenStack-Ansible configures the libvirt daemon in the following
way:

* TLS connections are enabled
* TCP plaintext connections are disabled
* Authentication over TCP connections uses SASL

Deployers can customize these settings using the Ansible variables shown
below:

.. code-block:: yaml

    # Enable libvirtd's TLS listener
    nova_libvirtd_listen_tls: 1

    # Disable libvirtd's plaintext TCP listener
    nova_libvirtd_listen_tcp: 0

    # Use SASL for authentication
    nova_libvirtd_auth_tcp: sasl

Multipath
~~~~~~~~~

Nova supports multipath for iSCSI-based storage.  Deployers can enable
multipath support in nova through a configuration override:

.. code-block:: yaml

    nova_nova_conf_overrides:
      libvirt:
          iscsi_use_multipath: true

Shared storage and synchronized UID/GID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deployers can specify a custom UID for the nova user and GID for the nova group
to ensure they are identical on each host. This is helpful when using shared
storage on compute nodes because it allows instances to migrate without
filesystem ownership failures.

By default, Ansible will create the nova user and group without specifying the
UID or GID. To specify custom values for the UID/GID, set the following
Ansible variables:

.. code-block:: yaml

    nova_system_user_uid = <specify a UID>
    nova_system_group_gid = <specify a GID>

**WARNING:** Setting this value **after** deploying an environment with
OpenStack-Ansible can cause failures, errors, and general instability. These
values should only be set once **before** deploying an OpenStack environment
and then never changed.

--------------

.. include:: navigation.txt
