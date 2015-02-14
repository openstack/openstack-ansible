OpenStack glance
################
:tags: openstack, glance, cloud, ansible
:category: \*nix

Role to install glance and glance registry.

This role will install the following:
    * glance-api
    * glance-registry

.. code-block:: yaml

    - name: Install glance server
      hosts: glance_all
      user: root
      roles:
        - { role: "os_glance", tags: [ "os-glance" ] }
      vars:
        external_lb_vip_address: 172.16.24.1
        internal_lb_vip_address: 192.168.0.1
        galera_address: "{{ internal_lb_vip_address }}"
