==================
Networking service
==================

Load-Balancer-as-a-Service (LBaaS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The LBaaS functionality is configured and deployed using
OpenStack-Ansible. For more information about LBaaS operations,
see `LBaaS`_ in the OpenStack Networking guide.

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


In Mitaka, you can `enable Dashboard (horizon) panels`_ for LBaaS.
Additionally, a customer can specify a list of servers behind a
listener and reuse that list for another listener. This feature,
called *shared pools*, only applies to customers that have a large
number of listeners (ports) behind a load balancer.

.. _LBaaS:
   http://docs.openstack.org/mitaka/networking-guide/config-lbaas.html

.. _enable Dashboard (horizon) panels:
   http://docs.openstack.org/developer/openstack-ansible/mitaka/install-guide/
   configure-network-services.html#deploying-lbaas-v2
