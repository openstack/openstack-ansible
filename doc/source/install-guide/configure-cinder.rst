`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Block Storage service (optional)
------------------------------------------------

.. toctree::

   configure-cinder-nfs.rst
   configure-cinder-backup.rst
   configure-cinder-az.rst

By default, the Block Storage service uses the LVM back end. Therefore
the container hosting the Block Storage service has to be considered
as is_metal.

If you rather use another backend (like NetApp, Ceph, etc.) in a
container instead of bare metal, you may edit
the ``/etc/openstack_deploy/env.d/cinder.yml`` and remove the
``is_metal: true`` stanza under the cinder_volumes_container properties.

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
         xxxxxx-Infra01:
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
