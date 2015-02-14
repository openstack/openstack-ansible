OpenStack memcached servers
###########################
:tags: openstack, memcached, server, cloud, ansible
:category: \*nix

Role for the deployoment and installation of Memcached

.. code-block:: yaml

    - name: Install memcached
      hosts: memcached
      user: root
      roles:
        - { role: "memcached_server", tags: [ "memcached-server" ] }
      vars:
        memcached_listen: "10.0.0.1"
