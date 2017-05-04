==================
Managing instances
==================

This chapter describes how to create and access instances.

Creating an instance using the Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using an image, create a new instance via the Dashboard options.

#. Log into the Dashboard, and select the **Compute** project from the
   drop down list.

#. Click the **Images** option.

#. Locate the image that will act as the instance base from the
   **Images** table.

#. Click **Launch** from the **Actions** column.

#. Check the **Launch Instances** dialog, and find the **details** tab.
   Enter the appropriate values for the instance.

   #. In the Launch Instance dialog, click the **Access & Security** tab.
      Select the keypair. Set the security group as "default".

   #. Click the **Networking tab**. This tab will be unavailable if
      OpenStack networking (neutron) has not been enabled. If networking
      is enabled, select the networks on which the instance will
      reside.

   #. Click the **Volume Options tab**. This tab will only be available
      if a Block Storage volume exists for the instance. Select
      **Don't boot from a volume** for now.

      For more information on attaching Block Storage volumes to
      instances for persistent storage, see the
      *Managing volumes for persistent storage* section below.

   #. Add customisation scripts, if needed, by clicking the
      **Post-Creation** tab. These run after the instance has been
      created. Some instances support user data, such as root passwords,
      or admin users. Enter the information specific to the instance
      here if required.

   #. Click **Advanced Options**. Specify whether the instance uses a
      configuration drive to store metadata by selecting a disk
      partition type.

#. Click **Launch** to create the instance. The instance will start on a
   compute node. The **Instance** page will open and start creating a
   new instance. The **Instance** page that opens will list the instance
   name, size, status, and task. Power state and public and private IP
   addresses are also listed here.

   The process will take less than a minute to complete. Instance
   creation is complete when the status is listed as active. Refresh the
   page to see the new active instance.

   .. list-table:: **Launching an instance options**
      :widths: 33 33 33
      :header-rows: 1

      * - Field Name
        - Required
        - Details
      * - **Availability Zone**
        - Optional
        - The availability zone in which the image service creates the instance.
          If no availability zones is defined, no instances will be found. The
          cloud provider sets the availability zone to a specific value.
      * - **Instance Name**
        - Required
        - The name of the new instance, which becomes the initial host name of the
          server. If the server name is changed in the API or directly changed,
          the Dashboard names remain unchanged
      * - **Image**
        - Required
        - The type of container format, one of ``ami``, ``ari``, ``aki``,
          ``bare``, or ``ovf``
      * - **Flavor**
        - Required
        - The vCPU, Memory, and Disk configuration. Note that larger flavors can
          take a long time to create. If creating an instance for the first time
          and want something small with which to test, select ``m1.small``.
      * - **Instance Count**
        - Required
        - If creating multiple instances with this configuration, enter an integer
          up to the number permitted by the quota, which is ``10`` by default.
      * - **Instance Boot Source**
        - Required
        - Specify whether the instance will be based on an image or a snapshot. If
          it is the first time creating an instance, there will not yet be any
          snapshots available.
      * - **Image Name**
        - Required
        - The instance will boot from the selected image. This option will be
          pre-populated with the instance selected from the table. However, choose
          ``Boot from Snapshot`` in **Instance Boot Source**, and it will default
          to ``Snapshot`` instead.
      * - **Security Groups**
        - Optional
        - This option assigns security groups to an instance.
          The default security group activates when no customised group is
          specified here. Security Groups, similar to a cloud firewall, define
          which incoming network traffic is forwarded to instances.
      * - **Keypair**
        - Optional
        - Specify a key pair with this option. If the image uses a static key set
          (not recommended), a key pair is not needed.
      * - **Selected Networks**
        - Optional
        - To add a network to an instance, click the **+** in the **Networks
          field**.
      * - **Customisation Script**
        - Optional
        - Specify a customisation script. This script runs after the instance
          launches and becomes active.


Creating an instance using the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the command line, instance creation is managed with the **openstack server
create** command. Before launching an instance, determine what images and
flavors are available to create a new instance using the **openstack image
list** and **openstack flavor list** commands.

#. Log in to any utility container.

#. Issue the **openstack server create** command with a name for the instance,
   along with the name of the image and flavor to use:

   .. code::

      $ openstack server create --image precise-image --flavor=2 --key-name example-key example-instance
      +-------------------------------------+--------------------------------------+
      |               Property              |                Value                 |
      +-------------------------------------+--------------------------------------+
      |          OS-DCF:diskConfig          |                MANUAL                |
      |         OS-EXT-SRV-ATTR:host        |                 None                 |
      | OS-EXT-SRV-ATTR:hypervisor_hostname |                 None                 |
      |    OS-EXT-SRV-ATTR:instance_name    |          instance-0000000d           |
      |        OS-EXT-STS:power_state       |                  0                   |
      |        OS-EXT-STS:task_state        |              scheduling              |
      |         OS-EXT-STS:vm_state         |               building               |
      |              accessIPv4             |                                      |
      |              accessIPv6             |                                      |
      |              adminPass              |             ATSEfRY9fZPx             |
      |             config_drive            |                                      |
      |               created               |         2012-08-02T15:43:46Z         |
      |                flavor               |               m1.small               |
      |                hostId               |                                      |
      |                  id                 | 5bf46a3b-084c-4ce1-b06f-e460e875075b |
      |                image                |             precise-image            |
      |               key_name              |              example-key             |
      |               metadata              |                  {}                  |
      |                 name                |           example-instance           |
      |               progress              |                  0                   |
      |                status               |                BUILD                 |
      |              tenant_id              |   b4769145977045e2a9279c842b09be6a   |
      |               updated               |         2012-08-02T15:43:46Z         |
      |               user_id               |   5f2f2c28bdc844f9845251290b524e80   |
      +-------------------------------------+--------------------------------------+


#. To check that the instance was created successfully, issue the **openstack
   server list** command:

   .. code::

      $ openstack server list
      +------------------+------------------+--------+-------------------+---------------+
      |        ID        |       Name       | Status |      Networks     |   Image Name  |
      +------------------+------------------+--------+-------------------+---------------+
      | [ID truncated]   | example-instance | ACTIVE |  public=192.0.2.0 | precise-image |
      +------------------+------------------+--------+-------------------+---------------+


Managing an instance
~~~~~~~~~~~~~~~~~~~~

#. Log in to the Dashboard. Select one of the projects, and click
   **Instances**.

#. Select an instance from the list of available instances.

#. Check the **Actions** column, and click on the **More** option.
   Select the instance state.

The **Actions** column includes the following options:

-  Resize or rebuild any instance

-  View the instance console log

-  Edit the instance

-  Modify security groups

-  Pause, resume, or suspend the instance

-  Soft or hard reset the instance

 .. note::

    Terminate the instance under the **Actions** column.


Managing volumes for persistent storage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Volumes attach to instances, enabling persistent storage. Volume
storage provides a source of memory for instances. Administrators can
attach volumes to a running instance, or move a volume from one
instance to another.

Live migration
~~~~~~~~~~~~~~
