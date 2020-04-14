Prune Inventory Backup Archive
==============================

The inventory backup archive will require maintenance over a long enough
period of time.


Bulk pruning
------------

It is possible to do mass pruning of the inventory backup. The following
example will prune all but the last 15 inventories from the running archive.

.. code-block:: bash

  ARCHIVE="/etc/openstack_deploy/backup_openstack_inventory.tar"
  tar -tvf ${ARCHIVE} | \
    head -n -15 | awk '{print $6}' | \
    xargs -n 1 tar -vf ${ARCHIVE} --delete


Selective Pruning
-----------------

To prune the inventory archive selectively, first identify the files you wish
to remove by listing them out.

.. code-block:: bash

  tar -tvf /etc/openstack_deploy/backup_openstack_inventory.tar

  -rw-r--r-- root/root    110096 2018-05-03 10:11 openstack_inventory.json-20180503_151147.json
  -rw-r--r-- root/root    110090 2018-05-03 10:11 openstack_inventory.json-20180503_151205.json
  -rw-r--r-- root/root    110098 2018-05-03 10:12 openstack_inventory.json-20180503_151217.json


Now delete the targeted inventory archive.

.. code-block:: bash

  tar -vf /etc/openstack_deploy/backup_openstack_inventory.tar --delete openstack_inventory.json-20180503_151205.json
