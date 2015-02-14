OpenStack heat
##############
:tags: openstack, heat, cloud, ansible
:category: \*nix

Role to install heat api, cfn, cloudwatch, and engine.

This role will install the following:
    * heat-api
    * heat-api-cfn
    * heat-api-cloudwatch
    * heat-engine

.. code-block:: yaml

    - name: Install heat server
      hosts: heat_all
      user: root
      roles:
        - { role: "os_heat", tags: [ "os-heat" ] }
      vars:
        external_lb_vip_address: 172.16.24.1
        internal_lb_vip_address: 192.168.0.1
        galera_address: "{{ internal_lb_vip_address }}"
        keystone_admin_user_name: admin
        keystone_admin_tenant_name: admin
