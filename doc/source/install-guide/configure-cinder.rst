`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Block Storage service (optional)
------------------------------------------------

.. toctree::

   configure-cinder-nfs.rst
   configure-cinder-backup.rst
   configure-cinder-az.rst
   configure-cinder-horizon.rst

By default, the Block Storage service installs on the host itself using the LVM
backend. While this is the default for cinder it should be noted that using a
LVM backend results in a Single Point of Failure. As a result of the volume
service being deployed directly to the host is_metal is true when using LVM.

Configuring Cinder to use LVM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. List the container_vars which contain the storage options for this target host.
   Note that the vars related to the Cinder availability zone and the
   limit_container_types are optional.


   To configure an LVM you would utilize the following example:

   .. code-block:: yaml

        storage_hosts:
         Infra01:
           ip: 172.29.236.16
           container_vars:
             cinder_storage_availability_zone: cinderAZ_1
             cinder_default_availability_zone: cinderAZ_1
             cinder_backends:
               lvm:
                 volume_backend_name: LVM_iSCSI
                 volume_driver: cinder.volume.drivers.lvm.LVMVolumeDriver
                 volume_group: cinder-volumes
                 iscsi_ip_address: "{{ storage_address }}"
               limit_container_types: cinder_volume

If you rather use another backend (like Ceph, NetApp, etc.) in a
container instead of bare metal, you may edit
the ``/etc/openstack_deploy/env.d/cinder.yml`` and remove the
``is_metal: true`` stanza under the cinder_volumes_container properties.

Configuring Cinder to use Ceph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order for Cinder to use Ceph it will be necessary to configure for both
the API and backend. When using any forms of network storage
(iSCSI, NFS, Ceph ) for cinder, the API containers can be considered
as backend servers, so a separate storage host is not required.

In ``env.d/cinder.yml`` remove/disable ``is_metal: true``

#. List of target hosts on which to deploy the cinder API. It is recommended
   that a minumum of three target hosts are used for this service.

   .. code-block:: yaml

       storage-infra_hosts:
         infra1:
           ip: 172.29.236.101
         infra2:
           ip: 172.29.236.102
         infra3:
           ip: 172.29.236.103


   To configure an RBD backend utilize the following example:

   .. code-block:: yaml

       container_vars:
       cinder_storage_availability_zone: cinderAZ_3
       cinder_default_availability_zone: cinderAZ_1
       cinder_backends:
         limit_container_types: cinder_volume
         volumes_hdd:
           volume_driver: cinder.volume.drivers.rbd.RBDDriver
           rbd_pool: volumes_hdd
           rbd_ceph_conf: /etc/ceph/ceph.conf
           rbd_flatten_volume_from_snapshot: 'false'
           rbd_max_clone_depth: 5
           rbd_store_chunk_size: 4
           rados_connect_timeout: -1
           volume_backend_name: volumes_hdd
           rbd_user: "{{ cinder_ceph_client }}"
           rbd_secret_uuid: "{{ cinder_ceph_client_uuid }}"


The following example sets cinder to use the ``cinder_volumes`` pool.
The example uses cephx authentication and requires existing ``cinder``
account for ``cinder_volumes`` pool.


in ``user_variables.yml``

   .. code-block:: yaml


    ceph_mons:
      - 172.29.244.151
      - 172.29.244.152
      - 172.29.244.153




in ``openstack_user_config.yml``

  .. code-block:: yaml


   storage_hosts:
    infra1:
     ip: 172.29.236.101
     container_vars:
      cinder_backends:
        limit_container_types: cinder_volume
        rbd:
          volume_group: cinder-volumes
          volume_driver: cinder.volume.drivers.rbd.RBDDriver
          volume_backend_name: rbd
          rbd_pool: cinder-volumes
          rbd_ceph_conf: /etc/ceph/ceph.conf
          rbd_user: cinder
    infra2:
     ip: 172.29.236.102
     container_vars:
      cinder_backends:
        limit_container_types: cinder_volume
        rbd:
          volume_group: cinder-volumes
          volume_driver: cinder.volume.drivers.rbd.RBDDriver
          volume_backend_name: rbd
          rbd_pool: cinder-volumes
          rbd_ceph_conf: /etc/ceph/ceph.conf
          rbd_user: cinder
    infra3:
     ip: 172.29.236.103
     container_vars:
      cinder_backends:
        limit_container_types: cinder_volume
        rbd:
          volume_group: cinder-volumes
          volume_driver: cinder.volume.drivers.rbd.RBDDriver
          volume_backend_name: rbd
          rbd_pool: cinder-volumes
          rbd_ceph_conf: /etc/ceph/ceph.conf
          rbd_user: cinder



This link provides a complete working example of ceph setup and
integration with cinder (nova and glance included)

* `OpenStack-Ansible and Ceph Working Example`_

.. _OpenStack-Ansible and Ceph Working Example: https://www.openstackfaq.com/openstack-ansible-ceph/



Configuring Cinder to use a NetApp appliance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a NetApp storage appliance back end, edit the
``/etc/openstack_deploy/openstack_user_config.yml`` file and configure
each storage node that will use it:

Ensure that the NAS Team enables httpd.admin.access.

#. Add the ``netapp`` stanza under the ``cinder_backends`` stanza for
   each storage node:

   .. code-block:: yaml

       cinder_backends:
         netapp:

   The options in subsequent steps fit under the ``netapp`` stanza.

   The back end name is arbitrary and becomes a volume type within the
   Block Storage service.

#. Configure the storage family:

   .. code-block:: yaml

       netapp_storage_family: STORAGE_FAMILY

   Replace ``STORAGE_FAMILY`` with ``ontap_7mode`` for Data ONTAP
   operating in 7-mode or ``ontap_cluster`` for Data ONTAP operating as
   a cluster.

#. Configure the storage protocol:

   .. code-block:: yaml

       netapp_storage_protocol: STORAGE_PROTOCOL

   Replace ``STORAGE_PROTOCOL`` with ``iscsi`` for iSCSI or ``nfs``
   for NFS.

   For the NFS protocol, you must also specify the location of the
   configuration file that lists the shares available to the Block
   Storage service:

   .. code-block:: yaml

       nfs_shares_config: SHARE_CONFIG

   Replace ``SHARE_CONFIG`` with the location of the share
   configuration file. For example, ``/etc/cinder/nfs_shares``.

#. Configure the server:

   .. code-block:: yaml

       netapp_server_hostname: SERVER_HOSTNAME

   Replace ``SERVER_HOSTNAME`` with the hostnames for both netapp
   controllers.

#. Configure the server API port:

   .. code-block:: yaml

       netapp_server_port: PORT_NUMBER

   Replace ``PORT_NUMBER`` with 80 for HTTP or 443 for HTTPS.

#. Configure the server credentials:

   .. code-block:: yaml

       netapp_login: USER_NAME
       netapp_password: PASSWORD

   Replace ``USER_NAME`` and ``PASSWORD`` with the appropriate
   values.

#. Select the NetApp driver:

   .. code-block:: yaml

       volume_driver: cinder.volume.drivers.netapp.common.NetAppDriver

#. Configure the volume back end name:

   .. code-block:: yaml

       volume_backend_name: BACKEND_NAME

   Replace ``BACKEND_NAME`` with a suitable value that provides a hint
   for the Block Storage scheduler. For example, ``NETAPP_iSCSI``.

#. Check that the ``openstack_user_config.yml`` configuration is
   accurate:

   .. code-block:: yaml

       storage_hosts:
         Infra01:
           ip: 172.29.236.16
           container_vars:
             cinder_backends:
               limit_container_types: cinder_volume
               netapp:
                 netapp_storage_family: ontap_7mode
                 netapp_storage_protocol: nfs
                 netapp_server_hostname: 111.222.333.444
                 netapp_server_port: 80
                 netapp_login: openstack_cinder
                 netapp_password: password
                 volume_driver: cinder.volume.drivers.netapp.common.NetAppDriver
                 volume_backend_name: NETAPP_NFS

   For ``netapp_server_hostname``, specify the IP address of the Data
   ONTAP server. Include iSCSI or NFS for the
   ``netapp_storage_family`` depending on the configuration. Add 80 if
   using HTTP or 443 if using HTTPS for ``netapp_server_port``.

   The ``cinder-volume.yml`` playbook will automatically install the
   ``nfs-common`` file across the hosts, transitioning from an LVM to a
   NetApp back end.

--------------

.. include:: navigation.txt
