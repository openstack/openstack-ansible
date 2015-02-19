OpenStack Haproxy Server
########################
:tags: openstack, galera, haproxy, cloud, ansible
:category: \*nix

Role for the installation and setup of haproxy

.. code-block:: yaml

    - name: Install haproxy
      hosts: haproxy_hosts
      user: root
      roles:
        - { role: "haproxy_server", tags: [ "haproxy-server" ] }
      vars:
        haproxy_service_configs:
          - service:
              hap_service_name: group_name
              hap_backend_nodes: "{{ groups['group_name'][0] }}"
              hap_backup_nodes: "{{ groups['group_name'][1:] }}"
              hap_port: 80
              hap_balance_type: http
              hap_backend_options:
                - "forwardfor"
                - "httpchk"
                - "httplog"
