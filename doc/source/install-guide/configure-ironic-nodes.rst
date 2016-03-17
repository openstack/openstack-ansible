`Home <index.html>`_ OpenStack-Ansible Installation Guide

Enroll Ironic nodes
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