RabbitMQ cluster maintenance
============================

A RabbitMQ broker is a logical grouping of one or several Erlang nodes with each
node running the RabbitMQ application and sharing users, virtual hosts, queues,
exchanges, bindings, and runtime parameters. A collection of nodes is often
referred to as a `cluster`. For more information on RabbitMQ clustering, see
`RabbitMQ cluster <https://www.rabbitmq.com/clustering.html>`_.

Within OpenStack-Ansible, all data and states required for operation of the
RabbitMQ cluster is replicated across all nodes including the message queues
providing high availability. RabbitMQ nodes address each other using domain
names. The hostnames of all cluster members must be resolvable from all cluster
nodes, as well as any machines where CLI tools related to RabbitMQ might be
used. There are alternatives that may work in more restrictive environments.
For more details on that setup, see
`Inet Configuration <https://www.erlang.org/doc/apps/erts/inet_cfg.html>`_.


.. note::

   There is currently an Ansible bug in regards to ``HOSTNAME``. If
   the host ``.bashrc`` holds a var named ``HOSTNAME``, the container where the
   ``lxc_container`` module attaches will inherit this var and potentially
   set the wrong ``$HOSTNAME``. See
   `the Ansible fix <https://github.com/ansible/ansible/pull/22246>`_ which will
   be released in Ansible version 2.3.

Create a RabbitMQ cluster
-------------------------

RabbitMQ clusters can be formed in two ways:

* Manually with ``rabbitmqctl``

* Declaratively (list of cluster nodes in a config, with
  ``rabbitmq-autocluster``, or ``rabbitmq-clusterer`` plugins)

.. note::

   RabbitMQ brokers can tolerate the failure of individual nodes within the
   cluster. These nodes can start and stop at will as long as they have the
   ability to reach previously known members at the time of shutdown.

There are two types of nodes you can configure: disk and RAM nodes. Most
commonly, you will use your nodes as disk nodes (preferred). Whereas
RAM nodes are more of a special configuration used in performance clusters.

RabbitMQ nodes and the CLI tools use an ``erlang cookie`` to determine whether
or not they have permission to communicate. The cookie is a string
of alphanumeric characters and can be as short or as long as you would like.

.. note::

   The cookie value is a shared secret and should be protected and kept private.

The default location of the cookie on ``*nix`` environments is
``/var/lib/rabbitmq/.erlang.cookie`` or in ``$HOME/.erlang.cookie``.

.. tip::

   While troubleshooting, if you notice one node is refusing to join the
   cluster, it is definitely worth checking if the erlang cookie matches
   the other nodes. When the cookie is misconfigured (for example, not identical),
   RabbitMQ will log errors such as "Connection attempt from disallowed node" and
   "Could not auto-cluster". See `clustering <https://www.rabbitmq.com/clustering.html>`_
   for more information.

To form a RabbitMQ Cluster, you start by taking independent RabbitMQ brokers
and re-configuring these nodes into a cluster configuration.

Using a 3 node example, you would be telling nodes 2 and 3 to join the
cluster of the first node.

#. Login to the 2nd and 3rd node and stop the RabbitMQ application.

#. Join the cluster, then restart the application:

   .. code-block:: console

       rabbit2$ rabbitmqctl stop_app
       Stopping node rabbit@rabbit2 ...done.
       rabbit2$ rabbitmqctl join_cluster rabbit@rabbit1
       Clustering node rabbit@rabbit2 with [rabbit@rabbit1] ...done.
       rabbit2$ rabbitmqctl start_app
       Starting node rabbit@rabbit2 ...done.

Check the RabbitMQ cluster status
---------------------------------

#. Run ``rabbitmqctl cluster_status`` from either node.

You will see ``rabbit1`` and ``rabbit2`` are both running as before.

The difference is that the cluster status section of the output, both
nodes are now grouped together:

.. code-block:: console

   rabbit1$ rabbitmqctl cluster_status
   Cluster status of node rabbit@rabbit1 ...
   [{nodes,[{disc,[rabbit@rabbit1,rabbit@rabbit2]}]},
   {running_nodes,[rabbit@rabbit2,rabbit@rabbit1]}]
   ...done.

To add the third RabbitMQ node to the cluster, repeat the above
process by stopping the RabbitMQ application on the third node.

#. Join the cluster, and restart the application on the third node.

