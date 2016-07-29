`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Aodh service (optional)
=======================================

The Telemetry (ceilometer) alarming services perform the following functions:

  - Creates an API endpoint for controlling alarms.

  - Allows you to set alarms based on threshold evaluation for a collection of
    samples.



Configuring the hosts
~~~~~~~~~~~~~~~~~~~~~

Configure Aodh by specifying the ``metering-alarm_hosts`` directive in
the ``/etc/openstack_deploy/conf.d/aodh.yml`` file. The following shows
the example included in the
``etc/openstack_deploy/conf.d/aodh.yml.example`` file:

  .. code-block:: yaml

     # The infra nodes that the Aodh services run on.
     metering-alarm_hosts:
       infra1:
         ip: 172.20.236.111
       infra2:
         ip: 172.20.236.112
       infra3:
         ip: 172.20.236.113

The ``metering-alarm_hosts`` provides several services:

  - An API server (``aodh-api``): Runs on one or more central management
    servers to provide access to the alarm information in the
    data store.

  - An alarm evaluator (``aodh-evaluator``): Runs on one or more central
    management servers to determine alarm fire due to the
    associated statistic trend crossing a threshold over a sliding
    time window.

  - A notification listener (``aodh-listener``): Runs on a central
    management server and fire alarms based on defined rules against
    event captured by ceilometer's module's notification agents.

  - An alarm notifier (``aodh-notifier``). Runs on one or more central
    management servers to allow the setting of alarms to base on the
    threshold evaluation for a collection of samples.

These services communicate by using the OpenStack messaging bus. Only
the API server has access to the data store.

Run the ``os-aodh-install.yml`` playbook. If deploying a new OpenStack
(instead of only Aodh), run ``setup-openstack.yml``.
The Aodh playbooks run as part of this playbook.

--------------

.. include:: navigation.txt
