Galera cluster maintenance
==========================

Routine maintenance includes gracefully adding or removing nodes from
the cluster without impacting operation and also starting a cluster
after gracefully shutting down all nodes.

MariaDB instances are restarted when creating a cluster, when adding a
node, when the service is not running, or when changes are made to the
``/etc/mysql/my.cnf`` configuration file.

Verify cluster status
---------------------

Compare the output of the following command with the following output.
It should give you information about the status of your cluster.

.. code-block:: shell-session

    # ansible galera_container -m shell -a "mariadb \
    -e 'show status like \"%wsrep_cluster_%\";'"
    node3_galera_container-3ea2cbd3 | FAILED | rc=1 >>
    ERROR 2002 (HY000): Can't connect to local MySQL server
    through socket '/var/run/mysqld/mysqld.sock' (2)

    node2_galera_container-49a47d25 | FAILED | rc=1 >>
    ERROR 2002 (HY000): Can't connect to local MySQL server
    through socket '/var/run/mysqld/mysqld.sock' (2)

    node4_galera_container-76275635 | success | rc=0 >>
    Variable_name             Value
    wsrep_cluster_conf_id     7
    wsrep_cluster_size        1
    wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
    wsrep_cluster_status      Primary

In this example, only one node responded.

Gracefully shutting down the MariaDB service on all but one node allows the
remaining operational node to continue processing SQL requests. When
gracefully shutting down multiple nodes, perform the actions sequentially to
retain operation.

Start a cluster
---------------

Gracefully shutting down all nodes destroys the cluster. Starting or
restarting a cluster from zero nodes requires creating a new cluster on
one of the nodes.

#. Start a new cluster on the most advanced node.
   Change to the ``playbooks`` directory and check the ``seqno``
   value in the ``grastate.dat`` file on all of the nodes:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "cat /var/lib/mysql/grastate.dat"
       node2_galera_container-49a47d25 | success | rc=0 >>
       # GALERA saved state version: 2.1
       uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
       seqno:   31
       cert_index:

       node3_galera_container-3ea2cbd3 | success | rc=0 >>
       # GALERA saved state version: 2.1
       uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
       seqno:   31
       cert_index:

       node4_galera_container-76275635 | success | rc=0 >>
       # GALERA saved state version: 2.1
       uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
       seqno:   31
       cert_index:

   In this example, all nodes in the cluster contain the same positive
   ``seqno`` values as they were synchronized just prior to
   graceful shutdown. If all ``seqno`` values are equal, any node can
   start the new cluster.

   .. code-block:: shell-session

       ## for init
       # /etc/init.d/mariadb start --wsrep-new-cluster
       ## for systemd
       # systemctl set-environment _WSREP_NEW_CLUSTER='--wsrep-new-cluster'
       # systemctl start mariadb
       # systemctl set-environment _WSREP_NEW_CLUSTER=''

   Please also have a look at
   `Starting the Cluster <https://galeracluster.com/library/training/tutorials/starting-cluster.html>`_.

   This can also be done with the help of Ansible using the shell
   module:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "/etc/init.d/mariadb start --wsrep-new-cluster" --limit galera_container[0]

   This command results in a cluster containing a single node. The
   ``wsrep_cluster_size`` value shows the number of nodes in the
   cluster.

   .. code-block:: shell-session

       node2_galera_container-49a47d25 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (111)

       node3_galera_container-3ea2cbd3 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (2)

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     1
       wsrep_cluster_size        1
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

#. Restart MariaDB on the other nodes (replace [0] from previous
   Ansible command with [1:]) and verify that they rejoin the
   cluster.

   .. code-block:: shell-session

       node2_galera_container-49a47d25 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     3
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node3_galera_container-3ea2cbd3 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     3
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     3
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

.. _galera-cluster-recovery:

Galera cluster recovery
-----------------------

Run the ``openstack.osa.galera_server`` playbook using the ``galera_force_bootstrap`` variable
to automatically recover a node or an entire environment.

#. Run the following Ansible command to show the failed nodes:

   .. code-block:: shell-session

       # openstack-ansible openstack.osa.galera_server -e galera_force_bootstrap=True --tags galera_server-config

You can additionally define a different bootstrap node through
``galera_server_bootstrap_node`` variable, in case current bootstrap node is in
desynced/broken state. You can check what node is currently selected for
bootstrap using this ad-hoc:

   .. code-block:: shell-session

       root@aio1:/opt/openstack-ansible# ansible -m debug -a var="groups['galera_all'][0]" localhost

The cluster comes back online after completion of this command. If this
fails, please review `restarting the cluster`_ and `recovering the primary
component`_ in the Galera documentation as they're invaluable for a full
cluster recovery.

.. _restarting the cluster: https://galeracluster.com/library/training/tutorials/restarting-cluster.html
.. _recovering the primary component: https://galeracluster.com/library/documentation/pc-recovery.html

Recover a single-node failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a single node fails, the other nodes maintain quorum and
continue to process SQL requests.

#. Change to the ``playbooks`` directory and run the following
   Ansible command to determine the failed node:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mariadb \
       -e 'show status like \"%wsrep_cluster_%\";'"
       node3_galera_container-3ea2cbd3 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server through
       socket '/var/run/mysqld/mysqld.sock' (111)

       node2_galera_container-49a47d25 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     17
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     17
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

   In this example, node 3 has failed.

#. Restart MariaDB on the failed node and verify that it rejoins the
   cluster.

#. If MariaDB fails to start, run the ``mariadbd`` command and perform
   further analysis on the output. As a last resort, rebuild the container
   for the node.

