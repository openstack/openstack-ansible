Overview
========

The OpenStack-Ansible repository provides playbooks and scripts used
to upgrade an environment from Kilo to Liberty. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks
can be run individually if necessary.

Running the Upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Liberty series releases of OpenStack-Ansible contain the code for
migrating from Kilo to Liberty.

.. note::

  The upgrade script is still under active development and should not be run at
  this time.

To upgrade from Kilo to Liberty using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout <liberty-tag>
   # ./scripts/run-upgrade.sh


Configuration Changes
---------------------

The upgrade process will modify files residing in ``/etc/openstack_deploy`` in
order to reflect new Liberty values.

Flag Files
----------

Some flag files are created by the migration scripts in order to achieve
idempotency. These files are placed in the ``/etc/openstack_deploy.KILO``
directory

MariaDB Upgrade
---------------

The version of MariaDB is upgraded from the 5.5 series to 10.0 in Liberty.
These changes are facilitated directly by the MariaDB/Galera roles themselves.

See :ref:`setup-infra-playbook'` for details.

RabbitMQ Upgrade
----------------

The RabbitMQ server can be upgraded during an OpenStack-Ansible upgrade. For
Liberty, upgrading RabbitMQ is optional.

See :ref:`setup-infra-playbook'` for details.

--------------

.. include:: navigation.txt
