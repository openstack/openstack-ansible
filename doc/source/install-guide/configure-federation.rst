`Home <index.html>`__ OpenStack Ansible Installation Guide

Configuring Identity Service federation (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::

   configure-federation-wrapper
   configure-federation-sp-overview.rst
   configure-federation-sp.rst
   configure-federation-idp.rst
   configure-federation-idp-adfs.rst
   configure-federation-mapping.rst
   configure-federation-use-case.rst

In Identity Service federation, the identity provider (IdP) and service
provider (SP) exchange information securely to enable a user on the IdP cloud
to access resources of the SP cloud.

.. note::
   For the Kilo release of OpenStack, federation is only partially supported.
   It is possible to perform a federated login using command line clients and
   scripting, but Dashboard (horizon) does not support this functionality.

The following procedure describes how set up federation.

#. `Configure Identity Service (keystone) service providers. <configure-federation-sp.html>`_

#. Configure the identity provider:

   * `Configure Identity Service (keystone) as an identity provider. <configure-federation-idp.html>`_
   * `Configure Active Directory Federation Services (ADFS) 3.0 as an identity provider. <configure-federation-idp-adfs.html>`_

#. Configure the service provider:

   * `Configure Identity Service (keystone) as a federated service provider. <configure-federation-sp.html>`_
   * `Configure Identity Service (keystone) Domain-Project-Group-Role mappings. <configure-federation-mapping.html>`_

#. `Run the authentication wrapper to use Identity Service to Identity Service federation. <configure-federation-wrapper.html>`_

   For examples of how to set up Identity Service to Identity
   Service federation, see the `Identity Service to Identity Service
   federation example use-case. <configure-federation-use-case.html>`_

--------------

.. include:: navigation.txt


