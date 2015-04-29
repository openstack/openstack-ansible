os-ansible-deployment Playbooks
===============================

The OpenStack Ansible playbooks are stored in the playbooks directory.

There are several top-level playbooks that are run to prepare the host machines
before actually deploying OpenStack and associated containers.

Running Playbooks
-----------------

There is an `openstack-ansible` command installed by the
`scripts/bootstrap-ansible.sh` script. This wraps the `ansible-playbook`
command and provides the `/etc/openstack_deploy/user_*.yml` variable files
to the playbooks.

All of the playbooks should be run within the `os-ansible-deployment/playbooks`
directory

Setting up the Hosts
--------------------

Run `openstack-ansible setup-hosts.yml` to set up the physical hosts for
containers.

Setting up Infrastructure
-------------------------

Infrastructure pertains to utility services such as RabbitMQ, memcached,
galera, and logging which are not actually OpenStack services, but that
OpenStack relies on.

Run `openstack-ansible setup-infrastructure.yml` to install these containers.

Setting up OpenStack
--------------------

Running `openstack-ansible setup-openstack.yml` will install the following
OpenStack services:

    * Keystone
    * Swift
    * Glance
    * Cinder
    * Nova
    * Neutron
    * Heat
    * Horizon
