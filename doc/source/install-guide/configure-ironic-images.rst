`Home <index.html>`_ OpenStack-Ansible Installation Guide

Building Ironic images
----------------------

Images using the ``diskimage-builder`` must be built outside of a container.
For this process, use one of the physical hosts within the environment.

#. Install the necessary packages:

   .. code-block:: bash

      apt-get install -y qemu uuid-runtime curl

#. Install the ``disk-imagebuilder`` client:

   .. code-block:: bash

      pip install diskimage-builder --isolated

   .. important::

      Only use the ``--isolated`` flag if you are building on a node that
      has already been deployed by OpenStack-Ansible as pip will not
      allow the external package to be resolved.

#. Optional: Force the ubuntu ``image-create`` process to use a modern kernel:

   .. code-block:: bash

      echo 'linux-image-generic-lts-xenial:' > /usr/local/share/diskimage-builder/elements/ubuntu/package-installs.yaml

#. Create Ubuntu ``initramfs``:

   .. code-block:: bash

      disk-image-create ironic-agent ubuntu -o ${IMAGE_NAME}

#. Upload the created deploy images into the Image Service:

   .. code-block:: bash

      # Upload the deploy image kernel
      glance image-create --name ${IMAGE_NAME}.kernel --visibility public --disk-format aki --container-format aki < ${IMAGE_NAME}.kernel

      # Upload the user image initramfs
      glance image-create --name ${IMAGE_NAME}.initramfs --visibility public --disk-format ari --container-format ari < ${IMAGE_NAME}.initramfs

#. Create Ubuntu user image:

   .. code-block:: bash

      disk-image-create ubuntu baremetal localboot local-config dhcp-all-interfaces grub2 -o ${IMAGE_NAME}

#. Upload the created user images into the Image Service:

   .. code-block:: bash

      # Upload the user image vmlinuz and store uuid
      VMLINUZ_UUID="$(glance image-create --name ${IMAGE_NAME}.vmlinuz --visibility public --disk-format aki --container-format aki  < ${IMAGE_NAME}.vmlinuz | awk '/\| id/ {print $4}')"

      # Upload the user image initrd and store uuid
      INITRD_UUID="$(glance image-create --name ${IMAGE_NAME}.initrd --visibility public --disk-format ari --container-format ari  < ${IMAGE_NAME}.initrd | awk '/\| id/ {print $4}')"

      # Create image
      glance image-create --name ${IMAGE_NAME} --visibility public --disk-format qcow2 --container-format bare --property kernel_id=${VMLINUZ_UUID} --property ramdisk_id=${INITRD_UUID} < ${IMAGE_NAME}.qcow2
