Overview
========

The OpenStack-Ansible repository provides playbooks and scripts used
to upgrade an environment from Kilo to Liberty. The ``run-upgrade.sh``
script runs each upgrade playbook in the correct order, or playbooks
can be run individually if necessary.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Liberty release series of OpenStack-Ansible contain the code for
migrating from Kilo to Liberty.

To upgrade from Kilo to Liberty using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout <liberty-tag>
   # ./scripts/run-upgrade.sh

Upgrading manually
~~~~~~~~~~~~~~~~~~

Deployers can run the upgrade steps manually. See :ref:`manual-upgrade`.

Upgrade actions
~~~~~~~~~~~~~~~

Both the upgrade script and manual upgrade steps perform the actions and
use the concepts introduced below.

Configuration changes
---------------------

The upgrade process modifies files residing in ``/etc/openstack_deploy`` in
order to reflect new Liberty values.

Flag files
----------

Some flag files are created by the migration scripts in order to achieve
idempotency. These files are placed in the ``/etc/openstack_deploy.KILO``
directory.

MariaDB upgrade
---------------

MariaDB and Galera directly facilitate the Liberty upgrade of MariaDB from the 5.5
series to the 10.0.

See :ref:`setup-infra-playbook` for details.

RabbitMQ upgrade
----------------

Upgrade the RabbitMQ server during an OpenStack-Ansible upgrade. When
upgrading from an early Kilo release, the update is mandatory.

See :ref:`setup-infra-playbook` for details.

Neutron port security
---------------------

OpenStack-Ansible enables neutron ML2 port security driver by default in
Liberty, but keeps the driver disabled in environments upgraded from Kilo
unless you have enabled it in Kilo.


See :ref:`neutron-port-sec-playbook` for details.


.. include:: navigation.txt
