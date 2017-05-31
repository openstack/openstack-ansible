==================
Networking service
==================

The os_neutron role provides for a lot of flexibility. See the `neutron`_ role
for a full list of all available options.

Load-Balancer-as-a-Service (LBaaS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understand the following characteristics of the OpenStack-Ansible LBaaS
technical preview:

* The preview release is not intended to provide highly scalable or
  highly available load balancing services.
* Testing and recommended usage is limited to 10 members in a pool
  and no more than 20 pools.
* Virtual load balancers deployed as part of the LBaaS service are
  not monitored for availability or performance.
* OpenStack-Ansible enables LBaaS v2 with the default HAProxy-based agent.
* The Octavia agent is not supported.
* Integration with physical load balancer devices is not supported.
* Customers can use API or CLI LBaaS interfaces.
* The Dashboard offers a panel for creating and managing LBaaS load balancers,
  listeners, pools, members, and health checks.
* SDN integration is not supported.

Since Mitaka, you can `enable Dashboard (horizon) panels`_ for LBaaS.
Additionally, a deployer can specify a list of servers behind a
listener and reuse that list for another listener. This feature,
called *shared pools*, only applies to customers that have a large
number of listeners (ports) behind a load balancer.

.. _neutron:
   https://docs.openstack.org/developer/openstack-ansible-os_neutron

.. _enable Dashboard (horizon) panels:
   https://docs.openstack.org/developer/openstack-ansible-os_horizon

