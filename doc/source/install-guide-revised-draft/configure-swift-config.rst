`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the service
=======================

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
       #     mount_point: /srv/node
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
       #     statsd_host: statsd.example.com
       #     statsd_port: 8125
       #     statsd_metric_prefix:
       #     statsd_default_sample_rate: 1.0
       #     statsd_sample_rate_factor: 1.0


   ``part_power``
       Set the partition power value based on the total amount of
       storage the entire ring uses.

       Multiply the maximum number of drives ever used with the swift
       installation by 100 and round that value up to the
       closest power of two value. For example, a maximum of six drives,
       times 100, equals 600. The nearest power of two above 600 is two
       to the power of nine, so the partition power is nine. The
       partition power cannot be changed after the swift rings
       are built.

   ``weight``
       The default weight is 100. If the drives are different sizes, set
       the weight value to avoid uneven distribution of data. For
       example, a 1 TB disk would have a weight of 100, while a 2 TB
       drive would have a weight of 200.

   ``min_part_hours``
       The default value is 1. Set the minimum partition hours to the
       amount of time to lock a partition's replicas after moving a partition.
       Moving multiple replicas at the same time
       makes data inaccessible. This value can be set separately in the
       swift, container, account, and policy sections with the value in
       lower sections superseding the value in the swift section.

   ``repl_number``
       The default value is 3. Set the replication number to the number
       of replicas of each object. This value can be set separately in
       the swift, container, account, and policy sections with the value
       in the more granular sections superseding the value in the swift
       section.

   ``storage_network``
       By default, the swift services listen on the default
       management IP. Optionally, specify the interface of the storage
       network.

       If the ``storage_network`` is not set, but the ``storage_ips``
       per host are set (or the ``storage_ip`` is not on the
       ``storage_network`` interface) the proxy server is unable
       to connect to the storage services.

   ``replication_network``
       Optionally, specify a dedicated replication network interface, so
       dedicated replication can be setup. If this value is not
       specified, no dedicated ``replication_network`` is set.

       Replication does not work properly if the ``repl_ip`` is not set on
       the ``replication_network`` interface.

   ``drives``
       Set the default drives per host. This is useful when all hosts
       have the same drives. These can be overridden on a per host
       basis.

   ``mount_point``
       Set the ``mount_point`` value to the location where the swift
       drives are mounted. For example, with a mount point of ``/srv/node``
       and a drive of ``sdc``, a drive is mounted at ``/srv/node/sdc`` on the
       ``swift_host``. This can be overridden on a per-host basis.

   ``storage_policies``
       Storage policies determine on which hardware data is stored, how
       the data is stored across that hardware, and in which region the
       data resides. Each storage policy must have an unique ``name``
       and a unique ``index``. There must be a storage policy with an
       index of 0 in the ``swift.yml`` file to use any legacy containers
       created before storage policies were instituted.

   ``default``
       Set the default value to ``yes`` for at least one policy. This is
       the default storage policy for any non-legacy containers that are
       created.

   ``deprecated``
       Set the deprecated value to ``yes`` to turn off storage policies.

       For account and container rings, ``min_part_hours`` and
       ``repl_number`` are the only values that can be set. Setting them
       in this section overrides the defaults for the specific ring.

   ``statsd_host``
      Swift supports sending extra metrics to a ``statsd`` host. This option
      sets the ``statsd`` host to receive ``statsd`` metrics. Specifying
      this here applies to all hosts in the cluster.

      If ``statsd_host`` is left blank or omitted, then ``statsd`` are
      disabled.

      All ``statsd`` settings can be overridden or you can specify deeper in the
      structure if you want to only catch ``statsdv`` metrics on certain hosts.

   ``statsd_port``
      Optionally, use this to specify the ``statsd`` server's port you are
      sending metrics to. Defaults to 8125 of omitted.

   ``statsd_default_sample_rate`` and ``statsd_sample_rate_factor``
      These ``statsd`` related options are more complex and are
      used to tune how many samples are sent to ``statsd``. Omit them unless
      you need to tweak these settings, if so first read:
      http://docs.openstack.org/developer/swift/admin_guide.html

#. Update the swift proxy hosts values:

   .. code-block:: yaml

       # swift-proxy_hosts:
       #   infra-node1:
       #     ip: 192.0.2.1
       #     statsd_metric_prefix: proxy01
       #   infra-node2:
       #     ip: 192.0.2.2
       #     statsd_metric_prefix: proxy02
       #   infra-node3:
       #     ip: 192.0.2.3
       #     statsd_metric_prefix: proxy03

   ``swift-proxy_hosts``
       Set the ``IP`` address of the hosts so Ansible connects to
       to deploy the ``swift-proxy`` containers. The ``swift-proxy_hosts``
       value matches the infra nodes.

  ``statsd_metric_prefix``
       This metric is optional, and also only evaluated it you have defined
       ``statsd_host`` somewhere. It allows you define a prefix to add to
       all ``statsd`` metrics sent from this hose. If omitted, use the node name.

#. Update the swift hosts values:

   .. code-block:: yaml

       # swift_hosts:
       #   swift-node1:
       #     ip: 192.0.2.4
       #     container_vars:
       #       swift_vars:
       #         zone: 0
       #         statsd_metric_prefix: node1
       #   swift-node2:
       #     ip: 192.0.2.5
       #     container_vars:
       #       swift_vars:
       #         zone: 1
       #         statsd_metric_prefix: node2
       #   swift-node3:
       #     ip: 192.0.2.6
       #     container_vars:
       #       swift_vars:
       #         zone: 2
       #         statsd_metric_prefix: node3
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
       and IP address of each swift host. The ``swift_hosts``
       section is not required.

   ``swift_vars``
       Contains the swift host specific values.

   ``storage_ip`` and ``repl_ip``
       Base these values on the IP addresses of the host's
       ``storage_network`` or ``replication_network``. For example, if
       the ``storage_network`` is ``br-storage`` and host1 has an IP
       address of 1.1.1.1 on ``br-storage``, then this is the IP address
       in use for ``storage_ip``. If only the ``storage_ip``
       is specified, then the ``repl_ip`` defaults to the ``storage_ip``.
       If neither are specified, both default to the host IP
       address.

       Overriding these values on a host or drive basis can cause
       problems if the IP address that the service listens on is based
       on a specified ``storage_network`` or ``replication_network`` and
       the ring is set to a different IP address.

   ``zone``
       The default is 0. Optionally, set the swift zone for the
       ring.

   ``region``
       Optionally, set the swift region for the ring.

   ``weight``
       The default weight is 100. If the drives are different sizes, set
       the weight value to avoid uneven distribution of data. This value
       can be specified on a host or drive basis (if specified at both,
       the drive setting takes precedence).

   ``groups``
       Set the groups to list the rings to which a host's drive belongs.
       This can be set on a per drive basis which overrides the host
       setting.

   ``drives``
       Set the names of the drives on the swift host. Specify at least
       one name.

  ``statsd_metric_prefix``
       This metric is optional, and only evaluates if ``statsd_host`` is defined
       somewhere. This allows you to define a prefix to add to
       all ``statsd`` metrics sent from the hose. If omitted, use the node name.

   In the following example, ``swift-node5`` shows values in the
   ``swift_hosts`` section that override the global values. Groups
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

#. Ensure the ``swift.yml`` is in the ``/etc/openstack_deploy/conf.d/``
   folder.

--------------

.. include:: navigation.txt
