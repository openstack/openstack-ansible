Accessibility for multi-region Object Storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In multi-region Object Storage utilizing separate database backends, objects
are retrievable from an alternate location if the ``default_project_id``
for a user in the keystone database is the same across each database
backend.

.. important::

   It is recommended to perform the following steps before a failure
   occurs to avoid having to dump and restore the database.

   If a failure does occur, follow these steps to restore the database
   from the Primary (failed) Region:

#. Record the Primary Region output of the ``default_project_id`` for
   the specified user from the user table in the keystone database:

   .. note::

      The user is ``admin`` in this example.

   .. code::

      # mariadb -e "SELECT default_project_id from keystone.user WHERE \
        name='admin';"

      +----------------------------------+
      | default_project_id               |
      +----------------------------------+
      | 76ef6df109744a03b64ffaad2a7cf504 |
      +-----------------—————————————————+


#. Record the Secondary Region output of the ``default_project_id``
   for the specified user from the user table in the keystone
   database:

   .. code::

      # mariadb -e "SELECT default_project_id from keystone.user WHERE \
        name='admin';"

      +----------------------------------+
      | default_project_id               |
      +----------------------------------+
      | 69c46f8ad1cf4a058aa76640985c     |
      +----------------------------------+

#. In the Secondary Region, update the references to the
   ``project_id`` to match the ID from the Primary Region:

   .. code::

      # export PRIMARY_REGION_TENANT_ID="76ef6df109744a03b64ffaad2a7cf504"
      # export SECONDARY_REGION_TENANT_ID="69c46f8ad1cf4a058aa76640985c"

      # mariadb -e "UPDATE keystone.assignment set \
      target_id='${PRIMARY_REGION_TENANT_ID}' \
      WHERE target_id='${SECONDARY_REGION_TENANT_ID}';"

      # mariadb -e "UPDATE keystone.user set \
      default_project_id='${PRIMARY_REGION_TENANT_ID}' WHERE \
      default_project_id='${SECONDARY_REGION_TENANT_ID}';"

      # mariadb -e "UPDATE keystone.project set \
      id='${PRIMARY_REGION_TENANT_ID}' WHERE \
      id='${SECONDARY_REGION_TENANT_ID}';"

The user in the Secondary Region now has access to objects PUT in the
Primary Region. The Secondary Region can PUT objects accessible by the
user in the Primary Region.
