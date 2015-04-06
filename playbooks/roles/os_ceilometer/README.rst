OpenStack ceilometer
####################
:tags: openstack, ceilometer, cloud, ansible
:category: \*nix

Role to install ceilometer and ceilometer registry.

This role will install the following:
    * ceilometer-api
    * ceilometer-registry

.. code-block:: yaml

    - name: Install ceilometer server
      hosts: ceilometer_all
      user: root
      roles:
        - { role: "os_ceilometer", tags: [ "os-ceilometer" ] }
      vars:
        external_lb_vip_address: 172.16.24.1
        internal_lb_vip_address: 192.168.0.1
        galera_address: "{{ internal_lb_vip_address }}"