#. Execute ``rabbitmq cluster_status`` to see all 3 nodes:

   .. code-block:: console

       rabbit1$ rabbitmqctl cluster_status
       Cluster status of node rabbit@rabbit1 ...
       [{nodes,[{disc,[rabbit@rabbit1,rabbit@rabbit2,rabbit@rabbit3]}]},
        {running_nodes,[rabbit@rabbit3,rabbit@rabbit2,rabbit@rabbit1]}]
       ...done.

Stop and restart a RabbitMQ cluster
-----------------------------------

To stop and start the cluster, keep in mind the order in which you shut the
nodes down. The last node you stop, needs to be the first node you start.
This node is the `master`.

If you start the nodes out of order, you could run into an issue where
it thinks the current `master` should not be the master and drops the messages
to ensure that no new messages are queued while the real master is down.

RabbitMQ and Mnesia
-------------------

Mnesia is a distributed database that RabbitMQ uses to store information about
users, exchanges, queues, and bindings. Messages, however
are not stored in the database.

For more information about Mnesia, see the
`Mnesia overview <https://www.erlang.org/doc/apps/mnesia/mnesia_overview>`_.

To view the locations of important RabbitMQ files, see
`File Locations <https://www.rabbitmq.com/relocate.html>`_.

Repair a partitioned RabbitMQ cluster for a single-node
-------------------------------------------------------

Invariably due to something in your environment, you are likely to lose a
node in your cluster. In this scenario, multiple LXC containers on the same
host are running RabbitMQ and are in a single RabbitMQ cluster.

If the host still shows as part of the cluster, but it is not running,
execute:

.. code-block:: console

   # rabbitmqctl start_app

However, you may notice some issues with your application as clients may be
trying to push messages to the un-responsive node. To remedy this, forget the
node from the cluster by executing the following:

#. Ensure RabbitMQ is not running on the node:

   .. code-block:: console

      # rabbitmqctl stop_app

#. On the RabbitMQ second node, execute:

   .. code-block:: console

      # rabbitmqctl forget_cluster_node rabbit@rabbit1

By doing this, the cluster can continue to run effectively and you can repair
the failing node.

.. important::

   Watch out when you restart the node, it will still think it is part of
   the cluster and will require you to reset the node. After resetting, you
   should be able to rejoin it to other nodes as needed.

   .. code-block:: console

      rabbit1$ rabbitmqctl start_app
      Starting node rabbit@rabbit1 ...

      Error: inconsistent_cluster: Node rabbit@rabbit1 thinks it's clustered
             with node rabbit@rabbit2, but rabbit@rabbit2 disagrees

      rabbit1$ rabbitmqctl reset
      Resetting node rabbit@rabbit1 ...done.
      rabbit1$ rabbitmqctl start_app
      Starting node rabbit@mcnulty ...
      ...done.

Repair a partitioned RabbitMQ cluster for a multi-node cluster
--------------------------------------------------------------

The same concepts apply to a multi-node cluster that exist in a single-node
cluster. The only difference is that the various nodes will actually be
running on different hosts. The key things to keep in mind when dealing with a
multi-node cluster are:

* When the entire cluster is brought down, the last node to go down must be the
  first node to be brought online. If this does not happen, the nodes will wait
  30 seconds for the last disc node to come back online, and fail afterwards.

  If the last node to go offline cannot be brought back up, it can be removed
  from the cluster using the :command:`forget_cluster_node` command.

* If all cluster nodes stop in a simultaneous and uncontrolled manner,
  (for example, with a power cut) you can be left with a situation in which
  all nodes think that some other node stopped after them. In this case you
  can use the :command:`force_boot` command on one node to make it
  bootable again.

Consult the rabbitmqctl manpage for more information.

Migrate between HA and Quorum queues
------------------------------------

In the 2024.1 (Caracal) release OpenStack-Ansible switches to use RabbitMQ
Quorum Queues by default, rather than the legacy High Availability classic
queues. Migration to Quorum Queues can be performed at upgrade time, but may
result in extended control plane downtime as this requires all OpenStack
services to be restarted with their new configuration.

In order to speed up the migration, the following playbooks can be run to
migrate either to or from Quorum Queues, whilst skipping package install and
other configuration tasks. These tasks are available from the 2024.1 release
onwards.

   .. code-block:: console

      $ openstack-ansible openstack.osa.rabbitmq_server --tags rabbitmq-config
      $ openstack-ansible openstack.osa.setup_openstack --tags common-mq,post-install

In order to take advantage of these steps, we suggest setting
`oslomsg_rabbit_quorum_queues` to False before upgrading to 2024.1. Then, once
you have upgraded, set `oslomsg_rabbit_quorum_queues` back to the default of
True and run the playbooks above.
