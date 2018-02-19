Advanced inventory topics
=========================

Changing the base environment directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``--environment/-e`` argument will take the path to a directory containing
an ``env.d`` directory. This defaults to ``inventory/`` in the
OpenStack-Ansible codebase.

Contents of this directory are populated into the environment *before* the
``env.d`` found in the directory specified by ``--config``.

Dynamic Inventory API documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: dynamic_inventory
   :members:
