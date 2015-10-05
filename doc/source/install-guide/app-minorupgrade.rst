`Home <index.html>`__ OpenStack Ansible Installation Guide

Appendix C. Minor Upgrades
--------------------------

Upgrades between minor versions of OpenStack-Ansible are handled by simply
updating the repository clone to the latest tag, then executing playbooks
against the target hosts.

Due to changes in python package dependencies by OpenStack (even in stable
branches) it is likely that some python packages may have to be downgraded in
a production environment.

In order to facilitate this extra options may be passed to the python package
installer to reinstall based on whatever version of the package is available
in the repository. This is done by executing, for example:

.. code-block:: bash

    openstack-ansible -e pip_install_options="--force-reinstall" \
        setup-openstack.yml

A minor upgrade will typically require the execution of the following:

.. code-block:: bash

    # Change directory into the repository clone root directory
    cd /opt/openstack-ansible

    # Update the git remotes
    git fetch --all

    # Checkout the latest tag (the below tag is an example)
    git checkout 12.0.1

    # Change into the playbooks directory
    cd playbooks

    # Build the updated repository
    openstack-ansible repo-install.yml

    # Update RabbitMQ
    openstack-ansible -e rabbitmq_upgrade=true \
        rabbitmq-install.yml

    # Update the Utility Container
    openstack-ansible -e pip_install_options="--force-reinstall" \
        utility-install.yml

    # Update all OpenStack Services
    openstack-ansible -e pip_install_options="--force-reinstall" \
        setup-openstack.yml

Note that if you wish to scope the upgrades to specific OpenStack components
then each of the component playbooks may be executed and scoped using groups.
For example:

.. code-block:: bash

    # Update only the Compute Hosts
    openstack-ansible -e pip_install_options="--force-reinstall" \
        os-nova-install.yml --limit nova_compute

    # Update only a single Compute Host
    #  Skipping the 'nova-key' tag is necessary as the keys on all compute
    #  hosts will not be gathered.
    openstack-ansible -e pip_install_options="--force-reinstall" \
        os-nova-install.yml --limit <node-name> --skip-tags 'nova-key'

If you wish to see which hosts belong to which groups, the
``inventory-manage.py`` script will show all groups and their hosts.
For example:

.. code-block:: bash

    # Change directory into the repository clone root directory
    cd /opt/openstack-ansible

    # Show all groups and which hosts belong to them
    ./scripts/inventory-manage.py -G

    # Show all hosts and which groups they belong to
    ./scripts/inventory-manage.py -g

You may also see which hosts a playbook will execute against, and which tasks
will be executed:

.. code-block:: bash

    # Change directory into the repository clone playbooks directory
    cd /opt/openstack-ansible/playbooks

    # See the hosts in the nova_compute group which a playbook will execute
    #  against
    openstack-ansible os-nova-install.yml --limit nova_compute --list-hosts

    # See the tasks which will be executed on hosts in the nova_compute group
    openstack-ansible os-nova-install.yml --limit nova_compute \
                                          --skip-tags 'nova-key' \
                                          --list-tasks

--------------

.. include:: navigation.txt
