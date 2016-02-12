Manual Changes
==============

Although the upgrade scripts and playbooks are fairly comprehensive, some
actions require manual intervention from the deployer. Some of these changes
require careful consideration of configuration variables or contents of a
database.

Updating user-configured SSL certificates for Horizon
-----------------------------------------------------

In Kilo, the variables for user-configured SSL certificates have changed. These
variables must be adjusted when upgrading from Juno to Kilo::

    Juno                        Kilo
    ----                        ----
    horizon_ssl_cert       ->   horizon_user_ssl_cert
    horizon_ssl_key        ->   horizon_user_ssl_key

User-provided CA certificates are now specified by
``horizon_user_ssl_ca_cert`` variable.

Removing nova spice console services
------------------------------------

Upgrading from Juno to Kilo using the upgrade scripts will automatically
remove the nova_spice_console containers, but the service entries will still
exist within the _services_ table in the _nova_ database.  These entries will
require manual removal.

Start by searching for services running the ``nova-consoleauth`` binary:

.. code-block:: sql

    SELECT Id, Binary, Host
    FROM nova.services
    WHERE Binary = 'nova-consoleauth';

If any of the service entries have ``nova_spice_console`` within the ``Host``
column, remove those entries carefully by their ``Id``:

.. code-block:: sql

    DELETE FROM nova.services
    WHERE Id = ###;
