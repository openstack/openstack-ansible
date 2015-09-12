`Home <index.html>`__ OpenStack Ansible Installation Guide

Configuring HAProxy (optional)
------------------------------

For evaluation, testing, and development, HAProxy can temporarily
provide load balancing services in lieu of hardware load balancers. The
default HAProxy configuration does not provide highly-available load
balancing services. For production deployments, deploy a hardware load
balancer prior to deploying OSA.

-  In the ``/etc/openstack_deploy/openstack_user_config.yml`` file, add
   the ``haproxy_hosts`` section with one or more infrastructure target
   hosts, for example:

   .. code-block:: yaml

       haproxy_hosts:
         123456-infra01:
           ip: 172.29.236.51
         123457-infra02:
           ip: 172.29.236.52
         123458-infra03:
           ip: 172.29.236.53

--------------

.. include:: navigation.txt
