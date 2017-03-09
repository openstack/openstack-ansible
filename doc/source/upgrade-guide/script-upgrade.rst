.. _upgrading-by-using-a-script:

===========================
Upgrading by using a script
===========================

The |current_release_formal_name| release series of OpenStack-Ansible contains
the code for migrating from |previous_release_formal_name| to
|current_release_formal_name|.

.. warning::

   The upgrade script is still under active development. Do *not* run it
   on a production environment at this time.

Running the upgrade script
~~~~~~~~~~~~~~~~~~~~~~~~~~

To upgrade from |previous_release_formal_name| to |current_release_formal_name|
by using the upgrade script, perform the following steps in the
``openstack-ansible`` directory:

#. Change directory to the repository clone root directory:

   .. code-block:: console

      # cd /opt/openstack-ansible

#. Run the following commands:

   .. parsed-literal::

      # git checkout |latest_tag|
      # ./scripts/run-upgrade.sh

