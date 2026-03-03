.. _verify-operation:

=============================
Verifying OpenStack operation
=============================

.. figure:: figures/installation-workflow-verify-openstack.png
   :width: 100%

To verify basic operation of the OpenStack API and the Dashboard, perform the
following tasks on an infrastructure host.

Verify the API
~~~~~~~~~~~~~~

The utility container provides a CLI environment for additional
configuration and testing.

#. Determine the name of the utility container:

   .. code-block:: console

      # lxc-ls | grep utility
      infra1_utility_container-161a4084

#. Access the utility container:

   .. code-block:: console

      # lxc-attach -n infra1_utility_container-161a4084

#. Source the ``admin`` project credentials:

   .. code::

      $ . ~/openrc

#. List your openstack users:

   .. code-block:: console

      # openstack user list --os-cloud=default
      +----------------------------------+--------------------+
      | ID                               | Name               |
      +----------------------------------+--------------------+
      | 08fe5eeeae314d578bba0e47e7884f3a | alt_demo           |
      | 0aa10040555e47c09a30d2240e474467 | dispersion         |
      | 10d028f9e47b4d1c868410c977abc3df | glance             |
      | 249f9ad93c024f739a17ca30a96ff8ee | demo               |
      | 39c07b47ee8a47bc9f9214dca4435461 | swift              |
      | 3e88edbf46534173bc4fd8895fa4c364 | cinder             |
      | 41bef7daf95a4e72af0986ec0583c5f4 | neutron            |
      | 4f89276ee4304a3d825d07b5de0f4306 | admin              |
      | 943a97a249894e72887aae9976ca8a5e | nova               |
      | ab4f0be01dd04170965677e53833e3c3 | stack_domain_admin |
      | ac74be67a0564722b847f54357c10b29 | heat               |
      | b6b1d5e76bc543cda645fa8e778dff01 | ceilometer         |
      | dc001a09283a404191ff48eb41f0ffc4 | aodh               |
      | e59e4379730b41209f036bbeac51b181 | keystone           |
      +----------------------------------+--------------------+

Verifying the Dashboard (Horizon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. With a web browser, access the Dashboard by using the external load
   balancer domain name or IP address defined by the
   ``external_lb_vip_address`` option in the
   ``/etc/openstack_deploy/openstack_user_config.yml`` file. The
   Dashboard uses HTTPS on port 443.

#. Authenticate by using the ``admin`` user name and the password defined by
   the ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_secrets.yml`` file.
