Pin apt packages
################
:tags: openstack, apt, pinning, cloud, ansible
:category: \*nix

Role for pinning apt packages.

Example Ansible play

.. code-block:: yaml

    - name: Pin packages on all "hosts"
      hosts: hosts
      user: root
      roles:
        - { role: "apt_package_pinning", tags: [ "apt-package-pinning" ] }
      vars:
        apt_pinned_packages:
          - { package: "lxc", version: "1.0.7-0ubuntu0.1" }
          - { package: "libvirt-bin", version: "1.2.2-0ubuntu13.1.9" }
          - { package: "rabbitmq-server", origin: "www.rabbitmq.com" }
          - { package: "*", release: "MariaDB" }
