========
Overview
========

An OpenStack-Ansible environment can upgrade to a minor or a major version.

.. note::

   You can only upgrade between sequential releases.

Upgrades between minor versions of OpenStack-Ansible require
updating the repository clone to the latest minor release tag, and then
running playbooks against the target hosts. For more information, see
:ref:`upgrading-to-a-minor-version`.

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
- Upgrades the RabbitMQ server. See :ref:`setup-infra-playbook` for details.

For more information about the major upgrade process, see
:ref:`upgrading-by-using-a-script` and :ref:`upgrading-manually`.
