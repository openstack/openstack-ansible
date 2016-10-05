.. _test-environment-config:

==================================================
Appendix A: Example test environment configuration
==================================================

Introduction
~~~~~~~~~~~~

A test environment contains the minimal set of components needed to deploy a
working OpenStack-Ansible (OSA) environment for testing purposes.

A test environment has the following characteristics:

* One infrastructure (control plane) host (8 vCPU, 8 GB RAM, 60 GB HDD)
* One compute host (8 vCPU, 8 GB RAM, 60 GB HDD)
* One Network Interface Card (NIC) for each host
* A basic compute kit environment, with the Image (glance) and Compute (nova)
  services set to use file-backed storage.

.. image:: figures/arch-layout-test.png
   :width: 100%
   :alt: Test environment host layout

Network configuration
~~~~~~~~~~~~~~~~~~~~~

.. TBD

Environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/openstack_user_config.yml`` configuration file
defines which hosts run the containers and services deployed by OSA. For
example, hosts listed in the ``shared-infra_hosts`` section run containers
for many of the shared services that your OpenStack environment requires.
The following is an example of the
``/etc/openstack_deploy/openstack_user_config.yml`` configuration file for a
test environment.

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.aio

