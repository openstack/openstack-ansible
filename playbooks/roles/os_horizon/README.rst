OpenStack horizon
##############
:tags: openstack, horizon, cloud, ansible
:category: \*nix

Role for deployment, setup and installation of horizon.

This role will install the following:
    * horizon-dashboard

.. code-block:: yaml

    - name: Installation and setup of horizon
      hosts: horizon_all
      user: root
      roles:
        - { role: "os_horizon", tags: [ "os-horizon" ] }
      vars:
        horizon_galera_address: "{{ internal_lb_vip_address }}"
