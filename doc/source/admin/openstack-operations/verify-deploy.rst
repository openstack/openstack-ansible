===============================
Verifying your cloud deployment
===============================

This is a draft cloud verification page for the proposed
OpenStack-Ansible operations guide.

Verifying your OpenStack-Ansible operation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This chapter goes through the verification steps for a basic operation of
the OpenStack API and dashboard.

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
   balancer IP address. This is defined by the ``external_lb_vip_address``
   option in the ``/etc/openstack_deploy/openstack_user_config.yml``
   file. The dashboard uses HTTPS on port 443.

#. Authenticate using the username ``admin`` and password defined by
   the ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_secrets.yml`` file.

#. Run an OpenStack command to reveal all endpoints from your deployment.
   For example:

   .. code::

      $ openstack endpoint list
      +----------------------------------+-----------+--------------+----------------+---------+-----------+--------------------------------------------------+
      | ID                               | Region    | Service Name | Service Type   | Enabled | Interface | URL                                              |
      +----------------------------------+-----------+--------------+----------------+---------+-----------+--------------------------------------------------+
      | 047ba01661334602abdb5cda12c2ef7d | RegionOne | cinderv2     | volumev2       | True    | admin     | http://172.29.236.100:8776/v2/%(tenant_id)s      |
      | 0c2e4ed0526e49149b1aeb55a744098e | RegionOne | cinder       | volume         | True    | public    | https://10.23.100.127:8776/v1/%(tenant_id)s      |
      | 0deb2ba5d07e47f0a690429b45213ed6 | RegionOne | aodh         | alarming       | True    | internal  | http://172.29.236.100:8042                       |
      | 0e95096aad824bcbab637add1c418f90 | RegionOne | glance       | image          | True    | public    | https://10.23.100.127:9292                       |
      | 12551bc5ba6b475cae1dd579ddcb4357 | RegionOne | cinderv2     | volumev2       | True    | internal  | http://172.29.236.100:8776/v2/%(tenant_id)s      |
      | 1316cd02ca5f4f1790ce7e212a37c2b5 | RegionOne | heat-cfn     | cloudformation | True    | admin     | http://172.29.236.100:8000/v1                    |
      | 1b54d54397154eca8c030b9294e0ef45 | RegionOne | neutron      | network        | True    | admin     | http://172.29.236.100:9696                       |
      | 1f256cadb4a04cd98a832970d615053c | RegionOne | aodh         | alarming       | True    | public    | https://10.23.100.127:8042                       |
      | 2116a50e1d8c4a3ab0ce1895bbe1fe19 | RegionOne | nova         | compute        | True    | admin     | http://172.29.236.100:8774/v2.1/%(tenant_id)s    |
      | 221c329f609d41d5a86bfa38f6e26b6e | RegionOne | heat-cfn     | cloudformation | True    | internal  | http://172.29.236.100:8000/v1                    |
      | 2d0468997f584d7a8d48d4b174394e16 | RegionOne | swift        | object-store   | True    | public    | https://10.23.100.127:8080/v1/AUTH_%(tenant_id)s |
      | 30971d32cc6047f1a68e719e4763a360 | RegionOne | designate    | dns            | True    | admin     | http://172.29.236.100:9001                       |
      | 3243253d50384373b3de8ca7cee03644 | RegionOne | cinderv2     | volumev2       | True    | public    | https://10.23.100.127:8776/v2/%(tenant_id)s      |
      | 35ed5b4756bc4e9b84b434d4ef748445 | RegionOne | keystone     | identity       | True    | admin     | http://172.29.236.100:35357/v3                   |
      | 35f2517709154381a85dba6a28f668c6 | RegionOne | ceilometer   | metering       | True    | admin     | http://172.29.236.100:8777/                      |
      | 4879bb2c0fc14de6ba73393a68d4b1dd | RegionOne | nova         | compute        | True    | public    | https://10.23.100.127:8774/v2.1/%(tenant_id)s    |
      | 48ee308e550445a9a4e89e14f3e0f696 | RegionOne | keystone     | identity       | True    | internal  | http://172.29.236.100:5000/v3                    |
      | 4dd6738824af42b499dd0b255bc0b7f8 | RegionOne | nova         | compute        | True    | internal  | http://172.29.236.100:8774/v2.1/%(tenant_id)s    |
      | 547266c8950e406f8c9a5b3e8ea278a3 | RegionOne | gnocchi      | metric         | True    | public    | https://10.23.100.127:8041                       |
      | 58e6317b9b834ba98d7e70ffc22f6be2 | RegionOne | neutron      | network        | True    | internal  | http://172.29.236.100:9696                       |
      | 676237d45bb6415eae4efba01e3f4919 | RegionOne | aodh         | alarming       | True    | admin     | http://172.29.236.100:8042                       |
      | 67b4f58f322b4165b40f41ab372bffec | RegionOne | heat         | orchestration  | True    | admin     | http://172.29.236.100:8004/v1/%(tenant_id)s      |
      | 6bd40e07f13f475db4d795a89b0fcbe7 | RegionOne | glance       | image          | True    | internal  | http://172.29.236.100:9292                       |
      | 760220c89e1c48dfa250f7f5f91035d3 | RegionOne | designate    | dns            | True    | internal  | http://172.29.236.100:9001                       |
      | 7e7dd80831954e6db16d317fb9bd8524 | RegionOne | cinder       | volume         | True    | internal  | http://172.29.236.100:8776/v1/%(tenant_id)s      |
      | 82b7373368c8401a9a1a6347a35e44ab | RegionOne | heat-cfn     | cloudformation | True    | public    | https://10.23.100.127:8000/v1                    |
      | 90e1bb2aeb7140af83343bd30d05107b | RegionOne | ceilometer   | metering       | True    | public    | https://10.23.100.127:8777                       |
      | 913c22b8664a4108b2e754761132cdb1 | RegionOne | designate    | dns            | True    | public    | http://10.23.100.127:9001                        |
      | 9f593894bd4c4e9293a314dd9b3fe688 | RegionOne | swift        | object-store   | True    | admin     | http://172.29.236.100:8080/v1/AUTH_%(tenant_id)s |
      | a184a037133845efb501589e5c7cf549 | RegionOne | heat         | orchestration  | True    | internal  | http://172.29.236.100:8004/v1/%(tenant_id)s      |
      | a23c4e39cdae4cd3b5976dd163eb722a | RegionOne | ceilometer   | metering       | True    | internal  | http://172.29.236.100:8777                       |
      | af34e48f4ed74e44984e9c5de1900cbe | RegionOne | cinder       | volume         | True    | admin     | http://172.29.236.100:8776/v1/%(tenant_id)s      |
      | b0d88d7eb5c84cb69ef39405d8121ca9 | RegionOne | swift        | object-store   | True    | internal  | http://172.29.236.100:8080/v1/AUTH_%(tenant_id)s |
      | b110eea649a244c0bb3276ae05335e0e | RegionOne | neutron      | network        | True    | public    | https://10.23.100.127:9696                       |
      | bed8df5c8ea643ec9bad01b841618e55 | RegionOne | heat         | orchestration  | True    | public    | https://10.23.100.127:8004/v1/%(tenant_id)s      |
      | c1fc69bf16d2481ca280d84b24d524f7 | RegionOne | gnocchi      | metric         | True    | admin     | http://172.29.236.100:8041                       |
      | e65fafe30d134cba9dd0e4a142fa208c | RegionOne | gnocchi      | metric         | True    | internal  | http://172.29.236.100:8041                       |
      | efe1f79e934d43fcbbb5d3a11e99dfd6 | RegionOne | keystone     | identity       | True    | public    | https://10.23.100.127:5000/v3                    |
      | f4d9e799d4de4635a3d3b66da591841b | RegionOne | glance       | image          | True    | admin     | http://172.29.236.100:9292                       |
      +----------------------------------+-----------+--------------+----------------+---------+-----------+--------------------------------------------------+

