`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring HAProxy (optional)
------------------------------

HAProxy provides load balancing for high availability architectures deployed by
OpenStack-Ansible. The default HAProxy configuration provides highly-available
load balancing services via keepalived if there are more than one hosts in the
``haproxy_hosts`` group.

.. note::

  A load balancer is required for a successful installation. Deployers may
  prefer to make use of hardware load balancers instead of haproxy. If hardware
  load balancers are used then the load balancing configuration for services must
  be implemented prior to executing the deployment.

To deploy HAProxy within your OpenStack-Ansible environment, define target
hosts which should run HAProxy:

   .. code-block:: yaml

       haproxy_hosts:
         infra1:
           ip: 172.29.236.101
         infra2:
           ip: 172.29.236.102
         infra3:
           ip: 172.29.236.103

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

All the variables mentioned above are used in the variable file
``vars/configs/keepalived_haproxy.yml`` to feed the
keepalived role. More information can be found in the keepalived
role documentation. You can use your own variable file by setting
the path in your ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

   haproxy_keepalived_vars_file:

Securing HAProxy communication with SSL certificates
####################################################

The OpenStack-Ansible project provides the ability to secure HAProxy
communications with self-signed or user-provided SSL certificates. By default,
self-signed certificates are used with HAProxy.  However, deployers can
provide their own certificates by using the following Ansible variables:

.. code-block:: yaml

    haproxy_user_ssl_cert:          # Path to certificate
    haproxy_user_ssl_key:           # Path to private key
    haproxy_user_ssl_ca_cert:       # Path to CA certificate

Refer to `Securing services with SSL certificates`_ for more information on
these configuration options and how deployers can provide their own
certificates and keys to use with HAProxy.

.. _Securing services with SSL certificates: configure-sslcertificates.html

--------------

.. include:: navigation.txt
