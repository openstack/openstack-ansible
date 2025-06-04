Managing images
===============

.. FROM JP TO ADD:
   I think a far more interesting section for operations is how to handle the
   CHANGES of images. For example, deprecation of images, re-uploading new
   ones... The process is dependent on each company, but at least it would be
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

#. Select the :guilabel:`Admin` tab in the navigation pane and click :guilabel:`Images`.

#. Click the :guilabel:`Create Image` button. The **Create an Image** dialog box
   will appear.

#. Enter the details of the image, including the **Image Location**,
   which is where the URL location of the image is required.

#. Click the :guilabel:`Create Image` button. The newly created image may take
   some time before it is completely uploaded since the image arrives in
   an image queue.


Adding an image using the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The utility container provides a CLI environment for additional
configuration and management.

#. Access the utility container:

   .. code::

      $ lxc-attach -n `lxc-ls -1 | grep utility | head -n 1`

Use the OpenStack client within the utility container to manage all glance images.
`See the OpenStack client official documentation on managing images
<https://docs.openstack.org/image-guide/create-images-manually.html>`_.

