OpenStack Galera Client
#######################
:tags: openstack, galera, client, cloud, ansible
:category: \*nix

Role for the installation of the mariadb and xtrabackup clients used to interact with and manage a galera cluster.

Example Ansible play

.. code-block:: yaml

    - name: Install galera server
      hosts: galera_all
      user: root
      roles:
        - { role: "galera_server", tags: [ "galera-server" ] }
      vars:
        galera_address: "10.0.0.1"
        galera_root_password: secrete
        galera_root_user: root
