OpenStack rsyslog client
########################
:tags: openstack, rsyslog, server, cloud, ansible
:category: \*nix

Role to deploy rsyslog for use within OpenStack.

.. code-block:: yaml

    - name: Install rsyslog
      hosts: rsyslog
      user: root
      roles:
        - { role: "rsyslog_client", tags: [ "rsyslog-client" ] }
