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

.. _neutron-env-script:

add_new_neutron_env.py
----------------------

This script will take any new items within the
``etc/openstack_deploy/env.d/neutron.yml`` file and add them to the deployed
``/etc/openstack_deploy/env.d/neutron.yml`` file. The key for LBaaS agents were
added in Liberty

This script will also create ``/etc/openstack_deploy.KILO/NEUTRON_MIGRATED``
to indicate to ansible that the step can be skipped on successive runs. The
script itself does not check for this file.

Called by :ref:`config-change-playbook`

--------------

.. include:: navigation.txt
