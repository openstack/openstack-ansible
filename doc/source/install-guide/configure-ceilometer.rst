`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Ceilometer service (optional)
---------------------------------------------

The Telemetry module(Ceilometer) performs the following functions:

  - Efficiently polls metering data related to OpenStack services.

  - Collects event and metering data by monitoring notifications sent from services.

  - Publishes collected data to various targets including data stores and message queues.

.. note::

  The alarming functionality was moved to a separate component in Liberty. It will be handled
  by the metering-alarm containers through the aodh services. For configuring these services,
  please see the Aodh docs.

Ceilometer on OSA requires a mongodb backend to be configured prior to running
the ceilometer playbooks. The connection data will then need to be given in the
``user_variables.yml`` file (see section `Configuring the user data`_ below).


Setting up a Mongodb database for ceilometer
############################################

1. Install the MongoDB package:

  .. code-block:: shell-session

    # apt-get install mongodb-server mongodb-clients python-pymongo

2. Edit the ``/etc/mongodb.conf`` file and change the bind_ip to the management interface of the node your running this on.

  .. code-block:: shell-session

    bind_ip = 10.0.0.11

3. Edit the ``/etc/mongodb.conf`` file and enable smallfiles

  .. code-block:: shell-session

    smallfiles = true

4. Restart the mongodb service

  .. code-block:: shell-session

    # service mongodb restart

5. Create the ceilometer database

  .. code-block:: shell-session

      # mongo --host controller --eval '
      db = db.getSiblingDB("ceilometer");
      db.addUser({user: "ceilometer",
      pwd: "CEILOMETER_DBPASS",
      roles: [ "readWrite", "dbAdmin" ]})'

  This should return:

  .. code-block:: shell-session

      MongoDB shell version: 2.4.x
      connecting to: controller:27017/test
      {
       "user" : "ceilometer",
       "pwd" : "72f25aeee7ad4be52437d7cd3fc60f6f",
       "roles" : [
        "readWrite",
        "dbAdmin"
       ],
       "_id" : ObjectId("5489c22270d7fad1ba631dc3")
      }

  NOTE: The ``CEILOMETER_DBPASS`` must match the ``ceilometer_container_db_password`` in the ``/etc/openstack_deploy/user_secrets.yml`` file. This is how ansible knows how to configure the connection string within the ceilometer configuration files.

Configuring the hosts
#####################

Ceilometer can be configured by specifying the ``metering-compute_hosts`` and
``metering-infra_hosts`` directives in the
``/etc/openstack_deploy/conf.d/ceilometer.yml`` file. Below is the example
included in the ``etc/openstack_deploy/conf.d/ceilometer.yml.example`` file:

.. code-block:: yaml

    # The compute host that the ceilometer compute agent will be running on.
    metering-compute_hosts:
      compute1:
        ip: 172.20.236.110

    # The infra node that the central agents will be running on
    metering-infra_hosts:
      infra1:
        ip: 172.20.236.111
      # Adding more than one host requires further configuration for ceilometer
      # to work properly. See 'Configuring the hosts for an HA deployment' section.
      infra2:
        ip: 172.20.236.112
      infra3:
        ip: 172.20.236.113

The ``metering-compute_hosts`` houses the ``ceilometer-agent-compute`` service. It runs on each compute node and pools for resource utilization statistics.
The ``metering-infra_hosts`` houses serveral services:

  - A central agent (ceilometer-agent-central): Runs on a central management server to poll for resource utilization statistics for resources not tied to instances or compute nodes. Multiple agents can be started to enable workload partitioning (See HA section below).

  - A notification agent (ceilometer-agent-notification): Runs on a central management server(s) and consumes messages from the message queue(s) to build event and metering data. Multiple notification agents can be started to enable workload partitioning (See HA section below).

  - A collector (ceilometer-collector): Runs on central management server(s) and dispatches collected telemetry data to a data store or external consumer without modification.

  - An API server (ceilometer-api): Runs on one or more central management servers to provide data access from the data store.

Configuring the hosts for an HA deployment
##########################################
Ceilometer supports running the polling agents and notifications agents in an
HA deployment, meaning that multiple of these services can run in parallel
with workload  among these services.

The Tooz library provides the coordination within the groups of service
instances. Tooz can be uses with several backends. At the time of this
writing, the following backends are supported:

  - Zookeeper. Recommended solution by the Tooz project.

  - Redis. Recommended solution by the Tooz project.

  - Memcached. Recommended for testing.

It's important to note that the OpenStack-Ansible project will not deploy
these backends. Instead, these backends are assumed to exist before
deploying the ceilometer service. HA is achieved by configuring the proper
directives in ceilometer.conf using ``ceilometer_ceilometer_conf_overrides``
in the user_variables.yml file. The Ceilometer admin guide[1] details the
options used in ceilometer.conf for an HA deployment. An example
``ceilometer_ceilometer_conf_overrides`` is provided below.

.. code-block:: yaml

   ceilometer_ceilometer_conf_overrides:
     coordination:
       backend_url: "zookeeper://172.20.1.110:2181"
     notification:
       workload_partitioning: True

Configuring the user data
#########################
In addition to adding these hosts in the
``/etc/openstack_deploy/conf.d/ceilometer.yml`` file, other configurations
must be specified in the ``/etc/openstack_deploy/user_variables.yml`` file.
These configurations are listed below, along with a description:


The type of database backend ceilometer will use. Currently only mongodb is supported:
``ceilometer_db_type: mongodb``

The IP address of the MonogoDB host:
``ceilometer_db_ip: localhost``

The port of the Mongodb service:
``ceilometer_db_port: 27017``

This configures swift to send notifications to the message bus:
``swift_ceilometer_enabled: False``

This configures heat to send notifications to the message bus:
``heat_ceilometer_enabled: False``

This configures cinder to send notifications to the message bus:
``cinder_ceilometer_enabled: False``

This configures glance to send notifications to the message bus:
``glance_ceilometer_enabled: False``

This configures nova to send notifications to the message bus:
``nova_ceilometer_enabled: False``

This configures neutron to send notifications to the message bus:
``neutron_ceilometer_enabled: False``

Once all of these steps are complete, you are ready to run the
os-ceilometer-install.yml playbook! Or, if deploying a new stack, simply run
setup-openstack.yml. The ceilometer playbooks will run as part of this playbook

References
##########
[1] `Ceilometer Admin Guide <http://docs.openstack.org/admin-guide-cloud/telemetry-data-collection.html>`
