`Home <index.html>`_ OpenStack-Ansible Installation Guide

Chapter 6. Infrastructure playbooks
-----------------------------------

**Figure 6.1. Installation workflow**

.. image:: figures/workflow-infraplaybooks.png

The main Ansible infrastructure playbook installs infrastructure
services and performs the following operations:

-  Install Memcached

-  Install the repository server

-  Install Galera

-  Install RabbitMQ

-  Install Rsyslog

-  Configure Rsyslog

Running the infrastructure playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

   Before continuing, the configuration files may be validated using the
   guidance in "`Checking the integrity of your configuration files`_".

.. _Checking the integrity of your configuration files: ../install-guide/configure-configurationintegrity.html

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the infrastructure setup playbook, which runs a series of
   sub-playbooks:

   .. code-block:: shell-session

       # openstack-ansible setup-infrastructure.yml

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: shell-session

       PLAY RECAP ********************************************************************
       ...
       deployment_host                : ok=27   changed=0    unreachable=0    failed=0

Verify the database cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Execute the following to show the current cluster state:

   .. code-block:: shell-session

       # ansible galera_container -m shell -a "mysql \
       -h localhost -e 'show status like \"%wsrep_cluster_%\";'"

   The results should look something like:

   .. code-block:: shell-session

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

   The ``wsrep_cluster_size`` field should indicate the number of nodes
   in the cluster and the ``wsrep_cluster_status`` field should indicate
   primary.

--------------

.. include:: navigation.txt
