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

.. _ceilo-env-script:

fix_ceilometer_env.py
---------------------

The alarming functionality for ceilometer has been removed from ceilometer
itself and moved into aodh in Liberty. To compensate, the relevant
OpenStack-Ansible environment memberships have been updated. See `this mailing
list post
<http://lists.openstack.org/pipermail/openstack-dev/2015-September/073897.html>`_
for details.

This file will remove the ``ceilometer_alarm_notifier`` and
``ceilometer_alarm_evaluator`` entries from the
``/etc/openstack_deploy/env.d/ceilometer.yml`` file. In order to preserve any
user changes made to the file, only these specific values are removed.

This script will also create
``/etc/openstack_deploy.KILO/CEILOMETER_MIGRATED`` to indicate to ansible that
the step can be skipped on successive runs. The script itself does not check
for this file.

Called by :ref:`config-change-playbook`

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
``/etc/openstack_deploy.KILO/VARS_MIGRATED_file`` e.g. once the script has
processed the file ``/etc/openstack_deploy/user_variables.yml`` it creates
``/etc/openstack_deploy.KILO/VARS_MIGRATED_user_variables`` to indicate to
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
|                        galera_sst_method |                  galera_wsrep_sst_method |
+------------------------------------------+------------------------------------------+
|         heat_service_project_domain_name |           heat_service_project_domain_id |
+------------------------------------------+------------------------------------------+
|            heat_service_user_domain_name |              heat_service_user_domain_id |
+------------------------------------------+------------------------------------------+
|                nova_v21_service_adminuri |                    nova_service_adminuri |
+------------------------------------------+------------------------------------------+
|          nova_v21_service_adminuri_proto |              nova_service_adminuri_proto |
+------------------------------------------+------------------------------------------+
|                nova_v21_service_adminurl |                    nova_service_adminurl |
+------------------------------------------+------------------------------------------+
|             nova_v21_service_description |                 nova_service_description |
+------------------------------------------+------------------------------------------+
|             nova_v21_service_internaluri |                 nova_service_internaluri |
+------------------------------------------+------------------------------------------+
|       nova_v21_service_internaluri_proto |           nova_service_internaluri_proto |
+------------------------------------------+------------------------------------------+
|             nova_v21_service_internalurl |                 nova_service_internalurl |
+------------------------------------------+------------------------------------------+
|                    nova_v21_service_name |                        nova_service_name |
+------------------------------------------+------------------------------------------+
|                    nova_v21_service_port |                        nova_service_port |
+------------------------------------------+------------------------------------------+
|                   nova_v21_service_proto |                       nova_service_proto |
+------------------------------------------+------------------------------------------+
|               nova_v21_service_publicuri |                   nova_service_publicuri |
+------------------------------------------+------------------------------------------+
|         nova_v21_service_publicuri_proto |             nova_service_publicuri_proto |
+------------------------------------------+------------------------------------------+
|               nova_v21_service_publicurl |                   nova_service_publicurl |
+------------------------------------------+------------------------------------------+
|                    nova_v21_service_type |                        nova_service_type |
+------------------------------------------+------------------------------------------+

Called by :ref:`config-change-playbook`

--------------

.. include:: navigation.txt
