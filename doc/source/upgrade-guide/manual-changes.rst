Manual Changes
==============

Although the upgrade scripts and playbooks are fairly comprehensive, some
actions require manual intervention from the deployer. Some of these changes
require careful consideration of configuration variables or contents of a
database.

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
