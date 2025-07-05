Configure your first networks
=============================

A newly deployed OpenStack-Ansible has no networks by default. If you need to
add networks, you can use the OpenStack CLI, or you can use the Ansible modules
for it.

An example on how to provision networks is in the `OpenStack-Ansible plugins <https://opendev.org/openstack/openstack-ansible-plugins>`_
repository, where you can use the openstack_resources role:

#. Define the variable openstack_resources_network according to the structure
   in the role `defaults <https://opendev.org/openstack/openstack-ansible-plugins/src/branch/master/roles/openstack_resources/defaults/main.yml#L100-L143>`

#. Run the playbook openstack.osa.openstack_resources with the tag network-resources:

   .. code-block:: shell-session

      openstack-ansible openstack.osa.openstack_resources --tags network-resources
