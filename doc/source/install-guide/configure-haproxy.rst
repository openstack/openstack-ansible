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

- ``haproxy_keepalived_internal_interface`` and
  ``haproxy_keepalived_external_interface`` represent the interfaces on the
  deployed node where the keepalived nodes will bind the internal/external
  vip. By default the ``br-mgmt`` will be used.

- ``haproxy_keepalived_internal_vip_cidr`` and
  ``haproxy_keepalived_external_vip_cidr`` represents the internal and
  external (respectively) vips (with their prefix length) that will be used on
  keepalived host with the master status, on the interface listed above.

- Additional variables can be set to adapt keepalived in the deployed
  environment. Please refer to the ``user_variables.yml`` for more descriptions.

To always deploy (or upgrade to) the latest stable version of keepalived,
edit the ``/etc/openstack_deploy/user_variables.yml`` by setting:

.. code-block:: yaml

   keepalived_use_latest_stable: True

The HAProxy playbook reads the ``vars/configs/keepalived_haproxy.yml``
variable file and provides its content to the keepalived role for
keepalived master and backup nodes.

Keepalived pings a public IP address to check its status. The default
address is ``193.0.14.129``. To change this default, for example to
your gateway, set the ``keepalived_ping_address`` variable in the
``user_variables.yml`` file.

.. note:: The keepalived test works with IPv4 addresses only.

You can define additional variables to adapt keepalived to the
deployed environment. Refer to the ``user_variables.yml`` file for
more information. Optionally, you can use your own variable file, as
follows:

.. code-block:: yaml

   haproxy_keepalived_vars_file: /path/to/myvariablefile.yml

Configuring keepalived ping checks
##################################

OpenStack-Ansible configures keepalived with a check script that pings an
external resource and uses that ping to determine if a node has lost network
connectivity. If the pings fail, keepalived will fail over to another node and
HAProxy will serve requests there.

The destination address, ping count and ping interval are configurable via
Ansible variables in ``/etc/openstack_deploy/user_variables.yml``:

.. code-block:: yaml

   keepalived_ping_address:         # IP address to ping
   keepalived_ping_count:           # ICMP packets to send (per interval)
   keepalived_ping_interval:        # How often ICMP packets are sent

By default, OpenStack-Ansible will configure keepalived to ping one of the root
DNS servers operated by RIPE. You can change this IP address to a different
external address or another address on your internal network.

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
