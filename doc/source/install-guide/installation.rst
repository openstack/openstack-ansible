============
Installation
============

The installation process requires running three main playbooks:

- The ``setup-hosts.yml`` Ansible foundation playbook prepares the target
  hosts for infrastructure and OpenStack services, builds and restarts
  containers on target hosts, and installs common components into containers
  on target hosts.

- The ``setup-infrastructure.yml`` Ansible infrastructure playbook installs
  infrastructure services: memcached, the repository server, Galera, RabbitMQ,
  and Rsyslog.

- The ``setup-openstack.yml`` OpenStack playbook installs OpenStack services,
  including the Identity service (keystone), Image service (glance),
  Block Storage (cinder), Compute service (nova), OpenStack Networking
  (neutron), Orchestration (heat), Dashboard (horizon), Telemetry service
  (ceilometer and aodh), Object Storage service (swift), and OpenStack
  Bare Metal provisioning (ironic).

Checking the integrity of your configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before running any playbook, check the integrity of your configuration files.

#. Ensure all files edited in ``/etc/openstack_deploy`` are Ansible
   YAML compliant. Guidelines can be found here:
   `<http://docs.ansible.com/ansible/YAMLSyntax.html>`_

#. Check the integrity of your YAML files.

   .. note::

      To check your lint online, we recommend: `<http://www.yamllint.com/>`_.

#. Run your command with ``syntax-check``:

   .. code-block:: shell-session

      # openstack-ansible setup-infrastructure.yml --syntax-check

#. Recheck that all indentation is correct. This is important as the syntax
   of the configuration files can be correct while not being meaningful for
   OpenStack-Ansible.

.. _run-playbooks:

Run playbooks
~~~~~~~~~~~~~

.. figure:: figures/installation-workflow-run-playbooks.png
   :width: 100%

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the host setup playbook:

   .. code-block:: console

       # openstack-ansible setup-hosts.yml

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: console

       PLAY RECAP ********************************************************************
       ...
       deployment_host                :  ok=18   changed=11   unreachable=0    failed=0


#. Run the infrastructure setup playbook:

   .. code-block:: console

      # openstack-ansible setup-infrastructure.yml

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: console

      PLAY RECAP ********************************************************************
      ...
      deployment_host                : ok=27   changed=0    unreachable=0    failed=0


#. Run the following command to verify the database cluster:

   .. code-block:: console

      # . /usr/local/bin/openstack-ansible.rc
      # ansible galera_container -m shell \
        -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"

   Example output:

   .. code-block:: console

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

   The ``wsrep_cluster_size`` field indicates the number of nodes
   in the cluster and the ``wsrep_cluster_status`` field indicates
   primary.

#. Run the OpenStack setup playbook:

   .. code-block:: console

      # openstack-ansible setup-openstack.yml

   Confirm satisfactory completion with zero items unreachable or
   failed.

Utility container
~~~~~~~~~~~~~~~~~

The utility container provides a space where miscellaneous tools and
software are installed. Tools and objects are placed in a
utility container if they do not require a dedicated container or if it
is impractical to create a new container for a single tool or object.
Utility containers are also used when tools cannot be installed
directly onto a host.

For example, the tempest playbooks are installed on the utility
container since tempest testing does not need a container of its own.

.. _verify-operation:

Verifying OpenStack operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: figures/installation-workflow-verify-openstack.png
   :width: 100%


.. TODO Add procedures to test different layers of the OpenStack environment

The utility container provides a CLI environment for additional
configuration and testing. The following instructions are to be done on an
infra host.

#. Determine the utility container name:

   .. code-block:: console

      # lxc-ls | grep utility
      infra1_utility_container-161a4084

#. Access the utility container:

   .. code-block:: console

      # lxc-attach -n infra1_utility_container-161a4084

#. Source the ``admin`` tenant credentials:

   .. code-block:: console

      # source /root/openrc

#. Run an OpenStack command that uses one or more APIs. For example:

   .. code-block:: console

      # openstack user list
      +----------------------------------+--------------------+
      | ID                               | Name               |
      +----------------------------------+--------------------+
      | 08fe5eeeae314d578bba0e47e7884f3a | alt_demo           |
      | 0aa10040555e47c09a30d2240e474467 | dispersion         |
      | 10d028f9e47b4d1c868410c977abc3df | glance             |
      | 249f9ad93c024f739a17ca30a96ff8ee | demo               |
      | 39c07b47ee8a47bc9f9214dca4435461 | swift              |
      | 3e88edbf46534173bc4fd8895fa4c364 | cinder             |
      | 41bef7daf95a4e72af0986ec0583c5f4 | neutron            |
      | 4f89276ee4304a3d825d07b5de0f4306 | admin              |
      | 943a97a249894e72887aae9976ca8a5e | nova               |
      | ab4f0be01dd04170965677e53833e3c3 | stack_domain_admin |
      | ac74be67a0564722b847f54357c10b29 | heat               |
      | b6b1d5e76bc543cda645fa8e778dff01 | ceilometer         |
      | dc001a09283a404191ff48eb41f0ffc4 | aodh               |
      | e59e4379730b41209f036bbeac51b181 | keystone           |
      +----------------------------------+--------------------+

Verifying the Dashboard (horizon)
---------------------------------

#. With a web browser, access the Dashboard using the external load
   balancer IP address defined by the ``external_lb_vip_address`` option
   in the ``/etc/openstack_deploy/openstack_user_config.yml`` file. The
   dashboard uses HTTPS on port 443.

#. Authenticate using the username ``admin`` and password defined by the
   ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_secrets.yml`` file.

.. TODO Add troubleshooting information to resolve common installation issues

