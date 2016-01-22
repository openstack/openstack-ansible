`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring HAProxy (optional)
------------------------------

For evaluation, testing, and development, HAProxy can temporarily
provide load balancing services in lieu of hardware load balancers. The
default HAProxy configuration does not provide highly-available load
balancing services. For production deployments, deploy a hardware load
balancer prior to deploying OSA.

To deploy HAProxy within your OpenStack-Ansible environment, define target
hosts which should run HAProxy:

   .. code-block:: yaml

       haproxy_hosts:
         123456-infra01:
           ip: 172.29.236.51
         123457-infra02:
           ip: 172.29.236.52
         123458-infra03:
           ip: 172.29.236.53

There is an example configuration file already provided in
``/etc/openstack_deploy/conf.d/haproxy.yml.example``. Rename the file to
``haproxy.yml`` and configure it with the correct target hosts to use HAProxy
in an OpenStack-Ansible deployment.

Making HAProxy highly-available
###############################

HAProxy will be deployed in a highly-available manner, by installing
keepalived if multiple hosts are found in the inventory.

To skip the deployment of keepalived along HAProxy when installing
HAProxy on multiple hosts, edit the
``/etc/openstack_deploy/user_variables.yml`` by setting:

.. code-block:: yaml

   haproxy_use_keepalived: False

Otherwise, edit at least the following variables in
``user_variables.yml`` to make keepalived work:

.. code-block:: yaml

   haproxy_keepalived_external_vip_cidr: 192.168.0.4/25
   haproxy_keepalived_internal_vip_cidr: 172.29.236.54/16
   haproxy_keepalived_external_interface: br-flat
   haproxy_keepalived_internal_interface: br-mgmt

``haproxy_keepalived_internal_interface`` represents the interface
on the deployed node where the keepalived master will bind the
internal vip. By default the ``br-mgmt`` will be used.

``haproxy_keepalived_external_interface`` represents the interface
on the deployed node where the keepalived master will bind the
external vip. By default the ``br-mgmt`` will be used.

``haproxy_keepalived_external_vip_cidr`` represents the external
vip (and its netmask) that will be used on keepalived master host.

``haproxy_keepalived_internal_vip_cidr`` represents the internal
vip (and its netmask) that will be used on keepalived master host.

Additional variables can be set to adapt keepalived in the deployed
environment. Please refer to the ``user_variables.yml``
for more descriptions.

All the variables mentionned here before are used in the variable
files ``vars/configs/keepalived_haproxy_master.yml`` and
``vars/configs/keepalived_haproxy_backup.yml`` to feed the
keepalived role. More information can be found on the keepalived
role documentation. You can use your own file by setting their path
in your ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

   haproxy_keepalived_vars_file:

Securing HAProxy communication with SSL certificates
####################################################

The OpenStack-Ansible project provides the ability to secure HAProxy
communications with self-signed or user-provided SSL certificates.

Refer to `Securing services with SSL certificates`_ for available configuration
options.

.. _Securing services with SSL certificates: configure-sslcertificates.html

--------------

.. include:: navigation.txt
