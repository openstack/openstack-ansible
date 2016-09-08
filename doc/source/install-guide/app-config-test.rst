==================================================
Appendix A: Example test environment configuration
==================================================

Introduction
~~~~~~~~~~~~

The test environment is a minimal set of components to deploy a working
OpenStack-Ansible environment for testing purposes.

The test environment has the following characteristics:

* One control plane host (8 vCPU, 8GB RAM, 60GB HDD)
* One compute host (8 vCPU, 8GB RAM, 60GB HDD)
* Each host only has one Network Interface Card (NIC)
* Only a basic compute kit environment will be installed, with glance
  and nova set to use file-backed storage.

.. image:: figures/arch-layout-test.png
   :width: 100%
   :alt: Test environment host layout

Network configuration
~~~~~~~~~~~~~~~~~~~~~

.. TBD

Environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/openstack_user_config.yml`` configuration file
sets the hosts available in the groups. This designates the services that
runs on them.

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.aio

