Check your OpenStack-Ansible cloud
==================================

This chapter goes through the verification steps for a basic operation of
the OpenStack API and dashboard, as an administrator.

.. note::

   The utility container provides a CLI environment for additional
   configuration and testing.

#. Access the utility container:

   .. code::

      $ lxc-attach -n `lxc-ls -1 | grep utility | head -n 1`

#. Source the ``admin`` tenant credentials:

   .. code::

      $ . ~/openrc

#. Run an OpenStack command that uses one or more APIs. For example:

   .. code::

      $ openstack user list --domain default
      +----------------------------------+--------------------+
      | ID                               | Name               |
      +----------------------------------+--------------------+
      | 04007b990d9442b59009b98a828aa981 | glance             |
      | 0ccf5f2020ca4820847e109edd46e324 | keystone           |
      | 1dc5f638d4d840c690c23d5ea83c3429 | neutron            |
      | 3073d0fa5ced46f098215d3edb235d00 | cinder             |
      | 5f3839ee1f044eba921a7e8a23bb212d | admin              |
      | 61bc8ee7cc9b4530bb18acb740ee752a | stack_domain_admin |
      | 77b604b67b79447eac95969aafc81339 | alt_demo           |
      | 85c5bf07393744dbb034fab788d7973f | nova               |
      | a86fc12ade404a838e3b08e1c9db376f | swift              |
      | bbac48963eff4ac79314c42fc3d7f1df | ceilometer         |
      | c3c9858cbaac4db9914e3695b1825e41 | dispersion         |
      | cd85ca889c9e480d8ac458f188f16034 | demo               |
      | efab6dc30c96480b971b3bd5768107ab | heat               |
      +----------------------------------+--------------------+

#. With a web browser, access the Dashboard using the external load
   balancer domain name or IP address. This is defined by the
   ``external_lb_vip_address`` option in the
   ``/etc/openstack_deploy/openstack_user_config.yml`` file.
   The dashboard uses HTTPS on port 443.

#. Authenticate using the username ``admin`` and password defined by
   the ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_secrets.yml`` file.

