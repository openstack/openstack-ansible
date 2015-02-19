OpenStack install python package from git
#########################################
:tags: openstack, pip, git, cloud, ansible
:category: \*nix

Role for installing a python package from a git repository.

.. code-block:: yaml

    - name: Install python2 lxc
      hosts: hosts
      user: root
      roles:
        - { role: "py_from_git", tags: [ "lxc-libs" ] }
      vars:
        git_repo: "https://github.com/lxc/python2-lxc"
        git_dest: "/opt/lxc_python2_{{ git_install_branch|replace('/', '_') }}"
        git_install_branch: master
