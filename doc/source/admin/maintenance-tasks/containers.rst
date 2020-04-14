Container management
====================

With Ansible, the OpenStack installation process is entirely automated
using playbooks written in YAML. After installation, the settings
configured by the playbooks can be changed and modified. Services and
containers can shift to accommodate certain environment requirements.
Scaling services are achieved by adjusting services within containers, or
adding new deployment groups. It is also possible to destroy containers,
if needed, after changes and modifications are complete.

Scale individual services
-------------------------

Individual OpenStack services, and other open source project services,
run within containers. It is possible to scale out these services by
modifying the ``/etc/openstack_deploy/openstack_user_config.yml`` file.

#. Navigate into the ``/etc/openstack_deploy/openstack_user_config.yml``
   file.

#. Access the deployment groups section of the configuration file.
   Underneath the deployment group name, add an affinity value line to
   container scales OpenStack services:

   .. code::

      infra_hosts:
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

Destroy and recreate containers
-------------------------------

Resolving some issues may require destroying a container, and rebuilding
that container from the beginning. It is possible to destroy and
re-create a container with the ``lxc-containers-destroy.yml`` and
``lxc-containers-create.yml`` commands. These Ansible scripts reside in the
``openstack-ansible/playbooks`` repository.

#. Navigate to the ``openstack-ansible`` directory.

#. Run the **openstack-ansible lxc-containers-destroy.yml** commands,
   specifying the target containers and the container to be destroyed.

   .. code::

      $ openstack-ansible lxc-containers-destroy.yml --limit "CONTAINER_NAME"
      $ openstack-ansible lxc-containers-create.yml --limit "CONTAINER_NAME"

#. Replace *``CONTAINER_NAME``* with the target container.
