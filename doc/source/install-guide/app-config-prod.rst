.. _production-environment-config:

========================================================
Appendix B: Example production environment configuration
========================================================

Introduction
~~~~~~~~~~~~

The production environment is a minimal set of components to deploy a working
OpenStack-Ansible environment for production purposes.

The environment has the following characteristics:

* 3 control plane hosts
* 2 compute hosts
* 1 storage host
* 1 log aggregation host
* 2 network agent hosts
* Each host multiple Network Interface Cards (NIC) configured as
  bonded pairs.
* The full compute kit will be installed with Telemetry (ceilometer) included,
  with NFS configured as a storage back-end for nova, glance, and
  cinder.

.. image:: figures/arch-layout-production.png
   :width: 100%

Network configuration
~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../etc/network/interfaces.d/openstack_interface.cfg.example

Environment configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``/etc/openstack_deploy/openstack_user_config.yml`` configuration file
sets the hosts available in the groups. This designates the services that
runs on them.

.. literalinclude:: ../../../etc/openstack_deploy/openstack_user_config.yml.example
   :start-after: # limitations under the License.

