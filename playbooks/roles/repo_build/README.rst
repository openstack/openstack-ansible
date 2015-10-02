OpenStack repo build
#####################
:tags: openstack, repo, build, cloud, ansible
:category: \*nix

Role to deploy a repository build for both python packages and git sources.

.. code-block:: yaml

    - name: Setup repo builds
      hosts: repo_all
      user: root
      roles:
        - { role: "repo_build", tags: [ "repo-build" ] }
      vars:
        memcached_builds: 127.0.0.1:11211
        memcached_encryption_key: secrete
