`Home <index.html>`_ OpenStack-Ansible Installation Guide

NFS back-end
------------

If the NetApp back end is configured to use an NFS storage protocol,
edit ``/etc/openstack_deploy/openstack_user_config.yml``, and configure
the NFS client on each storage node that will use it.

#. Add the ``cinder_backends`` stanza (which includes
   ``cinder_nfs_client``) under the ``container_vars`` stanza for
   each storage node:

   .. code-block:: yaml

       container_vars:
         cinder_backends:
           cinder_nfs_client:

#. Configure the location of the file that lists shares available to the
   block storage service. This configuration file must include
   ``nfs_shares_config``:

   .. code-block:: yaml

       nfs_shares_config: SHARE_CONFIG

   Replace ``SHARE_CONFIG`` with the location of the share
   configuration file. For example, ``/etc/cinder/nfs_shares``.

#. Configure one or more NFS shares:

   .. code-block:: yaml

       shares:
          - { ip: "NFS_HOST", share: "NFS_SHARE" }

   Replace ``NFS_HOST`` with the IP address or hostname of the NFS
   server, and the ``NFS_SHARE`` with the absolute path to an existing
   and accessible NFS share.

--------------

.. include:: navigation.txt
