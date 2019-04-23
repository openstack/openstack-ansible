==============================================
Telemetry with Gnocchi, Ceph and Redis example
==============================================

The default openstack-ansible installation configures gnocchi to use a file as
storage backend. When you already have a pre-installed ceph, you can use this
as backend for gnocchi. This documentation will guide you how to set up
gnocchi to use your ceph as storage backend.

Ceph as metric storage
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    gnocchi_storage_driver: ceph

You have to add some pip packages to your gnocchi setup:

.. code-block:: yaml

    gnocchi_pip_packages:
    - cryptography
    - gnocchiclient
    # this is what we want:
    #  - "gnocchi[mysql,ceph,ceph_alternative_lib,redis]"
    # but as there is no librados >=12.2 pip package we have to first install ceph without alternative support
    # after adding the ceph repo to gnocchi container, python-rados>=12.2.0 is installed and linked automatically
    # and gnocchi will automatically take up the features present in the used rados lib.
    - "gnocchi[mysql,ceph,redis]"
    - keystonemiddleware
    - python-memcached

But when your setup grows, gnocchi might slow down or block your ceph
installation. You might experience slow requests and stuck PGs in your Ceph.
As this might have multiple causes, take a look at the presentations linked
in the `Performance Tests for Gnocchi`_ section. They also include various
parameters which you might tune.

Redis as measure storage
~~~~~~~~~~~~~~~~~~~~~~~~

One solution to possible performance problems is to use an incoming measure
storage for your gnocchi installation. The `supported storage systems`_ are:

* File (default)
* Ceph (preferred)
* OpenStack Swift
* Amazon S3
* Redis

.. _supported storage systems: https://gnocchi.xyz/intro.html#incoming-and-storage-drivers

When your Swift installation uses Ceph as backend, the only one left for this
setup is Redis.

So first of all setup a redis server/cluster, e.g. with this `ansible role`_.
Next, you have to configure Gnocchi with OpenStack-Ansible to use the Redis
Cluster as incoming storage:

.. _ansible role: https://github.com/DavidWittman/ansible-redis

.. code-block:: yaml

    gnocchi_conf_overrides:
      incoming:
        driver: redis
        redis_url: redis://{{ hostvars[groups['redis-master'][0]]['ansible_default_ipv4']['address'] }}:{{ hostvars[groups['redis-master'][0]]['redis_sentinel_port'] }}?sentinel=master01{% for host in groups['redis-slave'] %}&sentinel_fallback={{ hostvars[host]['ansible_default_ipv4']['address'] }}:{{ hostvars[host]['redis_sentinel_port'] }}{% endfor %}

You also have to install additional pip/distro packages to use the redis
cluster:

.. code-block:: yaml

    gnocchi_distro_packages:
    - apache2
    - apache2-utils
    - libapache2-mod-wsgi
    - git
    - build-essential
    - python-dev
    - libpq-dev
    - python-rados
    # additional package for python redis client
    - python-redis

.. code-block:: yaml

    gnocchi_pip_packages:
    - cryptography
    - gnocchiclient
    # this is what we want:
    #  - "gnocchi[mysql,ceph,ceph_alternative_lib,redis]"
    # but as there is no librados >=12.2 pip package we have to first install ceph without alternative support
    # after adding the ceph repo to gnocchi container, python-rados>=12.2.0 is installed and linked automatically
    # and gnocchi will automatically take up the features present in the used rados lib.
    - "gnocchi[mysql,ceph,redis]"
    - keystonemiddleware
    - python-memcached
    - redis

.. note::

    A word of caution: the name of the Ceph alternative lib implementation (ceph_alternative_lib) varies between Gnocchi versions.

Zookeeper for coordination
~~~~~~~~~~~~~~~~~~~~~~~~~~

When you deployed Gnocchi on multiple servers to distribute the work,
add Zookeeper as coordination backend. To setup Zookeeper, you can use
`this ansible role`_.

.. _this ansible role: https://github.com/openstack/ansible-role-zookeeper.git

Create containers for Zookeeper:

.. code-block:: console

    ## conf.d
    zookeeper_hosts:
    {% for server in groups['control_nodes'] %}
    {{ server }}:
      ip: {{ hostvars[server]['ansible_default_ipv4']['address'] }}
    {% endfor%}

.. code-block:: console

    ## env.d
    component_skel:
      zookeeper_server:
        belongs_to:
          - zookeeper_all

    container_skel:
      zookeeper_container:
        belongs_to:
          - infra_containers
          - shared-infra_containers
        contains:
          - zookeeper_server
        properties:
          service_name: zookeeper

Now you can set up Zookeeper as coordination backend for Gnocchi:

.. code-block:: console

    gnocchi_coordination_url: "zookeeper://{% for host in groups['zookeeper_all'] %}{{ hostvars[host]['container_address'] }}:2181{% if not loop.last %},{% endif %}{% endfor %}"

You also have to install additional packages:

.. code-block:: console

    gnocchi_pip_packages:
    - cryptography
    - gnocchiclient
    # this is what we want:
    #  - "gnocchi[mysql,ceph,ceph_alternative_lib,redis]"
    # but as there is no librados >=12.2 pip package we have to first install ceph without alternative support
    # after adding the ceph repo to gnocchi container, python-rados>=12.2.0 is installed and linked automatically
    # and gnocchi will automatically take up the features present in the used rados lib.
    - "gnocchi[mysql,ceph,redis]"
    - keystonemiddleware
    - python-memcached
    - redis
    # addiitional pip packages needed for zookeeper coordination backend
    - tooz
    - lz4
    - kazoo

Performance Tests for Gnocchi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more ideas how to tune your Gnocchi stack, take a look at these
presentations:

* https://docs.openstack.org/developer/performance-docs/test_results/telemetry_gnocchi_with_ceph/index.html
