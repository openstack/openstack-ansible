`Home <index.html>`_ OpenStack-Ansible Installation Guide

Multi-node failure
------------------

When all but one node fails, the remaining node cannot achieve quorum
and stops processing SQL requests. In this situation, failed nodes that
recover cannot join the cluster because it no longer exists.

#. Run the following Ansible command to show the failed nodes:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql \
       -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
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
   `rebootstrap <http://galeracluster.com/documentation-webpages/quorumreset.html#id1>`_
   the operational node into the cluster.

   .. code-block:: shell-session

       # mysql -e "SET GLOBAL wsrep_provider_options='pc.bootstrap=yes';"
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
   cluster.

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql \
       -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
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
   **mysqld** command and perform further analysis on the output. As a
   last resort, rebuild the container for the node.

--------------

.. include:: navigation.txt
