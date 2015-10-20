`Home <index.html>`_ OpenStack-Ansible Installation Guide

Backup
------

You can configure Block Storage (cinder) to back up volumes to Object
Storage (swift) by setting variables. If enabled, the default
configuration backs up volumes to an Object Storage installation
accessible within your environment. Alternatively, you can set
``cinder_service_backup_swift_url`` and other variables listed below to
back up to an external Object Storage installation.

#. Add or edit the following line in the
   ``/etc/openstack_deploy/user_variables.yml`` file and set the value
   to ``True``:

   .. code-block:: yaml

       cinder_service_backup_program_enabled: True

#. By default, Block Storage will use the access credentials of the user
   initiating the backup. Default values are set in the
   ``/opt/openstack-ansible/playbooks/roles/os_cinder/defaults/main.yml``
   file. You can override those defaults by setting variables in
   ``/etc/openstack_deploy/user_variables.yml`` to change how Block
   Storage performs backups. As needed, add and edit any of the
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
       # obtain storage url from environment.
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
                 

During installation of Block Storage, the backup service is configured.
For more information about swift, refer to the Standalone Object Storage
Deployment guide.

--------------

.. include:: navigation.txt
