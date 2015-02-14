OpenStack openrc file
#####################
:tags: openstack, openrc, cloud, ansible
:category: \*nix

Role for the creation of an openrc file for the intended purpose to set credentials up for use within OpenStack.

.. code-block:: yaml

    - name: Install memcached
      hosts: memcached
      user: root
      roles:
        - { role: "memcached_server", tags: [ "memcached-server" ] }
      vars:
        openrc_cinder_endpoint_type: internalURL
        openrc_nova_endpoint_type: internalURL
        openrc_os_endpoint_type: internalURL
        openrc_os_username: admin
        openrc_os_tenant_name: admin
        openrc_os_auth_url: "http://10.0.0.1:5000"
        openrc_os_password: "secrete"
        openrc_file_dest: /root/openrc
