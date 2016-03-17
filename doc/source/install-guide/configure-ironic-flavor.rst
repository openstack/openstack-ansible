`Home <index.html>`_ OpenStack-Ansible Installation Guide

Creating an Ironic flavor
-------------------------

#. Create a new flavor called ``my-baremetal-flavor``.

   .. note::

      The following example sets the CPU architecture for the newly created
      flavor to be `x86_64`.

   .. code-block:: bash

      nova flavor-create ${FLAVOR_NAME} ${FLAVOR_ID} ${FLAVOR_RAM} ${FLAVOR_DISK} ${FLAVOR_CPU}
      nova flavor-key ${FLAVOR_NAME} set cpu_arch=x86_64
      nova flavor-key ${FLAVOR_NAME} set capabilities:boot_option="local"

.. note::

   The flavor and nodes should match when enrolling into Ironic.
   See the documentation on flavors for more information:
   http://docs.openstack.org/openstack-ops/content/flavors.html

After successfully deploying the ironic node on subsequent boots, the instance
will boot from your local disk as first preference. This will speed up the deployed
node's boot time. The alternative, if this is not set, will mean the ironic node will
attempt to PXE boot first, which will allow for operator-initiated image updates and
other operations. The operational reasoning and building an environment to support this
use case is not covered here.