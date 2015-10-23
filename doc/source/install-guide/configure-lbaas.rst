`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Network Load Balancing Service (Optional)
---------------------------------------------------------

The OpenStack Networking Service, Neutron, includes a Load Balancer as a
Service (LBaaS). This service lets you configure a load balancer that runs
outside of your instances and directs traffic to your instances. A common use
case is when you want to use multiple instances to serve web pages and want to
meet high performance or availability goals.

OpenStack-Ansible currently provides the OpenStack Neutron LBaaS service using
HAProxy as the load balancer.

The following procedure describes how to modify the
``/etc/openstack_deploy/user_variables.yml`` file to enable LBaaS.

#. Override the default list of Neutron plugins used in order to include
   ``neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPlugin``:

   .. code-block:: yaml

      neutron_plugin_base:
        - neutron.services.l3_router.l3_router_plugin.L3RouterPlugin
        - neutron.services.metering.metering_plugin.MeteringPlugin
        - neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPlugin

#. Execute the Neutron install playbook in order to update the configuration
   of the Neutron Agents:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-neutron-install.yml

#. Execute the Horizon install playbook in order to update the Horizon
   configuration to show the LBaaS panels:

   .. code-block:: shell-session

       # cd /opt/openstack-ansible/playbooks
       # openstack-ansible os-horizon-install.yml

The LBaaS default configuration options may be changed through the
`conf override`_ mechanism using the ``neutron_lbaas_agent_ini_overrides``
dict.

.. conf override: http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-openstack.html

--------------

.. include:: navigation.txt
