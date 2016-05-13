Scripts
=======

This section describes scripts that are used in the upgrade process in detail.

Within the main :file:`scripts` directory there is a :file:`upgrade-utilities`
directory, which contains additional scripts that facilitate the initial
upgrade process.

run-upgrade.sh
--------------

This script controls the overall upgrade process for deployers choosing not to
do so manually.

It provides the following environment variables:

    * ``SCRIPTS_PATH`` - path to the top level scripts directory
    * ``MAIN_PATH`` - openstack_ansible root directory.
    * ``UPGRADE_PLAYBOOKS`` - path to the playbooks used in upgrading

The upgrade script will also bootstrap ansible (using
``bootstrap-ansible.sh``) in order to provide the new role dependencies
introduced in the Liberty series.

.. _migrate-os-vars:

migrate_openstack_vars.py
-------------------------

In Liberty, some variable names were changed to reflect upstream decisions.
This script will look for and replace any instances of these strings in the
variable override files matching the pattern
``/etc/openstack_deploy/user_*.yml``.
Comments in the file will be preserved, though the variable names within the
comments will be updated.

This script will also create files of the form
``/etc/openstack_deploy.MITAKA/VARS_MIGRATED_file``. For example, once the script has
processed the file ``/etc/openstack_deploy/user_variables.yml``. it creates
``/etc/openstack_deploy.MITAKA/VARS_MIGRATED_user_variables`` to indicate to
ansible that the step can be skipped on successive runs. The script itself does
not check for this file.

The variable changes are shown in the following table.

.. This table was made with the output of
   scripts/upgrade-utilities/scripts/make_rst_table.py. Insertion needs to be
   done manually since the OpenStack publish jobs do not use `make` and there
   isn't yet a sphinx extension that runs an abitrary script on build.

+------------------------------------------+------------------------------------------+
|                                Old Value |                                New Value |
+==========================================+==========================================+
+------------------------------------------+------------------------------------------+

Called by :ref:`config-change-playbook`

--------------

.. include:: navigation.txt
