=====================
Minor version upgrade
=====================

Upgrades between minor versions of OpenStack-Ansible require
updating the repository clone to the latest minor release tag, updating
the Ansible roles, and then running playbooks against the target hosts.
This section provides instructions for those tasks.

Prerequisites
~~~~~~~~~~~~~

To avoid issues and simplify troubleshooting during the upgrade, disable the
security hardening role by setting the ``apply_security_hardening`` variable
to ``False`` in the :file:`user_variables.yml` file, and
backup your OpenStack-Ansible installation.

Execute a minor version upgrade
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A minor upgrade typically requires the following steps:

#. Change directory to the cloned repository's root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Ensure that your OpenStack-Ansible code is on the latest
   |current_release_formal_name| tagged release:

   .. parsed-literal::

      # git checkout |latest_tag|

#. Update all the dependent roles to the latest version:

   .. code-block:: console

      # ./scripts/bootstrap-ansible.sh

#. Change to the playbooks directory:

   .. code-block:: console

      # cd playbooks

#. Update the hosts:

   .. code-block:: console

      # openstack-ansible openstack.osa.setup_hosts -e package_state=latest

#. Update the infrastructure:

   .. code-block:: console

      # openstack-ansible -e rabbitmq_upgrade=true \
      openstack.osa.setup_infrastructure

#. Update all OpenStack services:

   .. code-block:: console

      # openstack-ansible openstack.osa.setup_openstack -e package_state=latest

.. note::

   You can limit upgrades to specific OpenStack components. See the following
   section for details.

Upgrade specific components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can limit upgrades to specific OpenStack components by running each of the
component playbooks against groups.

For example, you can update only the Compute hosts by running the following
command:

.. code-block:: console

   # openstack-ansible openstack.osa.nova --limit nova_compute

To update only a single Compute host, run the following command:

.. code-block:: console

   # openstack-ansible openstack.osa.nova --limit <node-name>

.. note::

   Skipping the ``nova-key`` tag is necessary so that the keys on
   all Compute hosts are not gathered.

To see which hosts belong to which groups, use the ``openstack-ansible-inventory-manage``
script to show all groups and their hosts. For example:

#. Change directory to the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Show all groups and which hosts belong to them:

   .. code-block:: console

      # openstack-ansible-inventory-manage -G

#. Show all hosts and the groups to which they belong:

   .. code-block:: console

      # openstack-ansible-inventory-manage -g

To see which hosts a playbook runs against, and to see which tasks are
performed, run the following commands (for example):


#. See the hosts in the ``nova_compute`` group that a playbook runs against:

   .. code-block:: console

      # openstack-ansible openstack.osa.nova --limit nova_compute \
                                              --list-hosts

#. See the tasks that are executed on hosts in the ``nova_compute`` group:

   .. code-block:: console

     # openstack-ansible openstack.osa.nova --limit nova_compute \
                                             --skip-tags 'nova-key' \
                                             --list-tasks

Upgrading a specific component within the same OpenStack-Ansible version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you may need to apply the latest security patches or bug
fixes for a service while remaining on the same stable branch. This can
be done by overriding the Git installation branch for that service, which
instructs OpenStack-Ansible to pull the most recent code from the branch
you are already tracking.
But using branches directly as ``<service>_git_install_branch`` is
highly discouraged. Every time the playbook is re-run, the service may
be upgraded to a newer commit, which can lead to inconsistent
versions between hosts (for example, when adding a new compute node
later).

So the recommended practice is to take the HEAD commit SHA of the
desired stable branch and set it explicitly. To find the latest SHA of the
``stable/2025.1`` branch, you can run (e.g. for Nova):

.. code-block:: bash

   git ls-remote https://opendev.org/openstack/nova refs/heads/stable/2025.1

And use that SHA in your configuration to ensure consistent versions across
all hosts in your ``user_variables.yml``:

.. code-block:: yaml

   nova_git_install_branch: {{SHA}}

And run:

.. code-block:: bash

   openstack-ansible openstack.osa.nova --tags nova-install

The playbook will fetch and install the code from the specified branch or
commit SHA, applying the latest patches and fixes as defined. Using a
pinned SHA ensures consistent versions across all hosts, while following
the branch directly will always pull its current HEAD.

We can verify the version of the service before and after the upgrade
(don't forget to load required environment variables):

.. code-block:: bash

   $ ansible -m shell -a '/openstack/venvs/nova-{{ openstack_release }}/bin/pip3 freeze | grep nova' nova_all
   infra1-nova-api-container-e5dbbe38 | CHANGED | rc=0 >>
   nova==31.0.1.dev12
   infra2-nova-api-container-0c5d0203 | CHANGED | rc=0 >>
   nova==31.0.1.dev12
   infra3-nova-api-container-d791a43e | CHANGED | rc=0 >>
   nova==31.0.1.dev12
   compute | CHANGED | rc=0 >>
   nova==31.0.1.dev12

After the upgrade to the latest patches in the same branch:

.. code-block:: bash

   $ ansible -m shell -a '/openstack/venvs/nova-{{ openstack_release }}/bin/pip3 freeze | grep nova' nova_all
   infra1-nova-api-container-e5dbbe38 | CHANGED | rc=0 >>
   nova==31.1.1.dev9
   infra2-nova-api-container-0c5d0203 | CHANGED | rc=0 >>
   nova==31.1.1.dev9
   infra3-nova-api-container-d791a43e | CHANGED | rc=0 >>
   nova==31.1.1.dev9
   compute | CHANGED | rc=0 >>
   nova==31.1.1.dev9

.. note::

   This approach is not limited to Nova. You can apply the same method
   to any other OpenStack service managed by OpenStack-Ansible by
   overriding its corresponding ``<service>_git_install_branch``
   variable.

Always ensure that the branch is up-to-date and compatible with the rest
of your deployment before proceeding.
