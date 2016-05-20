`Home <index.html>`_ OpenStack-Ansible Installation Guide

Storage devices
===============

This section offers a set of prerequisite instructions for setting up
Object Storage (swift) storage devices. The storage devices must be set up
before installing swift.

**Procedure 5.1. Configuring and mounting storage devices**

Object Storage recommends a minimum of three swift hosts
with five storage disks. The example commands in this procedure
use the storage devices ``sdc`` through to ``sdg``.

#. Determine the storage devices on the node to be used for swift.

#. Format each device on the node used for storage with XFS. While
   formatting the devices, add a unique label for each device.

   Without labels, a failed drive causes mount points to shift and
   data to become inaccessible.

   For example, create the file systems on the devices using the
   ``mkfs`` command:

   .. code-block:: shell-session

       # apt-get install xfsprogs
       # mkfs.xfs -f -i size=1024 -L sdc /dev/sdc
       # mkfs.xfs -f -i size=1024 -L sdd /dev/sdd
       # mkfs.xfs -f -i size=1024 -L sde /dev/sde
       # mkfs.xfs -f -i size=1024 -L sdf /dev/sdf
       # mkfs.xfs -f -i size=1024 -L sdg /dev/sdg

#. Add the mount locations to the ``fstab`` file so that the storage
   devices are remounted on boot. The following example mount options
   are recommended when using XFS:

   .. code-block:: shell-session

       LABEL=sdc /srv/node/sdc xfs noatime,nodiratime,nobarrier,logbufs=8,noauto 0 0
       LABEL=sdd /srv/node/sdd xfs noatime,nodiratime,nobarrier,logbufs=8,noauto 0 0
       LABEL=sde /srv/node/sde xfs noatime,nodiratime,nobarrier,logbufs=8,noauto 0 0
       LABEL=sdf /srv/node/sdf xfs noatime,nodiratime,nobarrier,logbufs=8,noauto 0 0
       LABEL=sdg /srv/node/sdg xfs noatime,nodiratime,nobarrier,logbufs=8,noauto 0 0

#. Create the mount points for the devices using the ``mkdir`` command:

   .. code-block:: shell-session

       # mkdir -p /srv/node/sdc
       # mkdir -p /srv/node/sdd
       # mkdir -p /srv/node/sde
       # mkdir -p /srv/node/sdf
       # mkdir -p /srv/node/sdg

   The mount point is referenced as the ``mount_point`` parameter in
   the ``swift.yml`` file (``/etc/rpc_deploy/conf.d/swift.yml``):

   .. code-block:: shell-session

       # mount /srv/node/sdc
       # mount /srv/node/sdd
       # mount /srv/node/sde
       # mount /srv/node/sdf
       # mount /srv/node/sdg

To view an annotated example of the ``swift.yml`` file, see `Appendix A,
*OSA configuration files* <app-configfiles.html>`_.

For the following mounted devices:

+--------------------------------------+--------------------------------------+
| Device                               | Mount location                       |
+======================================+======================================+
| /dev/sdc                             | /srv/node/sdc                        |
+--------------------------------------+--------------------------------------+
| /dev/sdd                             | /srv/node/sdd                        |
+--------------------------------------+--------------------------------------+
| /dev/sde                             | /srv/node/sde                        |
+--------------------------------------+--------------------------------------+
| /dev/sdf                             | /srv/node/sdf                        |
+--------------------------------------+--------------------------------------+
| /dev/sdg                             | /srv/node/sdg                        |
+--------------------------------------+--------------------------------------+

Table: Table 5.1. Mounted devices

The entry in the ``swift.yml``:

.. code-block:: yaml

    #    drives:
    #        - name: sdc
    #        - name: sdd
    #        - name: sde
    #        - name: sdf
    #        - name: sdg
    #    mount_point: /srv/node

--------------

.. include:: navigation.txt
