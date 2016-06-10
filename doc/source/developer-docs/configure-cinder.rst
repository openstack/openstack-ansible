`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Block (cinder) storage service (optional)
=========================================================

By default, the Block (cinder) storage service installs on the host itself using
the LVM backend.

.. note::

   While this is the default for cinder, using the LVM backend results in a
   Single Point of Failure. As a result of the volume service being deployed
   directly to the host, ``is_metal`` is ``true`` when using LVM.

NFS backend
~~~~~~~~~~~~

Edit ``/etc/openstack_deploy/openstack_user_config.yml`` and configure
the NFS client on each storage node if the NetApp backend is configured to use
an NFS storage protocol.

#. Add the ``cinder_backends`` stanza (which includes
   ``cinder_nfs_client``) under the ``container_vars`` stanza for
   each storage node:

   .. code-block:: yaml

       container_vars:
         cinder_backends:
           cinder_nfs_client:

#. Configure the location of the file that lists shares available to the
   block storage service. This configuration file must include
   ``nfs_shares_config``:

   .. code-block:: yaml

       nfs_shares_config: SHARE_CONFIG

   Replace ``SHARE_CONFIG`` with the location of the share
   configuration file. For example, ``/etc/cinder/nfs_shares``.

#. Configure one or more NFS shares:

   .. code-block:: yaml

       shares:
          - { ip: "NFS_HOST", share: "NFS_SHARE" }

   Replace ``NFS_HOST`` with the IP address or hostname of the NFS
   server, and the ``NFS_SHARE`` with the absolute path to an existing
   and accessible NFS share.

Backup
~~~~~~

You can configure cinder to backup volumes to Object
Storage (swift). Enable the default
configuration to back up volumes to a swift installation
accessible within your environment. Alternatively, you can set
``cinder_service_backup_swift_url`` and other variables to
back up to an external swift installation.

#. Add or edit the following line in the
   ``/etc/openstack_deploy/user_variables.yml`` file and set the value
   to ``True``:

   .. code-block:: yaml

       cinder_service_backup_program_enabled: True

#. By default, cinder uses the access credentials of the user
   initiating the backup. Default values are set in the
   ``/opt/openstack-ansible/playbooks/roles/os_cinder/defaults/main.yml``
   file. You can override those defaults by setting variables in
   ``/etc/openstack_deploy/user_variables.yml`` to change how cinder
   performs backups. Add and edit any of the
   following variables to the
   ``/etc/openstack_deploy/user_variables.yml`` file:

   .. code-block:: yaml

       ...
       cinder_service_backup_swift_auth: per_user
       # Options include 'per_user' or 'single_user'. We default to
       # 'per_user' so that backups are saved to a user's swift
       # account.
       cinder_service_backup_swift_url:
       # This is your swift storage url when using 'per_user', or keystone
       # endpoint when using 'single_user'.  When using 'per_user', you
       # can leave this as empty or as None to allow cinder-backup to
       # obtain a storage url from environment.
       cinder_service_backup_swift_url:
       cinder_service_backup_swift_auth_version: 2
       cinder_service_backup_swift_user:
       cinder_service_backup_swift_tenant:
       cinder_service_backup_swift_key:
       cinder_service_backup_swift_container: volumebackups
       cinder_service_backup_swift_object_size: 52428800
       cinder_service_backup_swift_retry_attempts: 3
       cinder_service_backup_swift_retry_backoff: 2
       cinder_service_backup_compression_algorithm: zlib
       cinder_service_backup_metadata_version: 2

During installation of cinder, the backup service is configured.


Using Ceph for cinder backups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can deploy Ceph to hold cinder volume backups.
To get started, set the ``cinder_service_backup_driver`` Ansible
variable:

.. code-block:: yaml

    cinder_service_backup_driver: cinder.backup.drivers.ceph

Configure the Ceph user and the pool to use for backups. The defaults
are shown here:

.. code-block:: yaml

    cinder_service_backup_ceph_user: cinder-backup
    cinder_service_backup_ceph_pool: backups


Availability zones
~~~~~~~~~~~~~~~~~~

Create multiple availability zones to manage cinder storage hosts. Edit the
``/etc/openstack_deploy/openstack_user_config.yml`` and
``/etc/openstack_deploy/user_variables.yml`` files to set up
availability zones.

#. For each cinder storage host, configure the availability zone under
   the ``container_vars`` stanza:

   .. code-block:: yaml

       cinder_storage_availability_zone: CINDERAZ

   Replace ``CINDERAZ`` with a suitable name. For example
   ``cinderAZ_2``.

#. If more than one availability zone is created, configure the default
   availability zone for all the hosts by creating a
   ``cinder_default_availability_zone`` in your
   ``/etc/openstack_deploy/user_variables.yml``

   .. code-block:: yaml

       cinder_default_availability_zone: CINDERAZ_DEFAULT

   Replace ``CINDERAZ_DEFAULT`` with a suitable name. For example,
   ``cinderAZ_1``. The default availability zone should be the same
   for all cinder hosts.

OpenStack Dashboard (horizon) configuration for cinder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure variables to set the behavior for cinder
volume management in OpenStack Dashboard (horizon).
By default, no horizon configuration is set.

#. The default destination availability zone is ``nova`` if you use
   multiple availability zones and ``cinder_default_availability_zone``
   has no definition.  Volume creation with
   horizon might fail if there is no availability zone named ``nova``.
   Set ``cinder_default_availability_zone`` to an appropriate
   availability zone name so that :guilabel:`Any availability zone`
   works in horizon.

#. horizon does not populate the volume type by default. On the new
   volume page, a request for the creation of a volume with the
   default parameters fails. Set ``cinder_default_volume_type`` so
   that a volume creation request without an explicit volume type
   succeeds.


Configuring cinder to use LVM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. List the ``container_vars`` that contain the storage options for the target host.

   .. note::

      The vars related to the cinder availability zone and the
      ``limit_container_types`` are optional.


   To configure an LVM, utilize the following example:

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

To use another backend in a
container instead of bare metal, edit
the ``/etc/openstack_deploy/env.d/cinder.yml`` and remove the
``is_metal: true`` stanza under the ``cinder_volumes_container`` properties.

Configuring cinder to use Ceph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order for cinder to use Ceph, it is necessary to configure for both
the API and backend. When using any forms of network storage
(iSCSI, NFS, Ceph) for cinder, the API containers can be considered
as backend servers. A separate storage host is not required.

In ``env.d/cinder.yml`` remove ``is_metal: true``

#. List of target hosts on which to deploy the cinder API. We recommend
   that a minumum of three target hosts are used for this service.

   .. code-block:: yaml

       storage-infra_hosts:
         infra1:
           ip: 172.29.236.101
         infra2:
           ip: 172.29.236.102
         infra3:
           ip: 172.29.236.103


   To configure an RBD backend, utilize the following example:

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


In ``user_variables.yml``:

   .. code-block:: yaml


    ceph_mons:
      - 172.29.244.151
      - 172.29.244.152
      - 172.29.244.153


In ``openstack_user_config.yml``:

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



This link provides a complete working example of Ceph setup and
integration with cinder (nova and glance included):

* `OpenStack-Ansible and Ceph Working Example`_

.. _OpenStack-Ansible and Ceph Working Example: https://www.openstackfaq.com/openstack-ansible-ceph/


Configuring cinder to use a NetApp appliance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a NetApp storage appliance back end, edit the
``/etc/openstack_deploy/openstack_user_config.yml`` file and configure
each storage node that will use it.

.. note::

   Ensure that the NAS Team enables ``httpd.admin.access``.

#. Add the ``netapp`` stanza under the ``cinder_backends`` stanza for
   each storage node:

   .. code-block:: yaml

       cinder_backends:
         netapp:

   The options in subsequent steps fit under the ``netapp`` stanza.

   The backend name is arbitrary and becomes a volume type within cinder.

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

   For the NFS protocol, specify the location of the
   configuration file that lists the shares available to cinder:

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

   Replace ``BACKEND_NAME`` with a value that provides a hint
   for the cinder scheduler. For example, ``NETAPP_iSCSI``.

#. Ensure the ``openstack_user_config.yml`` configuration is
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

