`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the ironic service (optional)
-----------------------------------------

.. note::

   This feature is experimental at this time and it has not been fully production
   tested yet. This implementation instructions assume that Ironic is being deployed
   as the sole hypervisor for the region.

.. toctree::

   configure-ironic-deployment.rst
   configure-ironic-neutron.rst
   configure-ironic-images.rst
   configure-ironic-flavor.rst
   configure-ironic-nodes.rst
   configure-ironic-baremetal-node.rst

Ironic is an OpenStack project which provisions bare metal (as opposed to virtual)
machines by leveraging common technologies such as PXE boot and IPMI to cover a wide
range of hardware, while supporting pluggable drivers to allow vendor-specific
functionality to be added.

OpenStack’s Ironic project makes physical servers as easy to provision as
virtual machines in a cloud, which in turn will open up new avenues for enterprises
and service providers.
