.. _configure:

========================
Configure the deployment
========================

.. figure:: figures/installation-workflow-configure-deployment.png
   :width: 100%

Ansible references some files that contain mandatory and optional
configuration directives. Before you can run the Ansible playbooks, modify
these files to define the target environment. Configuration tasks include:

* Target host networking to define bridge interfaces and
  networks.
* A list of target hosts on which to install the software.
* Virtual and physical network relationships for OpenStack
  Networking (neutron).
* Passwords for all services.

Initial environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible (OSA) depends on various files that are used to build an
inventory for Ansible. Perform the following configuration on the deployment
host.

#. Copy the contents of the
   ``/opt/openstack-ansible/etc/openstack_deploy`` directory to the
   ``/etc/openstack_deploy`` directory.

#. Change to the ``/etc/openstack_deploy`` directory.

#. Copy the ``openstack_user_config.yml.example`` file to
   ``/etc/openstack_deploy/openstack_user_config.yml``.

#. Review the ``openstack_user_config.yml`` file and make changes
   to the deployment of your OpenStack environment.

   .. note::

      The file is heavily commented with details about the various options.

The configuration in the ``openstack_user_config.yml`` file defines which hosts
run the containers and services deployed by OpenStack-Ansible. For
example, hosts listed in the ``shared-infra_hosts`` section run containers for
many of the shared services that your OpenStack environment requires. Some of
these services include databases, Memcached, and RabbitMQ. Several other
host types contain other types of containers, and all of these are listed
in the ``openstack_user_config.yml`` file.

For examples, please see :ref:`test-environment-config` and
:ref:`production-environment-config`.

For details about how the inventory is generated from the environment
configuration, see
`developer-inventory <http://docs.openstack.org/developer/openstack-ansible/developer-docs/inventory.html>`_.

Installing additional services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install additional services, the files in
``/etc/openstack_deploy/conf.d`` provide examples showing
the correct host groups to use. To add another service, add the host group,
allocate hosts to it, and then execute the playbooks.

Advanced service configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible has many options that you can use for the advanced
configuration of services. Each role's documentation provides information
about the available options.

Infrastructure service roles
----------------------------

- `galera_server
  <http://docs.openstack.org/developer/openstack-ansible-galera_server>`_

- `haproxy_server
  <http://docs.openstack.org/developer/openstack-ansible-haproxy_server>`_

- `memcached_server
  <http://docs.openstack.org/developer/openstack-ansible-memcached_server>`_

- `rabbitmq_server
  <http://docs.openstack.org/developer/openstack-ansible-rabbitmq_server>`_

- `repo_build
  <http://docs.openstack.org/developer/openstack-ansible-repo_build>`_

- `repo_server
  <http://docs.openstack.org/developer/openstack-ansible-repo_server>`_

- `rsyslog_server
  <http://docs.openstack.org/developer/openstack-ansible-rsyslog_server>`_


OpenStack service roles
-----------------------

-  `os_aodh <http://docs.openstack.org/developer/openstack-ansible-os_aodh>`_

-  `os_barbican
   <http://docs.openstack.org/developer/openstack-ansible-os_barbican>`_

-  `os_ceilometer
   <http://docs.openstack.org/developer/openstack-ansible-os_ceilometer>`_

-  `os_cinder
   <http://docs.openstack.org/developer/openstack-ansible-os_cinder>`_

-  `os_designate
   <http://docs.openstack.org/developer/openstack-ansible-os_designate>`_

-  `os_glance
   <http://docs.openstack.org/developer/openstack-ansible-os_glance>`_

-  `os_gnocchi
   <http://docs.openstack.org/developer/openstack-ansible-os_gnocchi>`_

-  `os_heat <http://docs.openstack.org/developer/openstack-ansible-os_heat>`_

-  `os_horizon
   <http://docs.openstack.org/developer/openstack-ansible-os_horizon>`_

-  `os_ironic
   <http://docs.openstack.org/developer/openstack-ansible-os_ironic>`_

-  `os_keystone
   <http://docs.openstack.org/developer/openstack-ansible-os_keystone>`_

-  `os_magnum
   <http://docs.openstack.org/developer/openstack-ansible-os_magnum>`_

-  `os_neutron
   <http://docs.openstack.org/developer/openstack-ansible-os_neutron>`_

-  `os_nova <http://docs.openstack.org/developer/openstack-ansible-os_nova>`_

-  `os_rally <http://docs.openstack.org/developer/openstack-ansible-os_rally>`_

-  `os_sahara
   <http://docs.openstack.org/developer/openstack-ansible-os_sahara>`_

-  `os_swift <http://docs.openstack.org/developer/openstack-ansible-os_swift>`_

-  `os_tempest
   <http://docs.openstack.org/developer/openstack-ansible-os_tempest>`_

-  `os_trove <http://docs.openstack.org/developer/openstack-ansible-os_trove>`_


Other roles
-----------

- `ansible-plugins
  <http://docs.openstack.org/developer/openstack-ansible-plugins>`_

- `apt_package_pinning
  <http://docs.openstack.org/developer/openstack-ansible-apt_package_pinning/>`_

- `ceph_client
  <http://docs.openstack.org/developer/openstack-ansible-ceph_client>`_

- `galera_client
  <http://docs.openstack.org/developer/openstack-ansible-galera_client>`_

- `lxc_container_create
  <http://docs.openstack.org/developer/openstack-ansible-lxc_container_create>`_

- `lxc_hosts
  <http://docs.openstack.org/developer/openstack-ansible-lxc_hosts>`_

- `pip_install
  <http://docs.openstack.org/developer/openstack-ansible-pip_install/>`_

- `openstack_openrc
  <http://docs.openstack.org/developer/openstack-ansible-openstack_openrc>`_

- `openstack_hosts
  <http://docs.openstack.org/developer/openstack-ansible-openstack_hosts>`_

- `rsyslog_client
  <http://docs.openstack.org/developer/openstack-ansible-rsyslog_client>`_

Configuring service credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure credentials for each service in the
``/etc/openstack_deploy/*_secrets.yml`` files. Consider using the
`Ansible Vault <http://docs.ansible.com/playbooks_vault.html>`_ feature to
increase security by encrypting any files that contain credentials.

Adjust permissions on these files to restrict access by nonprivileged
users.

The ``keystone_auth_admin_password`` option configures the ``admin`` tenant
password for both the OpenStack API and Dashboard access.

We recommend that you use the ``pw-token-gen.py`` script to generate random
values for the variables in each file that contains service credentials:

   .. code-block:: shell-session

      # cd /opt/openstack-ansible/scripts
      # python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml

To regenerate existing passwords, add the ``--regen`` flag.

.. warning::

   The playbooks do not currently manage changing passwords in an existing
   environment. Changing passwords and rerunning the playbooks will fail
   and might break your OpenStack environment.
