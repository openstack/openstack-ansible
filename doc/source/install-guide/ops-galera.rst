`Home <index.html>`_ OpenStack-Ansible Installation Guide

Galera cluster maintenance
--------------------------

.. toctree::

   ops-galera-remove.rst
   ops-galera-start.rst
   ops-galera-recovery.rst

Routine maintenance includes gracefully adding or removing nodes from
the cluster without impacting operation and also starting a cluster
after gracefully shutting down all nodes.

MySQL instances are restarted when creating a cluster, adding a
node, the service isn't running, or when changes are made to the
``/etc/mysql/my.cnf`` configuration file.
--------------

.. include:: navigation.txt
