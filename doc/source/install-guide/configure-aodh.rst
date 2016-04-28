`Home <index.html>`_ OpenStack-Ansible Installation Guide

=======================================
Configuring the Aodh service (optional)
=======================================

The Telemetry Alarming services perform the following functions:

  - Creates an API endpoint for controlling alarms.

  - Allows you to set alarms based on threshold evaluation for a collection of samples.

Aodh on OSA requires a configured MongoDB back end prior to running
the Aodh playbooks. To specify the connection data, the deployer has to edit in the
``user_variables.yml`` file (see section `Configuring the user data`_
below).


Setting up a MongoDB database for Aodh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install the MongoDB package:

  .. code-block:: console

     # apt-get install mongodb-server mongodb-clients python-pymongo


2. Edit the ``/etc/mongodb.conf`` file and change ``bind_ip`` to the
   management interface of the node running Aodh.

  .. code-block:: ini

     bind_ip = 10.0.0.11


3. Edit the ``/etc/mongodb.conf`` file and enable smallfiles:

  .. code-block:: ini

     smallfiles = true


4. Restart the MongoDB service:

  .. code-block:: console

     # service mongodb restart


5. Create the Aodh database

  .. code-block:: console

     # mongo --host controller --eval 'db = db.getSiblingDB("aodh"); db.addUser({user: "aodh", pwd: "AODH_DBPASS", roles: [ "readWrite", "dbAdmin" ]});'


  This returns:

  .. code-block:: console

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


  .. note:: The ``AODH_DBPASS`` must match the
            ``aodh_container_db_password`` in the
            ``/etc/openstack_deploy/user_secrets.yml`` file. This
            allows Ansible to configure the connection string within
            the Aodh configuration files.


Configuring the hosts
~~~~~~~~~~~~~~~~~~~~~

Configure Aodh by specifying the ``metering-alarm_hosts`` directive in
the ``/etc/openstack_deploy/conf.d/aodh.yml`` file. The following shows
the example included in the
``etc/openstack_deploy/conf.d/aodh.yml.example`` file:

  .. code-block:: yaml

     # The infra nodes that the aodh services will run on.
     metering-alarm_hosts:
       infra1:
         ip: 172.20.236.111
       infra2:
         ip: 172.20.236.112
       infra3:
         ip: 172.20.236.113

The ``metering-alarm_hosts`` provides several services:

  - An API server (aodh-api). Runs on one or more central management
    servers to provide access to the alarm information stored in the
    data store.

  - An alarm evaluator (aodh-evaluator). Runs on one or more central
    management servers to determine when alarms fire due to the
    associated statistic trend crossing a threshold over a sliding
    time window.

  - A notification listener (aodh-listener). Runs on a central
    management server and fire alarms based on defined rules against
    event captured by the Telemetry module's notification agents.

  - An alarm notifier (aodh-notifier). Runs on one or more central
    management servers to allow alarms to be set based on the
    threshold evaluation for a collection of samples.

These services communicate by using the OpenStack messaging bus. Only
the API server has access to the data store.


Configuring the user data
~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to adding these hosts in the
``/etc/openstack_deploy/conf.d/aodh.yml`` file, other configurations
must be specified in the ``/etc/openstack_deploy/user_variables.yml``
file. These configurations are listed below, along with a description:


  - The type of database backend aodh will use. Currently only MongoDB
    is supported: ``aodh_db_type: mongodb``

  - The IP address of the MonogoDB host: ``aodh_db_ip: localhost``

  - The port of the MongoDB service: ``aodh_db_port: 27017``

After all of these steps are complete, run the ``os-aodh-install.yml``
playbook. If deploying a new openstack (instead of only aodh),
run ``setup-openstack.yml``. The aodh playbooks run as part of this
playbook.

--------------

.. include:: navigation.txt
