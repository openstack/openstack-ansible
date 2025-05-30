Recover a compute host failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following procedure addresses Compute node failure if shared storage
is used.

.. note::

   If shared storage is not used, data can be copied from the
   ``/var/lib/nova/instances`` directory on the failed Compute node
   ``${FAILED_NODE}`` to another node ``${RECEIVING_NODE}``\ before
   performing the following procedure. Please note this method is
   not supported.

#. Re-launch all instances on the failed node.

#. Invoke the MariaDB command line tool.

#. Generate a list of instance UUIDs hosted on the failed node:

   .. code-block:: console

      mysql> select uuid from instances where host = '${FAILED_NODE}' and deleted = 0;

#. Set instances on the failed node to be hosted on a different node:

   .. code-block:: console

      mysql> update instances set host ='${RECEIVING_NODE}' where host = '${FAILED_NODE}' \
      and deleted = 0;

#. Reboot each instance on the failed node listed in the previous query
   to regenerate the XML files:

   .. code-block:: console

      # nova reboot —hard $INSTANCE_UUID

#. Find the volumes to check the instance has successfully booted and is
   at the login:

   .. code-block:: console

      mysql> select nova.instances.uuid as instance_uuid, cinder.volumes.id \
      as voume_uuid, cinder.volumes.status, cinder.volumes.attach_status, \
      cinder.volumes.mountpoint, cinder.volumes,display_name from \
      cinder.volumes inner join nova.instances on cinder.volumes.instance_uuid=nova.instances.uuid \
      where nova.instances.host = '${FAILED_NODE}';

#. If rows are found, detach and re-attach the volumes using the values
   listed in the previous query:

   .. code-block:: console

      # nova volume-detach $INSTANCE_UUID $VOLUME_UUID && \
      # nova volume-attach $INSTANCE_UUID $VOLUME_UUID $VOLUME_MOUNTPOINT

#. Rebuild or replace the failed node as described in :ref:`add-compute-host`.