#. Run an OpenStack command to reveal all endpoints from your deployment.
   For example:

   .. code::

      $ openstack endpoint list
      +----------------+-----------+--------------+----------------+---------+-----------+---------------------------------------------------+
      | ID             | Region    | Service Name | Service Type   | Enabled | Interface | URL                                               |
      +----------------+-----------+--------------+----------------+---------+-----------+---------------------------------------------------+
      | [ID truncated] | RegionOne | cinderv2     | volumev2       | True    | admin     | http://172.29.236.100:8776/v2/%(project_id)s      |
      | [ID truncated] | RegionOne | cinderv3     | volumev3       | True    | public    | https://10.23.100.127:8776/v3/%(project_id)s      |
      | [ID truncated] | RegionOne | aodh         | alarming       | True    | internal  | http://172.29.236.100:8042                        |
      | [ID truncated] | RegionOne | glance       | image          | True    | public    | https://10.23.100.127:9292                        |
      | [ID truncated] | RegionOne | cinderv2     | volumev2       | True    | internal  | http://172.29.236.100:8776/v2/%(project_id)s      |
      | [ID truncated] | RegionOne | heat-cfn     | cloudformation | True    | admin     | http://172.29.236.100:8000/v1                     |
      | [ID truncated] | RegionOne | neutron      | network        | True    | admin     | http://172.29.236.100:9696                        |
      | [ID truncated] | RegionOne | aodh         | alarming       | True    | public    | https://10.23.100.127:8042                        |
      | [ID truncated] | RegionOne | nova         | compute        | True    | admin     | http://172.29.236.100:8774/v2.1/%(project_id)s    |
      | [ID truncated] | RegionOne | heat-cfn     | cloudformation | True    | internal  | http://172.29.236.100:8000/v1                     |
      | [ID truncated] | RegionOne | swift        | object-store   | True    | public    | https://10.23.100.127:8080/v1/AUTH_%(project_id)s |
      | [ID truncated] | RegionOne | designate    | dns            | True    | admin     | http://172.29.236.100:9001                        |
      | [ID truncated] | RegionOne | cinderv2     | volumev2       | True    | public    | https://10.23.100.127:8776/v2/%(project_id)s      |
      | [ID truncated] | RegionOne | keystone     | identity       | True    | admin     | http://172.29.236.100:5000/v3                     |
      | [ID truncated] | RegionOne | nova         | compute        | True    | public    | https://10.23.100.127:8774/v2.1/%(project_id)s    |
      | [ID truncated] | RegionOne | keystone     | identity       | True    | internal  | http://172.29.236.100:5000/v3                     |
      | [ID truncated] | RegionOne | nova         | compute        | True    | internal  | http://172.29.236.100:8774/v2.1/%(project_id)s    |
      | [ID truncated] | RegionOne | gnocchi      | metric         | True    | public    | https://10.23.100.127:8041                        |
      | [ID truncated] | RegionOne | neutron      | network        | True    | internal  | http://172.29.236.100:9696                        |
      | [ID truncated] | RegionOne | aodh         | alarming       | True    | admin     | http://172.29.236.100:8042                        |
      | [ID truncated] | RegionOne | heat         | orchestration  | True    | admin     | http://172.29.236.100:8004/v1/%(project_id)s      |
      | [ID truncated] | RegionOne | glance       | image          | True    | internal  | http://172.29.236.100:9292                        |
      | [ID truncated] | RegionOne | designate    | dns            | True    | internal  | http://172.29.236.100:9001                        |
      | [ID truncated] | RegionOne | cinderv3     | volume         | True    | internal  | http://172.29.236.100:8776/v3/%(project_id)s      |
      | [ID truncated] | RegionOne | heat-cfn     | cloudformation | True    | public    | https://10.23.100.127:8000/v1                     |
      | [ID truncated] | RegionOne | designate    | dns            | True    | public    | https://10.23.100.127:9001                        |
      | [ID truncated] | RegionOne | swift        | object-store   | True    | admin     | http://172.29.236.100:8080/v1/AUTH_%(project_id)s |
      | [ID truncated] | RegionOne | heat         | orchestration  | True    | internal  | http://172.29.236.100:8004/v1/%(project_id)s      |
      | [ID truncated] | RegionOne | cinderv3     | volumev3       | True    | admin     | http://172.29.236.100:8776/v3/%(project_id)s      |
      | [ID truncated] | RegionOne | swift        | object-store   | True    | internal  | http://172.29.236.100:8080/v1/AUTH_%(project_id)s |
      | [ID truncated] | RegionOne | neutron      | network        | True    | public    | https://10.23.100.127:9696                        |
      | [ID truncated] | RegionOne | heat         | orchestration  | True    | public    | https://10.23.100.127:8004/v1/%(project_id)s      |
      | [ID truncated] | RegionOne | gnocchi      | metric         | True    | admin     | http://172.29.236.100:8041                        |
      | [ID truncated] | RegionOne | gnocchi      | metric         | True    | internal  | http://172.29.236.100:8041                        |
      | [ID truncated] | RegionOne | keystone     | identity       | True    | public    | https://10.23.100.127:5000/v3                     |
      | [ID truncated] | RegionOne | glance       | image          | True    | admin     | http://172.29.236.100:9292                        |
      | [ID truncated] | RegionOne | placement    | placement      | True    | internal  | http://172.29.236.100:8780                        |
      | [ID truncated] | RegionOne | placement    | placement      | True    | admin     | http://172.29.236.100:8780                        |
      | [ID truncated] | RegionOne | placement    | placement      | True    | public    | https://10.23.100.127:8780                        |
      +----------------+-----------+--------------+----------------+---------+-----------+---------------------------------------------------+

