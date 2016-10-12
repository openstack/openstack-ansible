.. _production-environment-config:

========================================================
Appendix B: Example production environment configuration
========================================================

Introduction
~~~~~~~~~~~~

A production environment contains the minimal set of components needed to
deploy a working OpenStack-Ansible (OSA) environment for production purposes.

A production environment has the following characteristics:

* Three infrastructure (control plane) hosts
* Two compute hosts
* One storage host
* One log aggregation host
* Two network agent hosts
* Multiple Network Interface Cards (NIC) configured as bonded pairs for each
  host
* Full compute kit with the Telemetry service (ceilometer) included,
  with NFS configured as a storage back end for the Compute (nova), Image
  (glance), and Block Storage (cinder) services

.. image:: figures/arch-layout-production.png
   :width: 100%

Network configuration
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../etc/network/interfaces.d/openstack_interface.cfg.prod.example

Environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/openstack_user_config.yml`` configuration file
defines which hosts run the containers and services deployed by OSA. For
example, hosts listed in the ``shared-infra_hosts`` section run containers
for many of the shared services that your OpenStack environment requires.
Following is an example of the
``/etc/openstack_deploy/openstack_user_config.yml`` configuration file for a
production environment.

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.example
   :start-after: # limitations under the License.

