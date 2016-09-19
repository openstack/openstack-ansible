.. _script-upgrade:

========================
Upgrading using a script
========================

The |current_release_formal_name| release series of OpenStack-Ansible contains
the code for migrating from |previous_release_formal_name| to
|current_release_formal_name|.

.. warning::

   The upgrade script is still under active development and should not be run
   on a production environment at this time.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade from |previous_release_formal_name| to
|current_release_formal_name| using the upgrade script,
perform the following steps in the ``openstack-ansible``
directoy:

.. parsed-literal::

   # git checkout stable/|current_release_branch_name|
   # LATEST_TAG=$(git describe --abbrev=0 --tags)
   # git checkout ${LATEST_TAG}
   # ./scripts/run-upgrade.sh

