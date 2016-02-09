`Home <index.html>`_ OpenStack-Ansible Installation Guide

Centralized Logging
-------------------

OpenStack-Ansible will configure all instances to send syslog data to a
container (or group of containers) running rsyslog.  The rsyslog server
containers are specified in the ``log_hosts`` section of the
``openstack_user_config.yml`` file.

The rsyslog server container(s) have logrotate installed and configured with
a 14 day retention.  All rotated logs are compressed by default.

Finding logs
~~~~~~~~~~~~

Logs are accessible in multiple locations within an OpenStack-Ansible
deployment:

* The rsyslog server container collects logs in ``/var/log/log-storage`` within
  directories named after the container or physical host
* Each physical host has the logs from its service containers mounted at
  ``/openstack/log/``
* Each service container has its own logs stored at ``/var/log/<service_name>``
