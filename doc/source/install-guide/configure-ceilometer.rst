`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Ceilometer service (optional)
---------------------------------------------

The Telemetry module(Ceilometer) performs the following functions:

  - Efficiently polls metering data related to OpenStack services.

  - Collects event and metering data by monitoring notifications sent from services.

  - Publishes collected data to various targets including data stores and message queues.

  - Creates alarms when collected data breaks defined rules.

Ceilometer on OSA requires a monogodb backend to be configured prior to running the ceilometer
playbooks. The connection data will then need to be given in the ``user_variables.yml``
file (see section `Configuring the user data`_ below).


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

Ceilometer can be configured by specifying the ``metering-compute_hosts`` and ``metering-infra_hosts`` directives in the ``/etc/openstack_deploy/conf.d/ceilometer.yml`` file. Below is the example included in the ``etc/openstack_deploy/conf.d/ceilometer.yml.example`` file:

.. code-block:: yaml

    # The compute host that the ceilometer compute agent will be running on.
    metering-compute_hosts:
      compute1:
        ip: 172.20.236.110

    # The infra nodes that the central agents will be running on
    metering-infra_hosts:
      infra1:
        ip: 172.20.236.111
      infra2:
        ip: 172.20.236.112
      infra3:
        ip: 172.20.236.113

The ``metering-compute_hosts`` houses the ``ceilometer-agent-compute`` service. It runs on each compute node and pools for resource utilization statistics.
The ``metering-infra_hosts`` houses serveral services:

  - A central agent (ceilometer-agent-central): Runs on a central management server to poll for resource utilization statistics for resources not tied to instances or compute nodes. Multiple agents can be started to scale service horizontally.

  - A notification agent (ceilometer-agent-notification): Runs on a central management server(s) and consumes messages from the message queue(s) to build event and metering data.

  - A collector (ceilometer-collector): Runs on central management server(s) and dispatches collected telemetry data to a data store or external consumer without modification.

  - An alarm evaluator (ceilometer-alarm-evaluator): Runs on one or more central management servers to determine when alarms fire due to the associated statistic trend crossing a threshold over a sliding time window.

  - An alarm notifier (ceilometer-alarm-notifier): Runs on one or more central management servers to allow alarms to be set based on the threshold evaluation for a collection of samples.

  - An API server (ceilometer-api): Runs on one or more central management servers to provide data access from the data store.


Configuring the user data
#########################
In addtion to adding these hosts in the ``/etc/openstack_deploy/conf.d/ceilometer.yml`` file, other configurations must be specified in the ``/etc/openstack_deploy/user_variable.yml`` file. These configurations are listed below, along with a description:


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


Once all of these steps are complete, you are ready to run the os-ceilometer-install.yml playbook! Or, if deploying a new stack, simply run setup-openstack.yml. The ceilometer playbooks will run as part of this playbook.