#. Run an OpenStack command to ensure all the compute services are
   working (the output depends on your configuration)
   For example:

   .. code::

      $ openstack compute service list
      +----+------------------+----------------------------------------+----------+---------+-------+----------------------------+
      | ID | Binary           | Host                                   | Zone     | Status  | State | Updated At                 |
      +----+------------------+----------------------------------------+----------+---------+-------+----------------------------+
      |  1 | nova-conductor   | aio1-nova-conductor-container-5482ff27 | internal | enabled | up    | 2018-02-14T15:34:42.000000 |
      |  2 | nova-scheduler   | aio1-nova-scheduler-container-0b594e89 | internal | enabled | up    | 2018-02-14T15:34:47.000000 |
      |  5 | nova-consoleauth | aio1-nova-console-container-835ca240   | internal | enabled | up    | 2018-02-14T15:34:47.000000 |
      |  6 | nova-compute     | ubuntu-focal                           | nova     | enabled | up    | 2018-02-14T15:34:42.000000 |
      +----+------------------+----------------------------------------+----------+---------+-------+----------------------------+

#. Run an OpenStack command to ensure the networking services are
   working (the output also depends on your configuration)
   For example:

   .. code::

      $ openstack network agent list
      +--------------------------------------+----------------------+----------------------------------------+-------------------+-------+-------+---------------------------+
      | ID                                   | Agent Type           | Host                                   | Availability Zone | Alive | State | Binary                    |
      +--------------------------------------+----------------------+----------------------------------------+-------------------+-------+-------+---------------------------+
      | 262b29fe-e60e-44b0-ae3c-065565f8deb7 | Metering agent       | aio1-neutron-agents-container-2b0569d5 | None              | :-)   | UP    | neutron-metering-agent    |
      | 41135f7f-9e6c-4122-b6b3-d131bfaae53e | Open vSwitch agent   | ubuntu-focal                           | None              | :-)   | UP    | neutron-openvswitch-agent |
      | 615d12a8-e738-490a-8552-2a03c8544b51 | Metadata agent       | aio1-neutron-agents-container-2b0569d5 | None              | :-)   | UP    | neutron-metadata-agent    |
      | 99b2abd3-a330-4ca7-b524-ed176c10b31c | DHCP agent           | aio1-neutron-agents-container-2b0569d5 | nova              | :-)   | UP    | neutron-dhcp-agent        |
      | e0139a26-fbf7-4cee-a37f-90940dc5851f | Open vSwitch agent   | aio1-neutron-agents-container-2b0569d5 | None              | :-)   | UP    | neutron-openvswitch-agent |
      | feb20ed4-4346-4ad9-b50c-41efd784f2e9 | L3 agent             | aio1-neutron-agents-container-2b0569d5 | nova              | :-)   | UP    | neutron-l3-agent          |
      +--------------------------------------+----------------------+----------------------------------------+-------------------+-------+-------+---------------------------+

#. Run an OpenStack command to ensure the block storage services are
   working (depends on your configuration).
   For example:

   .. code::

      $ openstack volume service list
      +------------------+------------------------------------------+------+---------+-------+----------------------------+
      | Binary           | Host                                     | Zone | Status  | State | Updated At                 |
      +------------------+------------------------------------------+------+---------+-------+----------------------------+
      | cinder-scheduler | aio1-cinder-scheduler-container-ff4c6c1e | nova | enabled | up    | 2018-02-14T15:37:21.000000 |
      | cinder-volume    | ubuntu-bionic@lvm                        | nova | enabled | up    | 2018-02-14T15:37:25.000000 |
      | cinder-backup    | ubuntu-bionic                            | nova | enabled | up    | 2018-02-14T15:37:21.000000 |
      +------------------+------------------------------------------+------+---------+-------+----------------------------+

#. Run an OpenStack command to ensure the image storage service is
   working (depends on your uploaded images).
   For example:

   .. code::

      $ openstack image list
      +--------------------------------------+--------+--------+
      | ID                                   | Name   | Status |
      +--------------------------------------+--------+--------+
      | 6092d7b3-87c1-4d6c-a822-66c0c6171bd3 | cirros | active |
      +--------------------------------------+--------+--------+

#. Check the backend API health on your load balancer nodes.
   For example, if using HAProxy, ensure no backend is marked
   as "DOWN":

   .. code ::

      $ hatop -s /var/run/haproxy.stat
