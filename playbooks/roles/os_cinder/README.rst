OpenStack cinder
################
:tags: openstack, cinder, cloud, ansible
:category: \*nix

Role for deployment, setup and installation of cinder.

This role will install the following:
    * cinder-api
    * cinder-volume
    * cinder-scheduler

.. code-block:: yaml

    - name: Installation and setup of cinder
      hosts: cinder_all
      user: root
      roles:
        - { role: "os_cinder", tags: [ "os-cinder" ] }
      vars:
        galera_address: "{{ internal_lb_vip_address }}"
