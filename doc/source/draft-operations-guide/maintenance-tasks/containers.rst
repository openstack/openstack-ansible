====================
Container management
====================

With Ansible, the OpenStack installation process is entirely automated
using playbooks written in YAML. After installation, the settings
configured by the playbooks can be changed and modified. Services and
containers can shift to accommodate certain environment requirements.
Scaling services is achieved by adjusting services within containers, or
adding new deployment groups. It is also possible to destroy containers
if needed after changes and modifications are complete.

Scale individual services
~~~~~~~~~~~~~~~~~~~~~~~~~

Individual OpenStack services, and other open source project services,
run within containers. It is possible to scale out these services by
modifying the ``etc/openstack_deploy/openstack_user_config.yml`` file.

#. Navigate into the ``etc/openstack_deploy/openstack_user_config.yml``
   file.

#. Access the deployment groups section of the configuration file.
   Underneath the deployment group name, add an affinity value line to
   container scales OpenStack services:

   .. code::

      infra_host
        infra1:
          ip: 10.10.236.100
          # Rabbitmq
          affinity:
            galera_container: 1
            rabbit_mq_container: 2

   In this example, ``galera_container`` has a container value of one.
   In practice, any containers that do not need adjustment can remain at
   the default value of one, and should not be adjusted above or below
   the value of one.

   The affinity value for each container is set at one by default.
   Adjust the affinity value to zero for situations where the OpenStack
   services housed within a specific container will not be needed when
   scaling out other required services.

#. Update the container number listed under the ``affinity``
   configuration to the desired number. The above example has
   ``galera_container`` set at one and ``rabbit_mq_container`` at two,
   which scales RabbitMQ services, but leaves Galera services fixed.

#. Run the appropriate playbook commands after changing the
   configuration to create the new containers, and install the
   appropriate services.

   For example, run the **openstack-ansible lxc-containers-create.yml
   rabbitmq-install.yml** commands from the
   ``openstack-ansible/playbooks`` repository to complete the scaling
   process described in the example above:

   .. code::

      $ cd openstack-ansible/playbooks
      $ openstack-ansible lxc-containers-create.yml rabbitmq-install.yml

Scale services with new deployment groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In any OpenStack environment installed with Ansible, Deployment Groups
reside on specific nodes. Specific groups of containers are collected
open source project services, run within containers.

For example, the ``compute_hosts ``\ deployment group holds the
``nova_compute_container``, which contains the
``neutron_linuxbridge_agent`` and ``nova_compute`` OpenStack services.
This deployment group resides on the compute node.

Users can create new infrastructure nodes, and scale OpenStack services
within containers, by generating new deployment groups. The process
requires setting up a new deployment groups inside the host
configuration files.

#. On the host machine, navigate to the directory where
   ``openstack_config`` file resides. This configuration file
   defines which deployment groups are assigned to each node.

#. Add a new deployment group to the configuration file. Adjust the
   deployment group name followed by the affinity values within the
   deployment group section of the ``openstack_config`` config file to
   scale services.

   .. code::

      compute_hosts
      infra_hosts
      identity_hosts
      log_hosts
      network_hosts
      os-infra_hosts
      repo-infra_hosts
      shared-infra_hosts
      storage-infra_hosts
      storage_hosts
      swift_hosts
      swift-proxy_hosts

#. Modify the ``openstack_config`` file, adding containers for the new
   deployment group.

#. Specify the required affinity levels. Add a zero value for any
   OpenStack or open source services not needed that would ordinarily
   run on the deployment group.

   For example, to add a new deployment group with nova\_api and
   cinder\_api services reconfigure the ``openstack_config`` file:

   .. code::

       os-infra_hosts:
         my_new_node:
           ip: 3.4.5.6
           affinity:
             glance_container: 0
             heat_apis_container: 0
             heat_engine_container: 0
             horizon_container: 0
             nova_api_metadata_container: 0
             nova_cert_container: 0
             nova_conductor_container: 0
             nova_scheduler_container: 0
             nova_console_container: 0

   ``my_new_node`` is the name for the new deployment group.
   ``ip 3.4.5.6`` is the ip address assigned to the new deployment
   group.

#. As another example, a new deployment group that houses the
   ``cinder_api`` would have the following values:

   .. code::

       storage-infra_hosts:
         my_new_node:
           ip: 3.4.5.6
           affinity:
           cinder_api_container: 0

   The ``storage-infra_host`` contains only the ``cinder_api`` services.

Destroy and recreate containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resolving some issues may require destroying a container, and rebuilding
that container from the beginning. It is possible to destroy and
re-create a container with the ``destroy-containers.yml`` and
``build-containers.yml`` commands. These Ansible scripts reside in the
``openstack-ansible/playbooks`` repository.

#. Navigate to the ``openstack-ansible`` directory.

#. Run the **openstack-ansible destroy-containers.yml** commands,
   specifying the target containers and the container to be destroyed.

   .. code::

      $ openstack-ansible destroy-containers.yml \
      build-containers.yml OTHER_PLAYS -e container_group="CONTAINER_NAME"

#. Replace *``OTHER_PLAYS``* with the target container, and replace

#. Change the load balancer configuration to match the newly recreated
   container identity if needed.

Archive a container
~~~~~~~~~~~~~~~~~~~

If a container experiences a problem and needs to be deactivated, it is
possible to flag the container as inactive, and archive it in the
``/tmp`` directory.

#. Change into the playbooks directory.

#. Run the **openstack-ansible** with the **-e** argument, and replace
   *``HOST_NAME``* and *``          CONTAINER_NAME``* options with the
   applicable host and container names.

   .. code::

      $ openstack-ansible -e \
      "host_group=HOST_NAME,container_name=CONTAINER_NAME" \
      setup/archive-container.yml

   By default, Ansible archives the container contents to the ``/tmp``
   directory on the host machine.
