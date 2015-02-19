OpenStack swift
###############
:tags: openstack, swift, cloud, ansible
:category: \*nix

Role to install swift and swift registry.

This role will install the following:
    * swift

.. code-block:: yaml

    - name: Install swift server
      hosts: swift_all
      user: root
      roles:
        - { role: "os_swift", tags: [ "os-swift" ] }
      vars:
        external_lb_vip_address: 172.16.24.1
        internal_lb_vip_address: 192.168.0.1
        galera_address: "{{ internal_lb_vip_address }}"
