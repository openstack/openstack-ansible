`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Image Service
-----------------------------

In an all-in-one deployment with a single infrastructure node, the Image
Service uses the local file system on the target host to store images.
When deploying production clouds we recommend backing Glance with a
swift backend or some form or another of shared storage.

Configuring default and additional stores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible provides two configurations for controlling where the Image
Service stores files: the default store and additional stores.  As mentioned
in the previous section, the Image Service stores images in file-based storage
by default.  Two additional stores, http and cinder, are also enabled by
default.

Deployers can choose alternative default stores, as shown in the swift example
in the next section, and deployers can choose alternative additional stores.
For example, a deployer that uses Ceph may configure the following Ansible
variables:

.. code-block:: yaml

    glance_default_store = rbd
    glance_additional_stores:
      - swift
      - http
      - cinder

The configuration above will configure the Image Service to use rbd (Ceph) by
default, but the swift, http and cinder stores will also be enabled in the
Image Service configuration files.

Storing images in Cloud Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following procedure describes how to modify the
``/etc/openstack_deploy/user_variables.yml`` file to enable Cloud Files
usage.

#. Change the default store to use Object Storage (swift), the
   underlying architecture of Cloud Files:

   .. code-block:: yaml

       glance_default_store: swift

#. Set the appropriate authentication URL and version:

   .. code-block:: yaml

       glance_swift_store_auth_version: 2
       glance_swift_store_auth_address: https://127.0.0.1/v2.0

#. Set the swift account credentials (see *Special Considerations* at the
   bottom of this page):

   .. code-block:: yaml

       # Replace this capitalized variables with actual data.
       glance_swift_store_user: GLANCE_SWIFT_TENANT:GLANCE_SWIFT_USER
       glance_swift_store_key: SWIFT_PASSWORD_OR_KEY

#. Change the ``glance_swift_store_endpoint_type`` from the default
   ``internalURL`` settings to ``publicURL`` if needed.

   .. code-block:: yaml

       glance_swift_store_endpoint_type: publicURL

#. Define the store name:

   .. code-block:: yaml

       glance_swift_store_container: STORE_NAME

   Replace ``STORE_NAME`` with the container name in swift to be
   used for storing images. If the container doesn't exist, it will be
   automatically created.

#. Define the store region:

   .. code-block:: yaml

       glance_swift_store_region: STORE_REGION

   Replace ``STORE_REGION`` if needed.

#. (Optional) Set the paste deploy flavor:

   .. code-block:: yaml

       glance_flavor: GLANCE_FLAVOR

   By default, the Image Service uses caching and authenticates with the
   Identity service. The default maximum size of the image cache is 10
   GB. The default Image Service container size is 12 GB. In some
   configurations, the Image Service might attempt to cache an image
   which exceeds the available disk space. If necessary, you can disable
   caching. For example, to use Identity without caching, replace
   ``GLANCE_FLAVOR`` with ``keystone``:

   .. code-block:: yaml

       glance_flavor: keystone

   Or, to disable both authentication and caching, set
   ``GLANCE_FLAVOR`` to no value:

   .. code-block:: yaml

       glance_flavor:

   This option is set by default to use authentication and cache
   management in the ``playbooks/roles/os_glance/defaults/main.yml``
   file. To override the default behavior, set ``glance_flavor`` to a
   different value in ``/etc/openstack_deploy/user_variables.yml``.

   The possible values for ``GLANCE_FLAVOR`` are:

   -  (Nothing)

   -  ``caching``

   -  ``cachemanagement``

   -  ``keystone``

   -  ``keystone+caching``

   -  ``keystone+cachemanagement`` (default)

   -  ``trusted-auth``

   -  ``trusted-auth+cachemanagement``

Special Considerations
~~~~~~~~~~~~~~~~~~~~~~

If the swift password or key contains a dollar sign (``$``), it must
be escaped with an additional dollar sign (``$$``). For example, a password of
``super$ecure`` would need to be entered as ``super$$ecure``.  This is needed
due to the way `oslo.config formats strings`_.

.. _oslo.config formats strings: https://bugs.launchpad.net/oslo-incubator/+bug/1259729

--------------

.. include:: navigation.txt
