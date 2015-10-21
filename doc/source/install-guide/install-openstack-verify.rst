`Home <index.html>`_ OpenStack-Ansible Installation Guide

Verifying OpenStack operation
-----------------------------

Verify basic operation of the OpenStack API and dashboard.


**Procedure 8.1. Verifying the API**

The utility container provides a CLI environment for additional
configuration and testing.

#. Determine the utility container name:

   .. code-block:: shell-session

       # lxc-ls | grep utility
       infra1_utility_container-161a4084

#. Access the utility container:

   .. code-block:: shell-session

       # lxc-attach -n infra1_utility_container-161a4084

#. Source the ``admin`` tenant credentials:

   .. code-block:: shell-session

       # source openrc

#. Run an OpenStack command that uses one or more APIs. For example:

   .. code-block:: shell-session

       # keystone user-list
       +----------------------------------+----------+---------+-------+
       |                id                |   name   | enabled | email |
       +----------------------------------+----------+---------+-------+
       | 090c1023d0184a6e8a70e26a5722710d |  admin   |   True  |       |
       | 239e04cd3f7d49929c7ead506d118e40 |  cinder  |   True  |       |
       | e1543f70e56041679c013612bccfd4ee | cinderv2 |   True  |       |
       | bdd2df09640e47888f819057c8e80f04 |   demo   |   True  |       |
       | 453dc7932df64cc58e36bf0ac4f64d14 |   ec2    |   True  |       |
       | 257da50c5cfb4b7c9ca8334bc096f344 |  glance  |   True  |       |
       | 6e0bc047206f4f5585f7b700a8ed6e94 |   heat   |   True  |       |
       | 187ee2e32eec4293a3fa243fa21f6dd9 | keystone |   True  |       |
       | dddaca4b39194dc4bcefd0bae542c60a | neutron  |   True  |       |
       | f1c232f9d53c4adabb54101ccefaefce |   nova   |   True  |       |
       | fdfbda23668c4980990708c697384050 |  novav3  |   True  |       |
       | 744069c771d84f1891314388c1f23686 |    s3    |   True  |       |
       | 4e7fdfda8d14477f902eefc8731a7fdb |  swift   |   True  |       |
       +----------------------------------+----------+---------+-------+

 

**Procedure 8.2. Verifying the dashboard**

#. With a web browser, access the dashboard using the external load
   balancer IP address defined by the ``external_lb_vip_address`` option
   in the ``/etc/openstack_deploy/openstack_user_config.yml`` file. The
   dashboard uses HTTPS on port 443.

#. Authenticate using the username ``admin`` and password defined by the
   ``keystone_auth_admin_password`` option in the
   ``/etc/openstack_deploy/user_variables.yml`` file.

Uploading public images using the dashboard or CLI can only be performed
by users with administrator privileges.

--------------

.. include:: navigation.txt
