========
Overview
========

An OpenStack-Ansible environment can be upgraded between minor versions,
and between major versions.

Upgrades between minor versions of OpenStack-Ansible require
updating the repository clone to the latest minor release tag, then
running playbooks against the target hosts. For more information, see
:ref:`minor-upgrades`.

For major upgrades, the OpenStack-Ansible repository provides playbooks and
scripts used to upgrade an environment. The ``run-upgrade.sh`` script runs
each upgrade playbook in the correct order, or playbooks can be run
individually if necessary. Alternatively, a deployer can upgrade manually. A
major upgrade process performs the following actions:

- Modifies files residing in ``/etc/openstack_deploy`` in
  order to reflect new configuration values.
- Some flag files are created by the migration scripts in order to achieve
  idempotency. These files are placed in the ``/etc/openstack_deploy.NEWTON``
  directory.
- Upgrade the RabbitMQ server during an OpenStack-Ansible upgrade process.
  See :ref:`setup-infra-playbook` for details.

For more information on the major upgrade process, see :ref:`script-upgrade`
and :ref:`manual-upgrade`.

.. note::
   You can only upgrade between sequential releases.

