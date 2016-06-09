`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Bare Metal (ironic) service (optional)
======================================================

.. note::

   This feature is experimental at this time and it has not been fully production
   tested yet. These implementation instructions assume that ironic is being deployed
   as the sole hypervisor for the region.

Ironic is an OpenStack project which provisions bare metal (as opposed to virtual)
machines by leveraging common technologies such as PXE boot and IPMI to cover a wide
range of hardware, while supporting pluggable drivers to allow vendor-specific
functionality to be added.

OpenStack’s ironic project makes physical servers as easy to provision as
virtual machines in a cloud.

OpenStack-Ansible deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Modify the environment files and force ``nova-compute`` to run from
   within a container:

   .. code-block:: bash

      sed -i '/is_metal.*/d' /etc/openstack_deploy/env.d/nova.yml

Setup a neutron network for use by ironic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a general case, neutron networking can be a simple flat network. However,
in a complex case, this can be whatever you need and want. Ensure
you adjust the deployment accordingly. The following is an example:


.. code-block:: bash

    neutron net-create cleaning-net --shared \
                                    --provider:network_type flat \
                                    --provider:physical_network ironic-net

    neutron subnet-create ironic-net 172.19.0.0/22 --name ironic-subnet
                          --ip-version=4 \
                          --allocation-pool start=172.19.1.100,end=172.19.1.200 \
                          --enable-dhcp \
                          --dns-nameservers list=true 8.8.4.4 8.8.8.8

Building ironic images
~~~~~~~~~~~~~~~~~~~~~~

Images using the ``diskimage-builder`` must be built outside of a container.
For this process, use one of the physical hosts within the environment.

#. Install the necessary packages:

   .. code-block:: bash

      apt-get install -y qemu uuid-runtime curl

#. Install the ``disk-imagebuilder`` package:

   .. code-block:: bash

      pip install diskimage-builder --isolated

   .. important::

      Only use the ``--isolated`` flag if you are building on a node
      deployed by OpenStack-Ansible, otherwise pip will not
      resolve the external package.

#. Optional: Force the ubuntu ``image-create`` process to use a modern kernel:

   .. code-block:: bash

      echo 'linux-image-generic-lts-xenial:' > \
      /usr/local/share/diskimage-builder/elements/ubuntu/package-installs.yaml

#. Create Ubuntu ``initramfs``:

   .. code-block:: bash

      disk-image-create ironic-agent ubuntu -o ${IMAGE_NAME}

#. Upload the created deploy images into the Image (glance) Service:

   .. code-block:: bash

      # Upload the deploy image kernel
      glance image-create --name ${IMAGE_NAME}.kernel --visibility public \
       --disk-format aki --container-format aki < ${IMAGE_NAME}.kernel

      # Upload the user image initramfs
      glance image-create --name ${IMAGE_NAME}.initramfs --visibility public \
       --disk-format ari --container-format ari < ${IMAGE_NAME}.initramfs

#. Create Ubuntu user image:

   .. code-block:: bash

      disk-image-create ubuntu baremetal localboot local-config dhcp-all-interfaces grub2 -o ${IMAGE_NAME}

#. Upload the created user images into the Image (glance) Service:

   .. code-block:: bash

      # Upload the user image vmlinuz and store uuid
      VMLINUZ_UUID="$(glance image-create --name ${IMAGE_NAME}.vmlinuz --visibility public --disk-format aki --container-format aki  < ${IMAGE_NAME}.vmlinuz | awk '/\| id/ {print $4}')"

      # Upload the user image initrd and store uuid
      INITRD_UUID="$(glance image-create --name ${IMAGE_NAME}.initrd --visibility public --disk-format ari --container-format ari  < ${IMAGE_NAME}.initrd | awk '/\| id/ {print $4}')"

      # Create image
      glance image-create --name ${IMAGE_NAME} --visibility public --disk-format qcow2 --container-format bare --property kernel_id=${VMLINUZ_UUID} --property ramdisk_id=${INITRD_UUID} < ${IMAGE_NAME}.qcow2


Creating an ironic flavor
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Create a new flavor called ``my-baremetal-flavor``.

   .. note::

      The following example sets the CPU architecture for the newly created
      flavor to be `x86_64`.

   .. code-block:: bash

      nova flavor-create ${FLAVOR_NAME} ${FLAVOR_ID} ${FLAVOR_RAM} ${FLAVOR_DISK} ${FLAVOR_CPU}
      nova flavor-key ${FLAVOR_NAME} set cpu_arch=x86_64
      nova flavor-key ${FLAVOR_NAME} set capabilities:boot_option="local"

.. note::

   Ensure the flavor and nodes match when enrolling into ironic.
   See the documentation on flavors for more information:
   http://docs.openstack.org/openstack-ops/content/flavors.html

After successfully deploying the ironic node on subsequent boots, the instance
boots from your local disk as first preference. This speeds up the deployed
node's boot time. Alternatively, if this is not set, the ironic node PXE boots first and
allows for operator-initiated image updates and other operations.

.. note::

   The operational reasoning and building an environment to support this
   use case is not covered here.

Enroll ironic nodes
-------------------

#. From the utility container, enroll a new baremetal node by executing the following:

   .. code-block:: bash

      # Source credentials
      . ~/openrc

      # Create the node
      NODE_HOSTNAME="myfirstnodename"
      IPMI_ADDRESS="10.1.2.3"
      IPMI_USER="my-ipmi-user"
      IPMI_PASSWORD="my-ipmi-password"
      KERNEL_IMAGE=$(glance image-list | awk "/${IMAGE_NAME}.kernel/ {print \$2}")
      INITRAMFS_IMAGE=$(glance image-list | awk "/${IMAGE_NAME}.initramfs/ {print \$2}")
      ironic node-create \
            -d agent_ipmitool \
            -i ipmi_address="${IPMI_ADDRESS}" \
            -i ipmi_username="${IPMI_USER}" \
            -i ipmi_password="${IPMI_PASSWORD}" \
            -i deploy_ramdisk="${INITRAMFS_IMAGE}" \
            -i deploy_kernel="${KERNEL_IMAGE}" \
            -n ${NODE_HOSTNAME}

      # Create a port for the node
      NODE_MACADDRESS="aa:bb:cc:dd:ee:ff"
      ironic port-create \
            -n $(ironic node-list | awk "/${NODE_HOSTNAME}/ {print \$2}") \
            -a ${NODE_MACADDRESS}

      # Associate an image to the node
      ROOT_DISK_SIZE_GB=40
      ironic node-update $(ironic node-list | awk "/${IMAGE_NAME}/ {print \$2}") add \
          driver_info/deploy_kernel=$KERNEL_IMAGE \
          driver_info/deploy_ramdisk=$INITRAMFS_IMAGE \
          instance_info/deploy_kernel=$KERNEL_IMAGE \
          instance_info/deploy_ramdisk=$INITRAMFS_IMAGE \
          instance_info/root_gb=${ROOT_DISK_SIZE_GB}

      # Add node properties
      # The property values used here should match the hardware used
      ironic node-update $(ironic node-list | awk "/${NODE_HOSTNAME}/ {print \$2}") add \
          properties/cpus=48 \
          properties/memory_mb=254802 \
          properties/local_gb=80 \
          properties/size=3600 \
          properties/cpu_arch=x86_64 \
          properties/capabilities=memory_mb:254802,local_gb:80,cpu_arch:x86_64,cpus:48,boot_option:local

Deploy a baremetal node kicked with ironic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important::

   You will not have access unless you have a key set within nova before
   your ironic deployment. If you do not have an ssh key readily
   available, set one up with ``ssh-keygen``.

.. code-block:: bash

    nova keypair-add --pub-key ~/.ssh/id_rsa.pub admin

Now boot a node:

.. code-block:: bash

   nova boot --flavor ${FLAVOR_NAME} --image ${IMAGE_NAME} --key-name admin ${NODE_NAME}

