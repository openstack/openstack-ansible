=======
Scripts
=======

This section describes in detail the scripts that are used in the upgrade
process.

Within the main :file:`scripts` directory there is an :file:`upgrade-utilities`
directory, which contains additional scripts that facilitate the initial
upgrade process.

run-upgrade.sh
~~~~~~~~~~~~~~

The ``run-upgrade.sh`` script controls the overall upgrade process for
deployers who do not want to upgrade manually. It provides the following
environment variables:

* ``SCRIPTS_PATH`` - The path to the top level scripts directory
* ``MAIN_PATH`` - The ``openstack_ansible`` root directory.
* ``UPGRADE_PLAYBOOKS`` - The path to the playbooks used in upgrading

The upgrade script also bootstraps OpenStack-Ansible (using
``bootstrap-ansible.sh``) in order to provide the new role dependencies
introduced in the |previous_release_formal_name| series.

.. _migrate-os-vars:

migrate_openstack_vars.py
~~~~~~~~~~~~~~~~~~~~~~~~~

Upstream decisions influenced the change of some variable names in
|current_release_formal_name|. This script replaces any instances of these
strings in the variable override files matching the pattern
``/etc/openstack_deploy/user_*.yml``.
Variable names within comments are updated.

This script creates files in the form ``VARS_MIGRATED_<filename>`` and
places them in |upgrade_backup_dir| directory.
For example, after the script processes the
``/etc/openstack_deploy/user_variables.yml`` file, it creates the
``VARS_MIGRATED_user_variables.yml`` file in the |upgrade_backup_dir|
directory. This indicates to OpenStack-Ansible to skip this step on successive
runs. The script itself does not check for this file.

This script is called by the :ref:`config-change-playbook`.
