`Home <index.html>`_ OpenStack-Ansible Installation Guide

Load Balancing Service (Optional)
---------------------------------

OpenStack-Ansible currently provides the OpenStack Neutron LBaaS service using
HAProxy as the load balancer. LBaaS has two implementations available: v1 and
v2.

Both implementations use agents that manage `HAProxy`_ daemons. However, LBaaS
v1 has a limitation of one port per load balancer.  LBaaS v2 allows for multiple
ports (called *listeners*) per load balancer.

.. note::

   Horizon panels for LBaaS v2 are not yet available.

.. _HAProxy: http://www.haproxy.org/

Deploying LBaaS v1
~~~~~~~~~~~~~~~~~~

.. note::

    LBaaS v1 was deprecated during the Liberty release and is not recommended
    for new deployments.

#. Start by adding the LBaaS v1 plugin to the ``neutron_plugin_base`` variable
   within ``/etc/openstack_deploy/user_variables.yml``.

   .. code-block:: yaml

      neutron_plugin_base:
        - router
        - metering
        - lbaas

   Ensure that ``neutron_plugin_base`` includes all of the plugins that you
   want to deploy with Neutron **in addition** to the LBaaS plugin.

#. Run the Neutron and Horizon playbooks to deploy the LBaaS v1 agent and enable
   the LBaaS panels in Horizon.

   .. code-block:: console

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-neutron-install.yml
       # openstack-ansible os-horizon-install.yml

Deploying LBaaS v2
~~~~~~~~~~~~~~~~~~

#. Start by adding the LBaaS v2 plugin to the ``neutron_plugin_base`` variable
   within ``/etc/openstack_deploy/user_variables.yml``.

   .. code-block:: yaml

      neutron_plugin_base:
        - router
        - metering
        - lbaasv2

   Ensure that ``neutron_plugin_base`` includes all of the plugins that you
   want to deploy with Neutron **in addition** to the LBaaS plugin.

#. Run the Neutron playbook to deploy the LBaaS v2 agent:

   .. code-block:: console

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-neutron-install.yml

Special notes about LBaaS
~~~~~~~~~~~~~~~~~~~~~~~~~

The LBaaS default configuration options may be changed through the
`conf override`_ mechanism using the ``neutron_lbaas_agent_ini_overrides``
dict.

LBaaS v1 and v2 agents cannot run at the same time. If a deployer switches from
LBaaS v1 to v2, the v2 agent will be the only agent running. The LBaaS v1 agent
will be stopped along with any load balancers provisioned under the v1 agent.
The same is true if a deployer chooses to move from LBaaS v2 to v1.

Load balancers are not migrated between LBaaS v1 and v2 automatically. Each
implementation has different code paths and database tables. Deployers will need
to manually delete load balancers, pools, and members before switching LBaaS
versions. Those objects will need to be re-created afterwards.

.. _conf override: http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-openstack.html

--------------

.. include:: navigation.txt