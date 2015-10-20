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

.. code-block:: shell-session

    # openstack-ansible -e pip_install_options="--force-reinstall" \
        setup-openstack.yml

A minor upgrade will typically require the execution of the following:

1. Change directory into the repository clone root directory::

  .. code-block:: shell-session

      # cd /opt/openstack-ansible

2. Update the git remotes

  .. code-block:: shell-session

      # git fetch --all

3. Checkout the latest tag (the below tag is an example)

  .. code-block:: shell-session

      # git checkout 12.0.1

4. Change into the playbooks directory

  .. code-block:: shell-session

      # cd playbooks

5. Build the updated repository

  .. code-block:: shell-session

      # openstack-ansible repo-install.yml

6. Update RabbitMQ

  .. code-block:: shell-session

      # openstack-ansible -e rabbitmq_upgrade=true \
          rabbitmq-install.yml

7. Update the Utility Container

  .. code-block:: shell-session

      # openstack-ansible -e pip_install_options="--force-reinstall" \
          utility-install.yml

8. Update all OpenStack Services

  .. code-block:: shell-session

      # openstack-ansible -e pip_install_options="--force-reinstall" \
          setup-openstack.yml

Note that if you wish to scope the upgrades to specific OpenStack components
then each of the component playbooks may be executed and scoped using groups.
For example:

1. Update only the Compute Hosts

  .. code-block:: shell-session

      # openstack-ansible -e pip_install_options="--force-reinstall" \
          os-nova-install.yml --limit nova_compute

2. Update only a single Compute Host (skipping the 'nova-key' tag is necessary as the keys on all compute hosts will not be gathered)

  .. code-block:: shell-session

      # openstack-ansible -e pip_install_options="--force-reinstall" \
          os-nova-install.yml --limit <node-name> --skip-tags 'nova-key'

If you wish to see which hosts belong to which groups, the
``inventory-manage.py`` script will show all groups and their hosts.
For example:

1. Change directory into the repository clone root directory

  .. code-block:: shell-session

      # cd /opt/openstack-ansible

2. Show all groups and which hosts belong to them

  .. code-block:: shell-session

      # ./scripts/inventory-manage.py -G

3. Show all hosts and which groups they belong to

  .. code-block:: shell-session

      # ./scripts/inventory-manage.py -g

You may also see which hosts a playbook will execute against, and which tasks
will be executed:

1. Change directory into the repository clone playbooks directory

  .. code-block:: shell-session

      # cd /opt/openstack-ansible/playbooks

2. See the hosts in the nova_compute group which a playbook will execute against

  .. code-block:: shell-session

      # openstack-ansible os-nova-install.yml --limit nova_compute \
                                              --list-hosts

3. See the tasks which will be executed on hosts in the nova_compute group

  .. code-block:: shell-session

     # openstack-ansible os-nova-install.yml --limit nova_compute \
                                             --skip-tags 'nova-key' \
                                             --list-tasks

--------------

.. include:: navigation.txt
