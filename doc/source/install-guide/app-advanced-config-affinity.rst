========
Affinity
========

When OpenStack-Ansible generates its dynamic inventory, the affinity
setting determines how many containers of a similar type are deployed on a
single physical host.

Using ``shared-infra_hosts`` as an example, consider this
``openstack_user_config.yml`` configuration:

.. code-block:: yaml

    shared-infra_hosts:
      infra1:
        ip: 172.29.236.101
      infra2:
        ip: 172.29.236.102
      infra3:
        ip: 172.29.236.103

Three hosts are assigned to the `shared-infra_hosts` group,
OpenStack-Ansible ensures that each host runs a single database container,
a single Memcached container, and a single RabbitMQ container. Each host has
an affinity of 1 by default,  which means that each host runs one of each
container type.

If you are deploying a stand-alone Object Storage (swift) environment,
you can skip the deployment of RabbitMQ. If you use this configuration,
your ``openstack_user_config.yml`` file would look as follows:

.. code-block:: yaml

    shared-infra_hosts:
      infra1:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.101
      infra2:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.102
      infra3:
        affinity:
          rabbit_mq_container: 0
        ip: 172.29.236.103

This configuration deploys a Memcached container and a database container
on each host, but no RabbitMQ containers.

