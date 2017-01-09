==========================
Galera cluster maintenance
==========================

.. toctree::

   ops-galera-remove.rst
   ops-galera-start.rst
   ops-galera-recovery.rst

Routine maintenance includes gracefully adding or removing nodes from
the cluster without impacting operation and also starting a cluster
after gracefully shutting down all nodes.

MySQL instances are restarted when creating a cluster, when adding a
node, when the service is not running, or when changes are made to the
``/etc/mysql/my.cnf`` configuration file.
