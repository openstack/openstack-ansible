===============
Managing images
===============

.. FROM JP TO ADD:
   I think a far more interesting section for operations is how to handle the
   CHANGES of images. For example, deprecation of images, re-uploading new
   ones... The process is dependant on each company, but at least it would be
   original content, and far more valuable IMO. But it implies research.

An image represents the operating system, software, and any settings
that instances may need depending on the project goals. Create images
first before creating any instances.

Adding images can be done through the Dashboard, or the command line.
Another option available is the ``python-openstackclient`` tool, which
can be installed on the controller node, or on a workstation.

Adding an image using the Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to add an image using the Dashboard, prepare an image binary
file, which must be accessible over HTTP using a valid and direct URL.
Images can be compressed using ``.zip`` or ``.tar.gz``.

 .. note::

    Uploading images using the Dashboard will be available to users
    with administrator privileges. Operators can set user access
    privileges.

#. Log in to the Dashboard.

#. Select the **Admin** tab in the navigation pane and click **images**.

#. Click the **Create Image** button. The **Create an Image** dialog box
   will appear.

#. Enter the details of the image, including the **Image Location**,
   which is where the URL location of the image is required.

#. Click the **Create Image** button. The newly created image may take
   some time before it is completely uploaded since the image arrives in
   an image queue.


Adding an image using the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Log into the controller node directly to add images using the command
line with OpenStack command line clients. Glance commands allow users to
add, manipulate, and manage images.

Alternatively, configure the environment with administrative access to
the controller.

#. Log into the controller node.

#. Run the ``openstack image create`` command, and specify the image name.
   Use the
   ``--file <The Image File>`` variable to specify the image file.

#. Run the ``openstack image set`` command, and specify the image name with the
   ``--name <The Image Name>`` variable.

#. View a list of all the images currently available with ``openstack
   image list``.

#. Run the ``openstack image list`` command to view more details on each image.

 .. list-table:: **glance image details**
    :widths: 33 33 33
    :header-rows: 1

    * - Variable
      - Required
      - Details
    * - ``--name NAME``
      - Optional
      - A name for the image
    * - ``--public [True|False]``
      - Optional
      - If set to ``true``, makes the image available to all users. Permission
        to set this variable is admin only by default.
    * - ``--protected [True|False]``
      - Optional
      - If set to ``true``, this variable prevents an image from being deleted.
    * - ``--container-format CONTAINER_FORMAT``
      - Required
      - The type of container format, one of ``ami``, ``ari``, ``aki``,
        ``bare``, or ``ovf``
    * - ``--disk-format DISK_FORMAT``
      - Required
      - The type of disk format, one of ``ami``, ``ari``, ``aki``, ``vhd``,
        ``vdi``, and ``iso``
    * - ``--owner PROJECT_ID``
      - Optional
      - The tenant who should own the image.
    * - ``--size SIZE``
      - Optional
      - Size of the image data, which is measured in bytes.
    * - ``--min-disk DISK_GB``
      - Optional
      - The minimum size of the disk needed to boot the image being configured,
        which is measured in gigabytes.
    * - ``--min-ram DISK_GB``
      - Optional
      - The minimum amount of RAM needed to boot the image being configured,
        which is measured in megabytes.
    * - ``--location IMAGE_URL``
      - Optional
      - The location where the image data resides. This variables sets the
        location as a URL. If the image data is stored on a swift service,
        specify:  swift://account:<key@example.com>/container/obj.
    * - ``--checksum CHECKSUM``
      - Optional
      - Image data hash used for verification.
    * - ``--copy-from IMAGE_URL``
      - Optional
      - Indicates that the image server should copy data immediately, and store
        it in its configured image store.
    * - ``--property KEY=VALUE``
      - Optional
      - This variable associates an arbitrary property to the image, and can be
        used multiple times.
