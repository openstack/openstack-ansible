OpenStack LXC host setup
########################
:tags: openstack, lxc, host, cloud, ansible
:category: \*nix

Role for deployment and setup of an LXC host.

.. code-block:: yaml

    - name: Basic lxc host setup
      hosts: "hosts"
      user: root
      roles:
        - { role: "lxc_hosts", tags: [ "lxc-host", "host-setup" ] }
