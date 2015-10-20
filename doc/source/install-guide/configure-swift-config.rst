`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the service
-----------------------

**Procedure 5.2. Updating the Object Storage configuration ``swift.yml``
file**

#. Copy the ``/etc/openstack_deploy/conf.d/swift.yml.example`` file to
   ``/etc/openstack_deploy/conf.d/swift.yml``:

   .. code-block:: shell-session

       # cp /etc/openstack_deploy/conf.d/swift.yml.example \
           /etc/openstack_deploy/conf.d/swift.yml

#. Update the global override values:

   .. code-block:: yaml

       # global_overrides:
       #   swift:
       #     part_power: 8
       #     weight: 100
       #     min_part_hours: 1
       #     repl_number: 3
       #     storage_network: 'br-storage'
       #     replication_network: 'br-repl'
       #     drives:
       #       - name: sdc
       #       - name: sdd
       #       - name: sde
       #       - name: sdf
       #     mount_point: /mnt
       #     account:
       #     container:
       #     storage_policies:
       #       - policy:
       #           name: gold
       #           index: 0
       #           default: True
       #       - policy:
       #           name: silver
       #           index: 1
       #           repl_number: 3
       #           deprecated: True
               

   ``part_power``
       Set the partition power value based on the total amount of
       storage the entire ring will use.

       Multiply the maximum number of drives ever used with this Object
       Storage installation by 100 and round that value up to the
       closest power of two value. For example, a maximum of six drives,
       times 100, equals 600. The nearest power of two above 600 is two
       to the power of nine, so the partition power is nine. The
       partition power cannot be changed after the Object Storage rings
       are built.

   ``weight``
       The default weight is 100. If the drives are different sizes, set
       the weight value to avoid uneven distribution of data. For
       example, a 1 TB disk would have a weight of 100, while a 2 TB
       drive would have a weight of 200.

   ``min_part_hours``
       The default value is 1. Set the minimum partition hours to the
       amount of time to lock a partition's replicas after a partition
       has been moved. Moving multiple replicas at the same time might
       make data inaccessible. This value can be set separately in the
       swift, container, account, and policy sections with the value in
       lower sections superseding the value in the swift section.

   ``repl_number``
       The default value is 3. Set the replication number to the number
       of replicas of each object. This value can be set separately in
       the swift, container, account, and policy sections with the value
       in the more granular sections superseding the value in the swift
       section.

   ``storage_network``
       By default, the swift services will listen on the default
       management IP. Optionally, specify the interface of the storage
       network.

       If the ``storage_network`` is not set, but the ``storage_ips``
       per host are set (or the ``storage_ip`` is not on the
       ``storage_network`` interface) the proxy server will not be able
       to connect to the storage services.

   ``replication_network``
       Optionally, specify a dedicated replication network interface, so
       dedicated replication can be setup. If this value is not
       specified, no dedicated ``replication_network`` is set.

       As with the ``storage_network``, if the ``repl_ip`` is not set on
       the ``replication_network`` interface, replication will not work
       properly.

   ``drives``
       Set the default drives per host. This is useful when all hosts
       have the same drives. These can be overridden on a per host
       basis.

   ``mount_point``
       Set the ``mount_point`` value to the location where the swift
       drives are mounted. For example, with a mount point of ``/mnt``
       and a drive of ``sdc``, a drive is mounted at ``/mnt/sdc`` on the
       ``swift_host``. This can be overridden on a per-host basis.

   ``storage_policies``
       Storage policies determine on which hardware data is stored, how
       the data is stored across that hardware, and in which region the
       data resides. Each storage policy must have an unique ``name``
       and a unique ``index``. There must be a storage policy with an
       index of 0 in the ``swift.yml`` file to use any legacy containers
       created before storage policies were instituted.

   ``default``
       Set the default value to *yes* for at least one policy. This is
       the default storage policy for any non-legacy containers that are
       created.

   ``deprecated``
       Set the deprecated value to *yes* to turn off storage policies.

       For account and container rings, ``min_part_hours`` and
       ``repl_number`` are the only values that can be set. Setting them
       in this section overrides the defaults for the specific ring.

#. Update the Object Storage proxy hosts values:

   .. code-block:: yaml

       # swift-proxy_hosts:
       #   infra-node1:
       #     ip: 192.0.2.1
       #   infra-node2:
       #     ip: 192.0.2.2
       #   infra-node3:
       #     ip: 192.0.2.3

   ``swift-proxy_hosts``
       Set the ``IP`` address of the hosts that Ansible will connect to
       to deploy the swift-proxy containers. The ``swift-proxy_hosts``
       value should match the infra nodes.

#. Update the Object Storage hosts values:

   .. code-block:: yaml

       # swift_hosts:
       #   swift-node1:
       #     ip: 192.0.2.4
       #     container_vars:
       #       swift_vars:
       #         zone: 0
       #   swift-node2:
       #     ip: 192.0.2.5
       #     container_vars:
       #       swift_vars:
       #         zone: 1
       #   swift-node3:
       #     ip: 192.0.2.6
       #     container_vars:
       #       swift_vars:
       #         zone: 2
       #   swift-node4:
       #     ip: 192.0.2.7
       #     container_vars:
       #       swift_vars:
       #         zone: 3
       #   swift-node5:
       #     ip: 192.0.2.8
       #     container_vars:
       #       swift_vars:
       #         storage_ip: 198.51.100.8
       #         repl_ip: 203.0.113.8
       #         zone: 4
       #         region: 3
       #         weight: 200
       #         groups:
       #           - account
       #           - container
       #           - silver
       #         drives:
       #           - name: sdb
       #             storage_ip: 198.51.100.9
       #             repl_ip: 203.0.113.9
       #             weight: 75
       #             groups:
       #               - gold
       #           - name: sdc
       #           - name: sdd
       #           - name: sde
       #           - name: sdf

   ``swift_hosts``
       Specify the hosts to be used as the storage nodes. The ``ip`` is
       the address of the host to which Ansible connects. Set the name
       and IP address of each Object Storage host. The ``swift_hosts``
       section is not required.

   ``swift_vars``
       Contains the Object Storage host specific values.

   ``storage_ip`` and ``repl_ip``
       These values are based on the IP addresses of the host's
       ``storage_network`` or ``replication_network``. For example, if
       the ``storage_network`` is ``br-storage`` and host1 has an IP
       address of 1.1.1.1 on ``br-storage``, then that is the IP address
       that will be used for ``storage_ip``. If only the ``storage_ip``
       is specified then the ``repl_ip`` defaults to the ``storage_ip``.
       If neither are specified, both will default to the host IP
       address.

       Overriding these values on a host or drive basis can cause
       problems if the IP address that the service listens on is based
       on a specified ``storage_network`` or ``replication_network`` and
       the ring is set to a different IP address.

   ``zone``
       The default is 0. Optionally, set the Object Storage zone for the
       ring.

   ``region``
       Optionally, set the Object Storage region for the ring.

   ``weight``
       The default weight is 100. If the drives are different sizes, set
       the weight value to avoid uneven distribution of data. This value
       can be specified on a host or drive basis (if specified at both,
       the drive setting takes precedence).

   ``groups``
       Set the groups to list the rings to which a host's drive belongs.
       This can be set on a per drive basis which will override the host
       setting.

   ``drives``
       Set the names of the drives on this Object Storage host. At least
       one name must be specified.

   ``weight``
       The default weight is 100. If the drives are different sizes, set
       the weight value to avoid uneven distribution of data. This value
       can be specified on a host or drive basis (if specified at both,
       the drive setting takes precedence).

   In the following example, ``swift-node5`` shows values in the
   ``swift_hosts`` section that will override the global values. Groups
   are set, which overrides the global settings for drive ``sdb``. The
   weight is overridden for the host and specifically adjusted on drive
   ``sdb``. Also, the ``storage_ip`` and ``repl_ip`` are set differently
   for ``sdb``.

   .. code-block:: yaml

       #  swift-node5:
       #     ip: 192.0.2.8
       #     container_vars:
       #       swift_vars:
       #         storage_ip: 198.51.100.8
       #         repl_ip: 203.0.113.8
       #         zone: 4
       #         region: 3
       #         weight: 200
       #         groups:
       #           - account
       #           - container
       #           - silver
       #         drives:
       #           - name: sdb
       #             storage_ip: 198.51.100.9
       #             repl_ip: 203.0.113.9
       #             weight: 75
       #             groups:
       #               - gold
       #           - name: sdc
       #           - name: sdd
       #           - name: sde
       #           - name: sdf

#. Ensure the ``swift.yml`` is in the ``/etc/rpc_deploy/conf.d/``
   folder.

--------------

.. include:: navigation.txt
