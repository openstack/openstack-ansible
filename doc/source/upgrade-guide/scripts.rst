Scripts
=======

This section describes scripts that are used in the upgrade process in detail.

Within the main :file:`scripts` directory there is a :file:`upgrade-utilities`
directory, which contains additional scripts that facilitate the initial
upgrade process.


bootstrap-new-ansible.sh
------------------------

This bash script ensures that the correct version of Ansible is installed.
In the process of installing Ansible, the script will check for, backup, and
remove any :file:`pip.conf` files found within the home folder of
the user running the upgrade. Typically this is ``root``.


create-new-openstack-deploy-structure.sh
----------------------------------------

This bash script creates the new directory structure. The script backs up
the original :file:`rpc_deploy` configuration files, inventory, then migrates
these items to :file:`openstack_deploy`. When the script is executed,
the original :file:`rpc_deploy` directory will be archived as
:file:`pre-upgrade-backup.tgz`, which is stored in the executing user's home
folder. Later, the directory will be moved to :file:`/etc/rpc_deploy.OLD`,
where a :file:``DEPRECATED.txt` text file will be created to indicate that
the old directory is no longer in service. The original :file:`/etc/rpc_deploy.OLD`
directory remains on disk to ensure that you have something to refer back
to if there are any failures or errors during the upgrade.


juno-container-cleanup.sh
-------------------------

This bash script cleans up any containers that are not needed from hosts
and inventory. It also cleans up haproxy installations and configurations,
and pip configurations throughout all running containers and hosts.


juno-is-metal-preserve.py
-------------------------

This python script looks through the existing :file:`environment.yml` file and
collects any container with **is_metal* set to true. The script updates the current
:file:`environment.yml` files with the appropriate settings to ensure the value is
carried over for the upgrade. If anything is found, the script updates the current
:file:`environment.yml` files with the appropriate settings. This ensures that
the value is carried over for the upgrade.


juno-kilo-add-repo-infra.py
---------------------------

This python script looks through the existing :file:`openstack_user_variables.yml`
file and ensures that the repository infrastructure has been assigned to a host. If the
script is unable to determine the location of the repository infrastructure, the script
will use the existing infrastructure nodes as targets for the new repository server
deployment. If it needs to create entries for the repository infrastructure it
will do so within the :file:`/etc/openstack_deploy/conf.d directory` using the file
:file:`repo-servers.yml`.


juno-kilo-ldap-conversion.py
----------------------------

This python script looks through all available user variable files and attempts
to identify settings that are used for ``keystone_ldap_.*``. If the variables
are found the script will write the new dictionary and generator syntax into the
:file:`/etc/openstack_deploy/user_secrets.yml` file.

.. note::
   The LDAP variables are written into :file:`user_secrets.yml` from
   :file:`user_variables.yml` as a means of protecting the LDAP configuration.
   This change enables the deployer to encrypt the :file`user_secrets.yml`
   with the **ansible-vault** command.


juno-rpc-extras-create.py
-------------------------

This python script looks for and moves Rackspace-specific configuration options
from the generic :file:`user_variables.yml` file and into the
:file:`/etc/openstack_deploy/user_extras_variables.yml` file. This separates
the values set for RPC from those set for OpenStack Ansible. These variables are
important to what can be implemented using the rpc-openstack software repository
found here: https://github.com/rcbops/rpc-openstack


new-variable-prep.sh
--------------------

This bash script adds variables that may be missing when upgrading from Juno to
Kilo, appending variables to the system as needed. There are several new secret
items that have been added to the configuration files, and randomly generated
passwords will be created for these items upon execution of the script.

.. note::
   This script creates the variable file
   :file:`/etc/openstack_deploy/user_deleteme_post_upgrade_variables.yml`,
   which contains optional variables to allow an upgrade to complete without
   having to go through change management on external devices to which you may
   not have immediate access. When the upgrade is complete, review options
   within the file and make any adjustments as needed. When ready, remove this
   file and reconfigure any components that may have been impacted by the
   previous settings.


old-variable-remove.sh
----------------------

This bash script removes variables from the user variable files that may be
duplicates, changed, or are otherwise no longer needed.


post-upgrade-cleanup.sh
-----------------------

This bash script cleans up any remaining items that may need to be removed
upon completion of the upgrade.
