`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Aodh service (optional)
---------------------------------------------

The Alarming services of the Telemetry perform the following functions:

  - Creates an API endpoint for controlling alarms.

  - Alows you to set alarms based on threshold evaluation for a collection of samples.

Aodh on OSA requires a mongodb backend to be configured prior to running the aodh
playbooks. The connection data will then need to be given in the ``user_variables.yml``
file (see section `Configuring the user data`_ below).


Setting up a Mongodb database for Aodh
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

5. Create the aodh database

  .. code-block:: shell-session

      # mongo --host controller --eval '
      db = db.getSiblingDB("aodh");
      db.addUser({user: "aodh",
      pwd: "AODH_DBPASS",
      roles: [ "readWrite", "dbAdmin" ]})'

  This should return:

  .. code-block:: shell-session

      MongoDB shell version: 2.4.x
      connecting to: controller:27017/test
      {
       "user" : "aodh",
       "pwd" : "72f25aeee7ad4be52437d7cd3fc60f6f",
       "roles" : [
        "readWrite",
        "dbAdmin"
       ],
       "_id" : ObjectId("5489c22270d7fad1ba631dc3")
      }

  NOTE: The ``AODH_DBPASS`` must match the ``aodh_container_db_password`` in the ``/etc/openstack_deploy/user_secrets.yml`` file. This is how ansible knows how to configure the connection string within the aodh configuration files.

Configuring the hosts
#####################

Aodh can be configured by specifying the ``metering-alarm_hosts`` directive in the ``/etc/openstack_deploy/conf.d/aodh.yml`` file. Below is the example included in the ``etc/openstack_deploy/conf.d/aodh.yml.example`` file:

.. code-block:: yaml

    # The infra nodes that the aodh services will run on.
    metering-alarm_hosts:
      infra1:
        ip: 172.20.236.111
      infra2:
        ip: 172.20.236.112
      infra3:
        ip: 172.20.236.113

The ``metering-alarm_hosts`` houses serveral services:

  - An API server (aodh-api). Runs on one or more central management servers to provide access to the alarm information stored in the data store.

  - An alarm evaluator (aodh-evaluator). Runs on one or more central management servers to determine when alarms fire due to the associated statistic trend crossing a threshold over a sliding time window.

  - A notification listener (aodh-listener). Runs on a central management server and fire alarms based on defined rules against event captured by the Telemetry module's notification agents.

  - An alarm notifier (aodh-notifier). Runs on one or more central management servers to allow alarms to be set based on the threshold evaluation for a collection of samples.

These services communicate by using the OpenStack messaging bus. Only the API server has access to the data store.


Configuring the user data
#########################
In addtion to adding these hosts in the ``/etc/openstack_deploy/conf.d/aodh.yml`` file, other configurations must be specified in the ``/etc/openstack_deploy/user_variables.yml`` file. These configurations are listed below, along with a description:


The type of database backend aodh will use. Currently only mongodb is supported:
``aodh_db_type: mongodb``

The IP address of the MonogoDB host:
``aodh_db_ip: localhost``

The port of the Mongodb service:
``aodh_db_port: 27017``

Once all of these steps are complete, you are ready to run the os-aodh-install.yml playbook! Or, if deploying a new stack, simply run setup-openstack.yml. The aodh playbooks will run as part of this playbook.
