OpenStack nova
##############
:tags: openstack, nova, cloud, ansible
:category: \*nix

Role for deployment, setup and installation of nova.

This role will install the following:
    * nova-consoleauth
    * nova-conductor
    * nova-compute
    * nova-cert
    * nova-api-metadata
    * nova-spicehtml5proxy
    * nova-api-ec2
    * nova-api-os-compute
    * nova-api-ec2

.. code-block:: yaml

    - name: Installation and setup of Nova
      hosts: nova_all
      user: root
      roles:
        - { role: "os_nova", tags: [ "os-nova" ] }
      vars:
        galera_address: "{{ internal_lb_vip_address }}"
