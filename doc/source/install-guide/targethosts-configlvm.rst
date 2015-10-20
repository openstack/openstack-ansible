`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring LVM
---------------

#. To use the optional Block Storage (cinder) service, create an LVM
   volume group named *cinder-volumes* on the Block Storage host. A
   metadata size of 2048 must be specified during physical volume
   creation. For example:

   .. code-block:: shell-session

       # pvcreate --metadatasize 2048 physical_volume_device_path
       # vgcreate cinder-volumes physical_volume_device_path

#. Optionally, create an LVM volume group named *lxc* for container file
   systems. If the lxc volume group does not exist, containers will be
   automatically installed into the file system under */var/lib/lxc* by
   default.

--------------

.. include:: navigation.txt
