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

To upgrade from Kilo to Liberty using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout <liberty-tag>
   # ./scripts/run-upgrade.sh


Configuration Changes
---------------------

The upgrade process will modify files residing in ``/etc/openstack_deploy`` in
order to reflect new Liberty values.

--------------

.. include:: navigation.txt
