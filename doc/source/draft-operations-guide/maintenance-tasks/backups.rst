========
Back ups
========

For disaster recovery purposes, it is a good practice to perform regular
backups of the database, configuration files, network information, and
OpenStack service details in your environment. For an OpenStack cloud
deployed using OpenStack-Ansible, back up the ``/etc/openstack_deploy/``
directory.

Back up and restore the ``/etc/openstack_deploy/`` directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/`` directory contains a live
inventory, host structure, network information, passwords, and options that
are applied to the configuration files for each service in your OpenStack
deployment. Back up the ``/etc/openstack_deploy/`` directory to a remote
location.

To restore the ``/etc/openstack_deploy/`` directory, copy the backup of the
directory to your cloud environment.

Database backups and recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MySQL data is automatically backed up. To recover the database, use the
database backups and rebuild the Galera cluster. For more information, see
:ref:`galera-cluster-maintenance`.
