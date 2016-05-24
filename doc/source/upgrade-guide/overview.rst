Overview
========

The OpenStack-Ansible repository provides playbooks and scripts used
to upgrade an environment from Mitaka to Newton. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks
can be run individually if necessary.

Running the Upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Newton series releases of OpenStack-Ansible contain the code for
migrating from Mitaka to Newton.

.. warning::

   The upgrade script is still under active development and should not be run at this time.

To upgrade from Mitaka to Newton using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout stable/newton
   # LATEST_TAG=$(git describe --abbrev=0 --tags)
   # git checkout ${LATEST_TAG}
   # ./scripts/run-upgrade.sh

Upgrading Manually
~~~~~~~~~~~~~~~~~~

Deployers can run the upgrade steps manually. See :ref:`manual-upgrade`.
Manual execution is useful for scoping the changes in the upgrade process
(For example, in very large deployments with strict SLA requirements), or for
inclusion into other orchestration for upgrade automation beyond what
OpenStack-Ansible provides.

Upgrade Actions
~~~~~~~~~~~~~~~

Both the upgrade script and manual upgrade steps perform the actions and
use the concepts introduced below.

Configuration Changes
---------------------

The upgrade process will modify files residing in ``/etc/openstack_deploy`` in
order to reflect new Newton values.

Flag Files
----------

Some flag files are created by the migration scripts in order to achieve
idempotency. These files are placed in the ``/etc/openstack_deploy.NEWTON``
directory.

RabbitMQ Upgrade
----------------

The RabbitMQ server can be upgraded during an OpenStack-Ansible upgrade.

See :ref:`setup-infra-playbook` for details.

--------------

.. include:: navigation.txt
