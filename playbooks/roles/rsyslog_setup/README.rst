OpenStack rsyslog server
########################
:tags: openstack, rsyslog, server, cloud, ansible
:category: \*nix

Role to deploy rsyslog for use within OpenStack when deploying services using containers. 

.. code-block:: yaml

    - name: Install rsyslog
      hosts: rsyslog
      user: root
      roles:
        - { role: "rsyslog_setup", tags: [ "rsyslog-setup" ] }
