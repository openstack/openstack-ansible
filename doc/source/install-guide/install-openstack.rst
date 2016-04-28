`Home <index.html>`_ OpenStack-Ansible Installation Guide

==============================
Chapter 7. OpenStack playbooks
==============================

**Figure 7.1. Installation work flow**

.. image:: figures/workflow-openstackplaybooks.png

The main Ansible OpenStack playbook installs OpenStack services and
performs the following operations:

-  Install common components

-  Create a utility container that provides utilities to interact with
   services in other containers

-  Install Identity (keystone)

-  Generate service IDs for all services

-  Install the Image service (glance)

-  Install Orchestration (heat)

-  Install Compute (nova)

-  Install Networking (neutron)

-  Install Block Storage (cinder)

-  Install Dashboard (horizon)

-  Reconfigure Rsyslog

Running the OpenStack playbook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Change to the ``/opt/openstack-ansible/playbooks`` directory.

#. Run the OpenStack setup playbook:

   .. code-block:: shell-session

       # openstack-ansible setup-openstack.yml

   The ``openstack-common.yml`` sub-playbook builds all OpenStack services
   from source and takes up to 30 minutes to complete. As the playbook
   progresses, the quantity of containers in the polling state
   approaches zero. If any operations take longer than 30 minutes to
   complete, the playbook terminates with an error.

   .. code-block:: shell-session

       changed: [target_host_glance_container-f2ebdc06]
       changed: [target_host_heat_engine_container-36022446]
       changed: [target_host_neutron_agents_container-08ec00cd]
       changed: [target_host_heat_apis_container-4e170279]
       changed: [target_host_keystone_container-c6501516]
       changed: [target_host_neutron_server_container-94d370e5]
       changed: [target_host_nova_api_metadata_container-600fe8b3]
       changed: [target_host_nova_compute_container-7af962fe]
       changed: [target_host_cinder_api_container-df5d5929]
       changed: [target_host_cinder_volumes_container-ed58e14c]
       changed: [target_host_horizon_container-e68b4f66]
       <job 802849856578.7262> finished on target_host_heat_engine_container-36022446
       <job 802849856578.7739> finished on target_host_keystone_container-c6501516
       <job 802849856578.7262> finished on target_host_heat_apis_container-4e170279
       <job 802849856578.7359> finished on target_host_cinder_api_container-df5d5929
       <job 802849856578.7386> finished on target_host_cinder_volumes_container-ed58e14c
       <job 802849856578.7886> finished on target_host_horizon_container-e68b4f66
       <job 802849856578.7582> finished on target_host_nova_compute_container-7af962fe
       <job 802849856578.7604> finished on target_host_neutron_agents_container-08ec00cd
       <job 802849856578.7459> finished on target_host_neutron_server_container-94d370e5
       <job 802849856578.7327> finished on target_host_nova_api_metadata_container-600fe8b3
       <job 802849856578.7363> finished on target_host_glance_container-f2ebdc06
       <job 802849856578.7339> polling, 1675s remaining
       <job 802849856578.7338> polling, 1675s remaining
       <job 802849856578.7322> polling, 1675s remaining
       <job 802849856578.7319> polling, 1675s remaining

   Setting up the compute hosts takes up to another 30 minutes to
   complete, particularly in environments with many compute hosts. If
   any operations take longer than 30 minutes to complete, the playbook
   terminates with an error.

   .. code-block:: shell-session

       ok: [target_host_nova_conductor_container-2b495dc4]
       ok: [target_host_nova_api_metadata_container-600fe8b3]
       ok: [target_host_nova_api_ec2_container-6c928c30]
       ok: [target_host_nova_scheduler_container-c3febca2]
       ok: [target_host_nova_api_os_compute_container-9fa0472b]
       <job 409029926086.9909> finished on target_host_nova_api_os_compute_container-9fa0472b
       <job 409029926086.9890> finished on target_host_nova_api_ec2_container-6c928c30
       <job 409029926086.9910> finished on target_host_nova_conductor_container-2b495dc4
       <job 409029926086.9882> finished on target_host_nova_scheduler_container-c3febca2
       <job 409029926086.9898> finished on target_host_nova_api_metadata_container-600fe8b3
       <job 409029926086.8330> polling, 1775s remaining

   Confirm satisfactory completion with zero items unreachable or
   failed:

   .. code-block:: shell-session

       PLAY RECAP **********************************************************************
       ...
       deployment_host                :  ok=44   changed=11   unreachable=0    failed=0

Utility container
~~~~~~~~~~~~~~~~~

The utility container provides a space where miscellaneous tools and
software are installed. Tools and objects are placed in a
utility container if they do not require a dedicated container or if it
is impractical to create a new container for a single tool or object.
Utility containers are also used when tools cannot be installed
directly onto a host.

For example, the tempest playbooks are installed on the utility
container since tempest testing does not need a container of its own.

Verifying OpenStack operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify basic operation of the OpenStack API and dashboard.

**Procedure 8.1. Verifying the API**

The utility container provides a CLI environment for additional
configuration and testing.

#. Determine the utility container name:

   .. code-block:: shell-session

       # lxc-ls | grep utility
       infra1_utility_container-161a4084

#. Access the utility container:

   .. code-block:: shell-session

       # lxc-attach -n infra1_utility_container-161a4084

#. Source the ``admin`` tenant credentials:

   .. code-block:: shell-session

       # source /root/openrc

#. Run an OpenStack command that uses one or more APIs. For example:

   .. code-block:: shell-session

       # openstack user list
       +----------------------------------+--------------------+
       | ID                               | Name               |
       +----------------------------------+--------------------+
       | 08fe5eeeae314d578bba0e47e7884f3a | alt_demo           |
       | 0aa10040555e47c09a30d2240e474467 | dispersion         |
       | 10d028f9e47b4d1c868410c977abc3df | glance             |
       | 249f9ad93c024f739a17ca30a96ff8ee | demo               |
       | 39c07b47ee8a47bc9f9214dca4435461 | swift              |
       | 3e88edbf46534173bc4fd8895fa4c364 | cinder             |
       | 41bef7daf95a4e72af0986ec0583c5f4 | neutron            |
       | 4f89276ee4304a3d825d07b5de0f4306 | admin              |
       | 943a97a249894e72887aae9976ca8a5e | nova               |
       | ab4f0be01dd04170965677e53833e3c3 | stack_domain_admin |
       | ac74be67a0564722b847f54357c10b29 | heat               |
       | b6b1d5e76bc543cda645fa8e778dff01 | ceilometer         |
       | dc001a09283a404191ff48eb41f0ffc4 | aodh               |
       | e59e4379730b41209f036bbeac51b181 | keystone           |
       +----------------------------------+--------------------+

**Procedure 8.2. Verifying the dashboard**

#. With a web browser, access the dashboard using the external load
   balancer IP address defined by the ``external_lb_vip_address`` option
   in the ``/etc/openstack_deploy/openstack_user_config.yml`` file. The
   dashboard uses HTTPS on port 443.

#. Authenticate using the username ``admin`` and password defined by the
   ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_variables.yml`` file.

.. note::

   Only users with administrator privileges can upload public images
   using the dashboard or CLI.

--------------

.. include:: navigation.txt
