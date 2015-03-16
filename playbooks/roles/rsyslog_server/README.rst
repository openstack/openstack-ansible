OpenStack rsyslog server
########################
:tags: openstack, rsyslog, server, cloud, ansible
:category: \*nix

Role to deploy rsyslog for use within OpenStack when deploying services using containers.

.. code-block:: yaml

    - name: Install rsyslog
      hosts: rsyslog
      max_fail_percentage: 20
      user: root
      roles:
        - { role: "rsyslog_server", tags: [ "rsyslog-server" ] }
