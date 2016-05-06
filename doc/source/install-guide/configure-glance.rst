`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the Image (glance) service
======================================

In an all-in-one deployment with a single infrastructure node, the Image
(glance) service uses the local file system on the target host to store images.
When deploying production clouds, we recommend backing glance with a
swift backend or some form of shared storage.

Configuring default and additional stores
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenStack-Ansible provides two configurations for controlling where glance stores
files: the default store and additional stores. glance stores images in file-based
storage by default. Two additional stores, ``http`` and ``cinder`` (Block Storage),
are also enabled by default.

You can choose alternative default stores and alternative additional stores.
For example, a deployer that uses Ceph may configure the following Ansible
variables:

.. code-block:: yaml

    glance_default_store = rbd
    glance_additional_stores:
      - swift
      - http
      - cinder

The configuration above configures glance to use ``rbd`` (Ceph) by
default, but ``glance_additional_stores`` list enables ``swift``,
``http`` and ``cinder`` stores in the glance
configuration files.

The following example sets glance to use the ``images`` pool.
This example uses cephx authentication and requires an existing ``glance``
account for the ``images`` pool.


In ``user_variables.yml``:

   .. code-block:: yaml

    glance_default_store: rbd
    ceph_mons:
      - 172.29.244.151
      - 172.29.244.152
      - 172.29.244.153


You can use the following variables if you are not using the defaults:

    .. code-block:: yaml

     glance_ceph_client: <glance-username>
     glance_rbd_store_pool: <glance-pool-name>
     glance_rbd_store_chunk_size: <chunk-size>


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

#. Set the swift account credentials:

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
   used for storing images. If the container does not exist, it is
   automatically created.

#. Define the store region:

   .. code-block:: yaml

       glance_swift_store_region: STORE_REGION

   Replace ``STORE_REGION`` if needed.

#. (Optional) Set the paste deploy flavor:

   .. code-block:: yaml

       glance_flavor: GLANCE_FLAVOR

   By default, glance uses caching and authenticates with the
   Identity (keystone) service. The default maximum size of the image cache is 10GB.
   The default glance container size is 12GB. In some
   configurations, glance attempts to cache an image
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

Special considerations
~~~~~~~~~~~~~~~~~~~~~~

If the swift password or key contains a dollar sign (``$``), it must
be escaped with an additional dollar sign (``$$``). For example, a password of
``super$ecure`` would need to be entered as ``super$$ecure``.  This is necessary
due to the way `oslo.config formats strings`_.

.. _oslo.config formats strings: https://bugs.launchpad.net/oslo-incubator/+bug/1259729

--------------

.. include:: navigation.txt
