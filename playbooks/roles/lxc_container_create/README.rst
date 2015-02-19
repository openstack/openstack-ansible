OpenStack LXC container create
##############################
:tags: openstack, lxc, container, cloud, ansible
:category: \*nix

Role for creating LXC containers. This role has been setup for use in OpenStack. This role will create several directories on the LXC host for use in bind mounted storage within the container. 

Example Play:
    .. code-block:: yaml

        - name: Create container(s)
          hosts: all_containers
          gather_facts: false
          user: root
          roles:
            - { role: "lxc_container_create", tags: [ "lxc-container-create" ] }


Example Inventory:
    .. code-block:: json

        {
            "all_containers": {
                "children": [
                    "group_of_containers"
                ],
                "hosts": []
            },
            "lxc_hosts": {
                "children": [],
                "hosts": [
                    "infra1"
                ]
            },
            "group_of_containers": {
                "children": [],
                "hosts": [
                    "container1"
                ]
            },
            "_meta": {
                "hostvars": {
                    "infra1": {
                        "ansible_ssh_host": "192.168.0.1",
                        "container_address": "192.168.0.1",
                        "container_name": "infra1",
                        "container_networks": {
                            "management_address": {
                                "bridge": "br-mgmt",
                                "interface": "eth1",
                                "netmask": "255.255.252.0",
                                "type": "veth"
                            }
                        },
                        "properties": {
                            "container_release": "trusty",
                            "is_metal": true
                        }
                    },
                    "container1": {
                        "ansible_ssh_host": "10.0.0.1",
                        "container_address": "10.0.0.1",
                        "container_name": "container1",
                        "container_networks": {
                            "management_address": {
                                "address": "10.0.0.1",
                                "bridge": "br-mgmt",
                                "interface": "eth1",
                                "netmask": "255.255.252.0",
                                "type": "veth"
                            }
                        },
                        "physical_host": "infra1",
                        "physical_host_group": "lxc_hosts",
                        "properties": {
                            "container_release": "trusty",
                        }
                    }
                }
            }
        }
