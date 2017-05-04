=============================
Nova instances live migration
=============================

Nova is capable of live migration instances from one host to
a different host to support various operational tasks including:

 * Host Maintenance
 * Host capacity management
 * Resizing and moving instances to better hardware


Nova configuration drive implication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on the OpenStack-Ansible version in use, Nova can
be configured to force configuration drive attachments to instances.
In this case, a ISO9660 CD-ROM image will be made available to the
instance via the ``/mnt`` mount point. This can be used by tools,
such as cloud-init, to gain access to instance metadata. This is
an alternative way of accessing the Nova EC2-style Metadata.

To allow live migration of Nova instances, this forced provisioning
of the config (CD-ROM) drive needs either be turned off, or the format of
the configuration drive needs to be changed to a disk format like vfat, a
format which both Linux and Windows instances can access.

This work around is required for all Libvirt versions prior 1.2.17.

To turn off the forced provisioning of the config drive, add the following
override to the ``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   nova_force_config_drive: False

To change the format of the configuration drive, to a hard disk style format,
use the following configuration inside the same
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   nova_nova_conf_overrides:
     DEFAULT:
       config_drive_format: vfat
       force_config_drive: false


Tunneling versus direct transport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the default configuration, Nova determines the correct transport
URL for how to transfer the data from one host to the other.
Depending on the ``nova_virt_type`` override the following configurations
are used:

 * kvm defaults to ``qemu+tcp://%s/system``
 * qemu defaults to ``qemu+tcp://%s/system``
 * xen defaults to ``xenmigr://%s/system``

Libvirt TCP port to transfer the data to migrate.

OpenStack-Ansible changes the default setting and used a encrypted SSH
connection to transfer the instance data.

.. code-block:: yaml

   live_migration_uri = "qemu+ssh://nova@%s/system?no_verify=1&keyfile={{ nova_system_home_folder }}/.ssh/id_rsa"

Other configurations can be configured inside the
``/etc/openstack_deploy/user_variables.yml`` file:

.. code-block:: yaml

   nova_nova_conf_overrides:
     libvirt:
       live_migration_completion_timeout: 0
       live_migration_progress_timeout: 0
       live_migration_uri: "qemu+ssh://nova@%s/system?keyfile=/var/lib/nova/.ssh/id_rsa&no_verify=1"


Local versus shared storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, live migration assumes that your Nova instances are stored
on shared storage and KVM/Libvirt only need to synchronize the
memory and base image of the Nova instance to the new host.
Live migrations on local storage will fail as a result of that assumption.
Migrations with local storage can be accomplished by allowing instance disk
migrations with the ``--block-migrate`` option.

Additional Nova flavor features like ephemeral storage or swap have an
impact on live migration performance and success.

Cinder attached volumes also require a Libvirt version larger or equal to
1.2.17.

Executing the migration
~~~~~~~~~~~~~~~~~~~~~~~

The live migration is accessible via the nova client.

.. code-block:: console

    nova live-migration [--block-migrate] [--force] <uuid> [<host>]

Examplarery live migration on a local storage:

.. code-block:: console

    nova live-migration --block-migrate <uuid of the instance> <nova host>


Monitoring the status
~~~~~~~~~~~~~~~~~~~~~

Once the live migration request has been accepted, the status can be
monitored with the nova client:

.. code-block:: console

    nova migration-list

    +-----+------------+-----------+----------------+--------------+-----------+-----------+---------------+------------+------------+------------+------------+-----------------+
    | Id | Source Node | Dest Node | Source Compute | Dest Compute | Dest Host | Status    | Instance UUID | Old Flavor | New Flavor | Created At | Updated At | Type            |
    +----+-------------+-----------+----------------+--------------+-----------+-----------+---------------+------------+------------+------------+------------+-----------------+
    | 6  | -           | -         | compute01      | compute02    | -         | preparing | f95ee17a-d09c | 7          | 7          | date       | date       | live-migration  |
    +----+-------------+-----------+----------------+--------------+-----------+-----------+---------------+------------+------------+------------+------------+-----------------+

To filter the list, the options  ``--host`` or ``--status`` can be used:

.. code-block:: console

    nova migration-list --status error

In cases where the live migration fails, both the source and destination
compute nodes need to be checked for errors. Usually it is sufficient
to search for the instance UUID only to find errors related to the
live migration.

Other forms of instance migration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Besides the live migration, Nova offers the option to migrate entire hosts
in a online (live) or offline (cold) migration.

The following nova client commands are provided:

 * ``host-evacuate-live``

   Live migrate all instances of the specified host
   to other hosts if resource utilzation allows.
   It is best to use shared storage like Ceph or NFS
   for host evacuation.

 * ``host-servers-migrate``

   This command is similar to host evacuation but
   migrates all instances off the specified host while
   they are shutdown.

 * ``resize``

   Changes the flavor of an Nova instance (increase) while rebooting
   and also migrates (cold) the instance to a new host to accommodate
   the new resource requirements. This operation can take considerate
   amount of time, depending disk image sizes.

