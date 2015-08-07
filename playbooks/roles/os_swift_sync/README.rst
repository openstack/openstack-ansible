OpenStack swift key/ring sync
#############################
:tags: openstack, swift, cloud, ansible
:category: \*nix

Role to synchronise keys and the ring for swift hosts

This role will synchronise the following:
    * ring
    * ssh keys

.. code-block:: yaml

    - name: Sync swift rings and keys
      hosts: swift_all:swift_remote_all
      user: root
      roles:
        - { role: "os_swift_sync", tags: [ "os-swift-sync" ] }
