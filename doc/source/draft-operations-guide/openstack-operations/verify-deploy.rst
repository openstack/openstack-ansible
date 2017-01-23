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

      $ lxc-attach -n `lxc-ls -1 | grep utility`

#. Source the ``admin`` tenant credentials:

   .. code::

      # source openrc

#. Run an OpenStack command that uses one or more APIs. For example:

   .. code::

      # openstack user list --domain default
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
