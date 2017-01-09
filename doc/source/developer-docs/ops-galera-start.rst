==================
Starting a cluster
==================

Gracefully shutting down all nodes destroys the cluster. Starting or
restarting a cluster from zero nodes requires creating a new cluster on
one of the nodes.

#. Start a new cluster on the most advanced node.
   Check the ``seqno`` value in the ``grastate.dat`` file on all of the nodes:

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

       # /etc/init.d/mysql start --wsrep-new-cluster

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

#. Restart MariaDB on the other nodes and verify that they rejoin the
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