Recover a multi-node failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When all but one node fails, the remaining node cannot achieve quorum and
stops processing SQL requests. In this situation, failed nodes that
recover cannot join the cluster because it no longer exists.

#. Run the following Ansible command to show the failed nodes:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mariadb \
       -e 'show status like \"%wsrep_cluster_%\";'"
       node2_galera_container-49a47d25 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (111)

       node3_galera_container-3ea2cbd3 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (111)

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     18446744073709551615
       wsrep_cluster_size        1
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      non-Primary

   In this example, nodes 2 and 3 have failed. The remaining operational
   server indicates ``non-Primary`` because it cannot achieve quorum.

#. Run the following command to
   `rebootstrap <https://galeracluster.com/library/documentation/quorum-reset.html>`_
   the operational node into the cluster:

   .. code-block:: shell-session

       # mariadb -e "SET GLOBAL wsrep_provider_options='pc.bootstrap=yes';"
       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     15
       wsrep_cluster_size        1
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node3_galera_container-3ea2cbd3 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (111)

       node2_galera_container-49a47d25 | FAILED | rc=1 >>
       ERROR 2002 (HY000): Can't connect to local MySQL server
       through socket '/var/run/mysqld/mysqld.sock' (111)

   The remaining operational node becomes the primary node and begins
   processing SQL requests.

#. Restart MariaDB on the failed nodes and verify that they rejoin the
   cluster:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mariadb \
       -e 'show status like \"%wsrep_cluster_%\";'"
       node3_galera_container-3ea2cbd3 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     17
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node2_galera_container-49a47d25 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     17
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     17
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

#. If MariaDB fails to start on any of the failed nodes, run the
   ``mariadbd`` command and perform further analysis on the output. As a
   last resort, rebuild the container for the node.

Recover a complete environment failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Restore from backup if all of the nodes in a Galera cluster fail (do not
shutdown gracefully). Change to the ``playbook`` directory and run the
following command to determine if all nodes in
the cluster have failed:

.. code-block:: shell-session

    # ansible galera_container -m shell -a "cat /var/lib/mysql/grastate.dat"
    node3_galera_container-3ea2cbd3 | success | rc=0 >>
    # GALERA saved state
    version: 2.1
    uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
    seqno:   -1
    cert_index:

    node2_galera_container-49a47d25 | success | rc=0 >>
    # GALERA saved state
    version: 2.1
    uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
    seqno:   -1
    cert_index:

    node4_galera_container-76275635 | success | rc=0 >>
    # GALERA saved state
    version: 2.1
    uuid:    338b06b0-2948-11e4-9d06-bef42f6c52f1
    seqno:   -1
    cert_index:

All the nodes have failed if ``mariadbd`` is not running on any of the
nodes and all of the nodes contain a ``seqno`` value of -1.

If any single node has a positive ``seqno`` value, then that node can be
used to restart the cluster. However, because there is no guarantee that
each node has an identical copy of the data, we do not recommend to
restart the cluster using the ``--wsrep-new-cluster`` command on one
node.

Rebuild a container
~~~~~~~~~~~~~~~~~~~

Recovering from certain failures require rebuilding one or more containers.

#. Disable the failed node on the load balancer.

   .. note::

      Do not rely on the load balancer health checks to disable the node.
      If the node is not disabled, the load balancer sends SQL requests
      to it before it rejoins the cluster and cause data inconsistencies.

#. Destroy the container and remove MariaDB data stored outside
   of the container:

   .. code-block:: shell-session

       # openstack-ansible openstack.osa.containers_lxc_destroy \
       -l node3_galera_container-3ea2cbd3

   In this example, node 3 failed.

#. Run the host setup playbook to rebuild the container on node 3:

   .. code-block:: shell-session

       # openstack-ansible oopenstack.osa.containers_lxc_create -l node3 \
       -l node3_galera_container-3ea2cbd3

   The playbook restarts all other containers on the node.

#. Run the infrastructure playbook to configure the container
   specifically on node 3:

   .. code-block:: shell-session

       # openstack-ansible openstack.osa.setup_infrastructure \
       --limit node3_galera_container-3ea2cbd3

   .. warning::

      The new container runs a single-node Galera cluster, which is a dangerous
      state because the environment contains more than one active database
      with potentially different data.

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mariadb \
       -e 'show status like \"%wsrep_cluster_%\";'"
       node3_galera_container-3ea2cbd3 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     1
       wsrep_cluster_size        1
       wsrep_cluster_state_uuid  da078d01-29e5-11e4-a051-03d896dbdb2d
       wsrep_cluster_status      Primary

       node2_galera_container-49a47d25 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     4
       wsrep_cluster_size        2
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     4
       wsrep_cluster_size        2
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

#. Restart MariaDB in the new container and verify that it rejoins the
   cluster.

   .. note::

      In larger deployments, it may take some time for the MariaDB daemon to
      start in the new container. It will be synchronizing data from the other
      MariaDB servers during this time. You can monitor the status during this
      process by tailing the ``journalctl -f -u mariadb``
      log file.

      Lines starting with ``WSREP_SST`` will appear during the sync process
      and you should see a line with ``WSREP: SST complete, seqno: <NUMBER>``
      if the sync was successful.

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mariadb \
       -e 'show status like \"%wsrep_cluster_%\";'"
       node2_galera_container-49a47d25 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     5
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node3_galera_container-3ea2cbd3 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     5
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

       node4_galera_container-76275635 | success | rc=0 >>
       Variable_name             Value
       wsrep_cluster_conf_id     5
       wsrep_cluster_size        3
       wsrep_cluster_state_uuid  338b06b0-2948-11e4-9d06-bef42f6c52f1
       wsrep_cluster_status      Primary

#. Enable the previously failed node on the load balancer.
