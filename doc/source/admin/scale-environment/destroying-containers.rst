Destroying containers
~~~~~~~~~~~~~~~~~~~~~

#. To destroy a container, execute the following:

   .. code-block:: console

      # openstack-ansible openstack.osa.containers_lxc_destroy --limit localhost,<container name|container group>

   .. note::

      You will be asked two questions:

       Are you sure you want to destroy the LXC containers?
       Are you sure you want to destroy the LXC container data?

       The first will just remove the container but leave the data in the bind mounts and logs.
       The second will remove the data in the bind mounts and logs too.

   .. warning::
      If you remove the containers and data for the entire galera_server container group you
      will lose all your databases! Also, if you destroy the first container in many host groups
      you will lose other important items like certificates, keys, etc. Be sure that you
      understand what you're doing when using this tool.

#. To create the containers again, execute the following:

   .. code-block:: console

      # cd /opt/openstack-ansible/playbooks
      # openstack-ansible openstack.osa.containers_lxc_create --limit localhost,lxc_hosts,<container name|container
        group>

      The lxc_hosts host group must be included as the playbook and roles executed require the
      use of facts from the hosts.
