OpenStack pip
#############
:tags: openstack, pip, cloud, ansible
:category: \*nix

This role will install pip using the upstream pip.

.. code-block:: yaml

    - name: Install pip and lock it down
      hosts: host_name
      user: root
      roles:
        - { role: "pip_lock_down", tags: [ "pip-lock-down" ] }
      vars:
        pip_get_pip_url: https://bootstrap.pypa.io/get-pip.py
