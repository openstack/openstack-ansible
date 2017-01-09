==============
Removing nodes
==============

In the following example, all but one node was shut down gracefully:

.. code-block:: shell-session

    # ansible galera_container -m shell -a "mysql -h localhost \
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


Compare this example output with the output from the multi-node failure
scenario where the remaining operational node is non-primary and stops
processing SQL requests. Gracefully shutting down the MariaDB service on
all but one node allows the remaining operational node to continue
processing SQL requests. When gracefully shutting down multiple nodes,
perform the actions sequentially to retain operation.
