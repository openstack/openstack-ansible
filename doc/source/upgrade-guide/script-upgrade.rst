.. _script-upgrade:

========================
Upgrading using a script
========================

The Newton release series of OpenStack-Ansible contains the code for
migrating from Mitaka to Newton.

.. warning::

   The upgrade script is still under active development and should not be run
   on a production environment at this time.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade from Mitaka to Newton using the upgrade script, perform the
following steps in the ``openstack-ansible`` directory:

.. code-block:: console

   # git checkout stable/newton
   # LATEST_TAG=$(git describe --abbrev=0 --tags)
   # git checkout ${LATEST_TAG}
   # ./scripts/run-upgrade.sh

--------------

.. include:: navigation.txt
