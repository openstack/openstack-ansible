`Home <index.html>`_ OpenStack-Ansible Installation Guide

Rebuilding a container
----------------------

Sometimes recovering from a failure requires rebuilding one or more
containers.

#. Disable the failed node on the load balancer.

   Do not rely on the load balancer health checks to disable the node.
   If the node is not disabled, the load balancer will send SQL requests
   to it before it rejoins the cluster and cause data inconsistencies.

#. Use the following commands to destroy the container and remove
   MariaDB data stored outside of the container. In this example, node 3
   failed.

   .. code-block:: shell-session

       # lxc-stop -n node3_galera_container-3ea2cbd3
       # lxc-destroy -n node3_galera_container-3ea2cbd3
       # rm -rf /openstack/node3_galera_container-3ea2cbd3/*

#. Run the host setup playbook to rebuild the container specifically on
   node 3:

   .. code-block:: shell-session

       # openstack-ansible setup-hosts.yml -l node3 \
       -l node3_galera_container-3ea2cbd3


   The playbook will also restart all other containers on the node.

#. Run the infrastructure playbook to configure the container
   specifically on node 3:

   .. code-block:: shell-session

       # openstack-ansible infrastructure-setup.yml \
       -l node3_galera_container-3ea2cbd3


   The new container runs a single-node Galera cluster, a dangerous
   state because the environment contains more than one active database
   with potentially different data.

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql \
       -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
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

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql \
       -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
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
                 

#. Enable the failed node on the load balancer.

--------------

.. include:: navigation.txt
