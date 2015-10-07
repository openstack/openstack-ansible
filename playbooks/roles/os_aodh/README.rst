OpenStack Aodh
##############
:tags: openstack, ceilometer, cloud, ansible, aodh
:category: \*nix

Role to install aodh as the alarm functionality of Telemetry

This role will install the following:
    * aodh-api
    * aodh-listener
    * aodh-alarm-evaluator
    * aodh-alarm-notifier

.. code-block:: yaml

    - name: Install aodh services
      hosts: aodh_all
      user: root
      roles:
        - { role: "os_aodh", tags: [ "os-aodh" ] }
      vars:
        external_lb_vip_address: 172.16.24.1
        internal_lb_vip_address: 192.168.0.1
        galera_address: "{{ internal_lb_vip_address }}"
