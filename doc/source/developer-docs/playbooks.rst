=========
Playbooks
=========

The OpenStack-Ansible playbooks are stored in the playbooks directory.

There are several top-level playbooks that are run to prepare the host machines
before actually deploying OpenStack and associated containers.

Running Playbooks
-----------------

There is an `openstack-ansible` command installed by the
`scripts/bootstrap-ansible.sh` script. This wraps the `ansible-playbook`
command and provides the `/etc/openstack_deploy/user_*.yml` variable files
to the playbooks.

All of the playbooks should be run within the `openstack-ansible/playbooks`
directory

Setting up the Hosts
--------------------

Run `openstack-ansible setup-hosts.yml` to set up the physical hosts for
containers.

Setting up Infrastructure
-------------------------

Infrastructure pertains to utility services such as RabbitMQ, memcached,
Galera, and logging which are not actually OpenStack services, but that
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

After successful deployment, you are able to update variables in
``/etc/openstack_deploy/user_variables.yml``.

* Object Storage (swift)

   - The ``pretend_min_part_hours_passed`` option can now be
     passed to swift-ring-builder prior to performing a rebalance. This is set
     by the ``swift_pretend_min_part_hours_passed`` boolean variable.
     The default for this variable is False. However, we recommend using
     ``-e swift_pretend_min_part_hours_passed=True`` when running the
     ``os-swift.yml`` playbook to avoid resetting ``min_part_hours``
     unintentionally.

     .. important::

        If you run this command and deploy rebalanced rings before a replication
        pass completes, you may introduce unavailability in your cluster.

        This should only be used for testing or fully rebalanced clusters.
