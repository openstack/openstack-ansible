Process
=======

This document describes how to run the upgrade process using the
``run-upgrade.sh`` script and what the script is doing during execution.
The intention is to cover enough of the process so a deployer can
understand what is happening, when it is happening, and why it is happening.
This information will assist a deployer in recovering from upgrade script
failure and also enables the deployer to customize the upgrade path and
process.


About the script
----------------

The ``run-upgrade.sh`` script initiates the upgrade in a predetermined order.
If the script fails in any way, information will be printed to the screen
indicating how to continue the process.

Failed upgrades can sometimes require manual intervention. If this happens,
you might need to log in to a component of the environment to troubleshoot the
problem. However, if the original RPC Juno deployment is close to the
reference architecture, the script is expected to perform successfully.

Important Notes:
  * Before running the upgrade script, review your environment. Ensure you
  know which VMs you have online and how they were provisioned.

  * Shutdown any VM that was created using **boot from volume**.

  * To prevent data loss or corruption we recommend you halt any VMs using
  Block Storage. This is optional, since different block storage backends
  have different capabilities and some solutions may be more resilient than
  others. However, when using the cinder default LVM-backed storage, it is
  *HIGHLY* recommended you shut down block storage-attached VMs.

  * Before running the ``run-upgrade.sh`` script, schedule a maintenance
  window for the upgrade / migration process. While this is considered to be
  an online upgrade, the API will be interrupted while upgrading. Plan your
  maintenance window appropriately based on the size of your environment.

  * Neutron L3 networking will be interrupted while upgrading. During the
  upgrade, VMs that are connected to one another may not be able to
  communicate until all neutron agents services are restarted. While we have
  ensured potential downtime is minimal, container restart and subsequent
  service reloads will cause interruptions.


Running the upgrade script
--------------------------

The script will prompt you to accept the upgrade before it begins. To run the
script, execute the following command from the root directory where you cloned
the :file:`openstack-ansible` repository.

.. code-block:: bash

    ./scripts/run-upgrade.sh

The script will take some time to run, please be patient.


Running the upgrade by hand
---------------------------

While the recommended upgrade process is through use of the script,
it may be necessary to break up the process for environment stability,
scale, or other reasons. The following section describes the process for a
manual upgrade.

Getting started
^^^^^^^^^^^^^^^

Navigate to the playbooks directory located in the repository root. All steps
for the upgrade will be performed in this directory.

Creating two environment variables will simplify access to various upgrade
utilities.

.. code-block:: bash

    export UPGRADE_PLAYBOOKS="/opt/openstack-ansible/scripts/upgrade-utilities/playbooks"
    export UPGRADE_SCRIPTS="/opt/openstack-ansible/scripts/upgrade-utilities/scripts"

.. note::

   This is an optional step. If you prefer to call the files directly, use the
   path name instead of the variable, and the process will work normally.

.. note::

   While it's not required, running all of the following playbooks with the
   ``openstack-ansible`` command is recommended. Additionally during the upgrade
   it's recommended to pass the flag,
   ``-e 'pip_install_options=--force-reinstall'``. This flag will ensure all
   pip packages are reinstalled and running the expected versions upon
   the completion of the upgrade.


Executing the pre-work scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``create-new-openstack-deploy-structure.sh``. This script creates the new
directory structure required to use OpenStack-Ansible on your deployment host.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/create-new-openstack-deploy-structure.sh


----

Upgrade and install the latest required version of Ansible.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/bootstrap-new-ansible.sh


----

The following script searches for and separates all known RPC variables that
are used for RPC-specific product offerings. These options are mostly located
in :file:`user_variables.yml`

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/juno-rpc-extras-create.py


----

Populate user variables files with new defaults.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/new-variable-prep.sh


----

If you have been using keystone with LDAP enabled, run this script to
convert the variables to the new LDAP syntax.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/juno-kilo-ldap-conversion.py


----

If you have not already set the repository infrastructure components,
run this script to ensure it exists in your
:file:`openstack_user_config.yml` file.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/juno-kilo-add-repo-infra.py


----

