Overview
========

The OpenStack-Ansible repository provides playbooks and scripts used
to upgrade an environment from Liberty to Mitaka. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks
can be run individually if necessary.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Mitaka release series of OpenStack-Ansible contain the code for
migrating from Liberty to Mitaka.

To upgrade from Liberty to Mitaka using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout stable/mitaka
   # LATEST_TAG=$(git describe --abbrev=0 --tags)
   # git checkout ${LATEST_TAG}
   # ./scripts/run-upgrade.sh

Upgrading manually
~~~~~~~~~~~~~~~~~~

Deployers can run the upgrade steps manually. See :ref:`manual-upgrade`.
Manual execution is useful for scoping the changes in the upgrade process
(For example, in very large deployments with strict SLA requirements), or for
inclusion into other orchestration for upgrade automation beyond what
OpenStack-Ansible provides.

Upgrade actions
~~~~~~~~~~~~~~~

Both the upgrade script and manual upgrade steps perform the actions and
use the concepts introduced below.

Configuration changes
---------------------

The upgrade process modifies files residing in ``/etc/openstack_deploy`` in
order to reflect new Mitaka values.

Flag files
----------

Some flag files are created by the migration scripts in order to achieve
idempotency. These files are placed in the ``/etc/openstack_deploy.LIBERTY``
directory.

RabbitMQ upgrade
----------------

Upgrade the RabbitMQ server during an OpenStack-Ansible upgrade.

See :ref:`setup-infra-playbook` for details.

--------------

.. include:: navigation.txt
