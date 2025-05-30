Add a new infrastructure host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While three infrastructure hosts are recommended, if further hosts are
needed in an environment, it is possible to create additional nodes.

.. warning::

   Make sure you back up your current OpenStack environment
   before adding any new nodes. See :ref:`backup-restore` for more
   information.

#. Add the node to the ``infra_hosts`` stanza of the
   ``/etc/openstack_deploy/openstack_user_config.yml``:

   .. code:: console

      infra_hosts:
      [...]
        infra<node-ID>:
          ip: 10.17.136.32

#. Change to playbook folder on the deployment host:

   .. code:: console

      # cd /opt/openstack-ansible

#. To prepare new hosts and deploy containers on them run ``setup-hosts.yml``:
   playbook with the ``limit`` argument.

   .. code:: console

      # openstack-ansible openstack.osa.setup_hosts --limit localhost,infra<node-ID>,infra<node-ID>-host_containers

#. In case you're relying on ``/etc/hosts`` content, you should also update it for all hosts:

   .. code:: console

      # openstack-ansible openstack.osa.openstack_hosts_setup -e openstack_hosts_group=all --tags openstack_hosts-file

#. Next we need to expand Galera/RabbitMQ clusters, which is done during
   ``setup-infrastructure.yml``. So we will run this playbook without limits:

   .. warning::

     Make sure that containers from new infra host *does not* appear in inventory
     as first one for groups ``galera_all``, ``rabbitmq_all`` and ``repo_all``.
     You can verify that with ad-hoc commands:

     .. code:: console

       # ansible -m debug -a "var=groups['galera_all'][0]" localhost
       # ansible -m debug -a "var=groups['rabbitmq_all'][0]" localhost
       # ansible -m debug -a "var=groups['repo_all'][0]" localhost

   .. code:: console

      # openstack-ansible openstack.osa.setup_infrastructure -e galera_force_bootstrap=true

#. Once infrastructure playboks are done, it's turn of OpenStack services to be
   deployed. Most of the services are fine to be ran with limits, but some,
   like keystone, are not. So we run keystone playbook separately from all others:

   .. code:: console

      # openstack-ansible openstack.osa.keystone
      # openstack-ansible openstack.osa.setup_openstack --limit '!keystone_all',localhost,infra<node-ID>,infra<node-ID>-host_containers

Test new infra nodes
--------------------

After creating a new infra node, test that the node runs correctly by
launching a new instance. Ensure that the new node can respond to
a networking connection test through the :command:`ping` command.
Log in to your monitoring system, and verify that the monitors
return a green signal for the new node.
