`Home <index.html>`_ OpenStack-Ansible Installation Guide

Verifying infrastructure operation
----------------------------------

Verify the database cluster and Kibana web interface operation.

**Procedure 7.1. Verifying the database cluster**

#. Determine the Galera container name:

   .. code-block:: shell-session

       # lxc-ls | grep galera
       infra1_galera_container-4ed0d84a

#. Access the Galera container:

   .. code-block:: shell-session

       # lxc-attach -n infra1_galera_container-4ed0d84a

#. Run the MariaDB client, show cluster status, and exit the client:

   .. code-block:: shell-session

       # mysql -u root -p
       MariaDB> show status like 'wsrep_cluster%';
       +--------------------------+--------------------------------------+
       | Variable_name            | Value                                |
       +--------------------------+--------------------------------------+
       | wsrep_cluster_conf_id    | 3                                    |
       | wsrep_cluster_size       | 3                                    |
       | wsrep_cluster_state_uuid | bbe3f0f6-3a88-11e4-bd8f-f7c9e138dd07 |
       | wsrep_cluster_status     | Primary                              |
       +--------------------------+--------------------------------------+
       MariaDB> exit
               

   The ``wsrep_cluster_size`` field should indicate the number of nodes
   in the cluster and the ``wsrep_cluster_status`` field should indicate
   primary.

 

**Procedure 7.2. Verifying the Kibana web interface**

#. With a web browser, access the Kibana web interface using the
   external load balancer IP address defined by the
   ``external_lb_vip_address`` option in the
   ``/etc/openstack_deploy/openstack_user_config.yml`` file. The Kibana
   web interface uses HTTPS on port 8443.

#. Authenticate using the username ``kibana`` and password defined by
   the ``kibana_password`` option in the
   ``/etc/openstack_deploy/user_variables.yml`` file.

--------------

.. include:: navigation.txt
