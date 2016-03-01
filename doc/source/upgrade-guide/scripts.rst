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

--------------

.. include:: navigation.txt
