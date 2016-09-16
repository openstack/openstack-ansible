========
Affinity
========

OpenStack-Ansible's dynamic inventory generation has a concept called
`affinity`. This determines how many containers of a similar type are deployed
onto a single physical host.

Using `shared-infra_hosts` as an example, consider this
``openstack_user_config.yml``:

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
a single memcached container, and a single RabbitMQ container. Each host has
an affinity of 1 by default, and that means each host will run one of each
container type.

You can skip the deployment of RabbitMQ altogether. This is
helpful when deploying a standalone swift environment. If you need
this configuration, your ``openstack_user_config.yml`` would look like this:

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

The configuration above deploys a memcached container and a database
container on each host, without the RabbitMQ containers.

