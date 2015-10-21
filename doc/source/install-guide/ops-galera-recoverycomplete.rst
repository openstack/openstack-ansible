`Home <index.html>`_ OpenStack-Ansible Installation Guide

Complete failure
----------------

If all of the nodes in a Galera cluster fail (do not shutdown
gracefully), then the integrity of the database can no longer be
guaranteed and should be restored from backup. Run the following command
to determine if all nodes in the cluster have failed:

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
          

All the nodes have failed if ``mysqld`` is not running on any of the
nodes and all of the nodes contain a ``seqno`` value of -1.

If any single node has a positive ``seqno`` value, then that node can be
used to restart the cluster. However, because there is no guarantee that
each node has an identical copy of the data, it is not recommended to
restart the cluster using the **--wsrep-new-cluster** command on one
node.

--------------

.. include:: navigation.txt
