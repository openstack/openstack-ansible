=======
Scripts
=======

This section describes scripts that are used in the upgrade process in detail.

Within the main :file:`scripts` directory there is a :file:`upgrade-utilities`
directory, which contains additional scripts that facilitate the initial
upgrade process.

``run-upgrade.sh``
~~~~~~~~~~~~~~~~~~

This script controls the overall upgrade process for deployers choosing not to
do so manually.

It provides the following environment variables:

    * ``SCRIPTS_PATH`` - path to the top level scripts directory
    * ``MAIN_PATH`` - openstack_ansible root directory.
    * ``UPGRADE_PLAYBOOKS`` - path to the playbooks used in upgrading

The upgrade script also bootstraps OpenStack-Ansible (using
``bootstrap-ansible.sh``) in order to provide the new role dependencies
introduced in the |previous_release_formal_name| series.

.. _migrate-os-vars:

``migrate_openstack_vars.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Upstream decisions influenced the change of some variable names in
|current_release_formal_name|. This script replaces any instances of these
strings in the variable override files matching the pattern
``/etc/openstack_deploy/user_*.yml``.
Variable names within comments are updated.

This script creates files of the form ``VARS_MIGRATED_<filename>`` and
places them in |upgrade_backup_dir|.
For example, once the script has processed the file
``/etc/openstack_deploy/user_variables.yml``, it creates
``VARS_MIGRATED_user_variables.yml`` in |upgrade_backup_dir|.
This indicates to OpenStack-Ansible to skip this step on successive runs. The
script itself does not check for this file.

Called by :ref:`config-change-playbook`
