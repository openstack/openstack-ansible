`Home <index.html>`_ OpenStack-Ansible Installation Guide

Horizon configuration for Cinder
--------------------------------

A deployer can configure variables to set the behavior for Cinder
volume management in Horizon. By default, no Horizon configuration is
set.

#. If multiple availability zones are used and
   ``cinder_default_availability_zone`` is not defined, the default
   destination availability zone is ``nova``. Volume creation with
   Horizon might fail if there is no availability zone named ``nova``.
   Set ``cinder_default_availability_zone`` to an appropriate
   availability zone name so that :guilabel:`Any availability zone`
   works in Horizon.

#. Horizon does not populate the volume type by default. On the new
   volume page, a request for the creation of a volume with the
   default parameters fails. Set ``cinder_default_volume_type`` so
   that a volume creation request without an explicit volume type
   succeeds.

--------------

.. include:: navigation.txt