If you have an updated environment using **is_metal** for components
outside of the normal defaults, this script is used to populate
the new environment with the changes you have made.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/juno-is-metal-preserve.py


----

Run the variable removal script to ensure old options are cleaned up.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/old-variable-remove.sh


----

Run the final upgrade script to clean up containers and components
which will no longer be needed.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/juno-container-cleanup.sh



Executing the playbooks
^^^^^^^^^^^^^^^^^^^^^^^

Before running any of the service playbooks make sure to generate all of the
required secret information.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/user-secrets-adjustments.yml

----


If you have **Haproxy** installed on your deployment, run the haproxy
playbook.

.. code-block:: bash

    openstack-ansible haproxy-install.yml


----

Run the container network adjustment playbook to ensure erroneous network
configuration files have been removed. Note that this command forces the
playbook to have a return value of 0 because there are containers that may
not exist at this time.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/container-network-adjustments.yml || true


----

Run the host adjustments playbook to ensure container configuration
files are running to the correct specification and that anything that may have
been deprecated or otherwise changed between the RPC Juno and the
OpenStack-Ansible Kilo releases is cleaned up.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/host-adjustments.yml


----

Run the Keystone adjustments playbook to correct permissions issues within
keystone containers.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/keystone-adjustments.yml


----

Run the horizon adjustments playbook to correct permissions issues within
horizon containers.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/horizon-adjustments.yml


----

Run the cinder adjustments playbook to correct a potential duplicate
container configuration entry in the cinder containers, which could impact
its ability to start from a stopped state.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/cinder-adjustments.yml


----

If you are upgrading from one of the later releases of Juno (10.1.11 or
later), run the logrotate removal playbook. The logrotate configuration
used in RPC Juno was completely redesigned in the OpenStack-Ansible Kilo
release. Note that this command forces the playbook to have a return value
of 0 because there are containers that may not exist at this time.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/remove-juno-log-rotate.yml || true


----

Run the basic host setup play to ensure you have the latest configurations.

.. code-block:: bash

    openstack-ansible setup-hosts.yml


----

Run the container network restart playbook to ensure all containers have
functional networking. This command is forced to return ``true``, as there
are new containers that might not exist yet.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/container-network-bounce.yml || true


----

Run the infrastructure setup play with options needed to upgrade rabbitmq and
galera.

.. code-block:: bash

    openstack-ansible setup-infrastructure.yml -e 'rabbitmq_upgrade=true' -e 'galera_ignore_cluster_state=true'


----

If you are running Swift as deployed from RPC Juno, run the swift ring adjustment
playbook to ensure rings are in the appropriate locations.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/swift-ring-adjustments.yml


----

If you are running Swift as deployed from RPC Juno, run the swift repo adjustment
playbook to ensure all swift hosts have access to the backports repository.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/swift-repo-adjustments.yml


----

Run the setup OpenStack playbook to deploy new service code.

.. code-block:: bash

    openstack-ansible setup-openstack.yml


----

Run the nova extra migrations playbook to ensure that the nova db has been
modernized. While this is an optional step it is recommended for future proofing
the environment.

.. code-block:: bash

    openstack-ansible ${UPGRADE_PLAYBOOKS}/nova-extra-migrations.yml


----

When the OpenStack setup plays have finished, run the post-upgrade cleanup
script to remove the original galera monitoring user. If you are still
using this user for monitoring your galera cluster, do **NOT** execute this
script. The old galera monitoring user was *haproxy*.

.. code-block:: bash

    ${UPGRADE_SCRIPTS}/post-upgrade-cleanup.sh


During the upgrade process a file
:file:`/etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml`
was created to help the upgrade along in situations where a load balancer or
access to an external device that my not be immediately available. Post upgrade
it's recommended to review this file and make sure any temporary changes are
moved from into more permanent variable files or that the cluster is updated to
support an environment without the. it should be noted that any variable listed
in this file will not impact the capabilities of the cluster and were only set
to a known value to ensure a successful upgrade. As a deployer would be
perfectly acceptable to keep the setting within the file permanently.


Migration and Upgrade Complete
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Review the environment and make sure everything is functional. If each script
and playbook executed successfully, the environment has upgraded to Kilo.
