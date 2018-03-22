==============
Major upgrades
==============

This guide provides information about the upgrade process from
|previous_release_formal_name| to |current_release_formal_name|
for OpenStack-Ansible.

.. note::

   You can only upgrade between sequential releases.


Introduction
============

For upgrades between major versions, the OpenStack-Ansible repository provides
playbooks and scripts to upgrade an environment. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks can be run
individually if necessary. Alternatively, a deployer can upgrade manually. A
major upgrade process performs the following actions:

- Modifies files residing in the ``/etc/openstack_deploy`` directory, to
  reflect new configuration values.
- Places flag files that are created by the migration scripts in order to
  achieve idempotency. These files are placed in the |upgrade_backup_dir|
  directory.
- Upgrades the infrastructure servers.
  See :ref:`setup-infra-playbook` for details.

For more information about the major upgrade process, see
:ref:`upgrading-by-using-a-script` and :ref:`upgrading-manually`.

.. include:: major-upgrades-with-script.rst
.. include:: major-upgrades-manual-upgrade.rst
