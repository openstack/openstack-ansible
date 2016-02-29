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

--------------

.. include:: navigation.txt
