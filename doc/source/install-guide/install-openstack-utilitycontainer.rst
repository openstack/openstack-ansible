`Home <index.html>`_ OpenStack-Ansible Installation Guide

Utility container
-----------------

The utility container provides a space where miscellaneous tools and
other software can be installed. Tools and objects can be placed in a
utility container if they do not require a dedicated container or if it
is impractical to create a new container for a single tool or object.
Utility containers can also be used when tools cannot be installed
directly onto a host.

For example, the tempest playbooks are installed on the utility
container since tempest testing does not need a container of its own.
For another example of using the utility container, see `the section
called "Verifying OpenStack
operation" <install-openstack-verify.html>`_.

--------------

.. include:: navigation.txt
