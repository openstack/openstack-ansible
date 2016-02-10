`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Compute (Nova) Service (optional)
-------------------------------------------------

The compute service (nova) handles the creation of virtual machines within an
OpenStack environment. Many of the default options used by OpenStack-Ansible
are found within `defaults/main.yml` within the nova role.

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

The `Ceph documentation for OpenStack`_ has additional information about these settings.

.. _Ceph documentation for OpenStack: http://docs.ceph.com/docs/master/rbd/rbd-openstack/

--------------

.. include:: navigation.txt
