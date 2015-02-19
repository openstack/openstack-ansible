OpenStack pip lockdown
######################
:tags: openstack, pip, lockdown, cloud, ansible
:category: \*nix

Role to lock pip down to a particular links repo. This will create a ``.pip.conf`` which will ensure that the only python packages installed when using pip are from a known repository of packages.

.. code-block:: yaml

    - name: Basic lxc host setup
      hosts: host_group
      user: root
      roles:
        - { role: "pip_lock_down", tags: [ "pip-lock-down" ] }
      vars:
        pip_links:
          name: openstack-release
          link: https://openstack-hostname.something/python_packages/master


This was intended for use with a repository built from the repo role.
