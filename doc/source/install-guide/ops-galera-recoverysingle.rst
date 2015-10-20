`Home <index.html>`_ OpenStack-Ansible Installation Guide

Single-node failure
-------------------

If a single node fails, the other nodes maintain quorum and continue to
process SQL requests.

#. Run the following Ansible command to determine the failed node:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql -h localhost \
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

#. If MariaDB fails to start, run the **mysqld** command and perform
   further analysis on the output. As a last resort, rebuild the
   container for the node.

--------------

.. include:: navigation.txt
