`Home <index.html>`__ OpenStack-Ansible Installation Guide

Using Identity service to Identity service federation
=====================================================

In Identity service (keystone) to Identity service (keystone)
federation (K2K) the identity provider (IdP) and service provider (SP)
keystone instances exchange information securely to enable a user on
the IdP cloud to access resources of the SP cloud.

.. important::

   This section applies only to federation between keystone IdP
   and keystone SP. It does not apply to non-keystone IdP.

.. note::

   For the Kilo release of OpenStack, K2K is only partially supported.
   It is possible to perform a federated login using command line clients and
   scripting. However, horizon does not support this functionality.

The K2K authentication flow involves the following steps:

#. You log in to the IdP with your credentials.
#. You sends a request to the IdP to generate an assertion for a given
   SP. An assertion is a cryptographically signed XML document that identifies
   the user to the SP.
#. You submit the assertion to the SP on the configured ``sp_url``
   endpoint. The Shibboleth service running on the SP receives the assertion
   and verifies it. If it is valid, a session with the client starts and
   returns the session ID in a cookie.
#. You now connect to the SP on the configured ``auth_url`` endpoint,
   providing the Shibboleth cookie with the session ID. The SP responds with
   an unscoped token that you use to access the SP.
#. You connect to the keystone service on the SP with the unscoped
   token, and the desired domain and project, and receive a scoped token
   and the service catalog.
#. You, now in possession of a token, can make API requests to the
   endpoints in the catalog.

Identity service to Identity service federation authentication wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following steps above involve manually sending API requests.

.. note::

   The infrastructure for the command line utilities that performs these steps
   for the user does not exist.

To obtain access to a SP cloud, OpenStack-Ansible provides a script that wraps
the above steps. The script is called ``federated-login.sh`` and is
used as follows:

.. code::

   # ./scripts/federated-login.sh -p project [-d domain] sp_id

* ``project`` is the project in the SP cloud that you want to access.
* ``domain`` is the domain in which the project lives (the default domain is
  used if this argument is not given).
* ``sp_id`` is the unique ID of the SP. This is given in the IdP configuration.

The script outputs the results of all the steps in the authentication flow to
the console. At the end, it prints the available endpoints from the catalog
and the scoped token provided by the SP.

Use the endpoints and token with the openstack command line client as follows:

.. code::

   # openstack --os-token=<token> --os-url=<service-endpoint> [options]

Or, alternatively:

.. code::

   # export OS_TOKEN=<token>
   # export OS_URL=<service-endpoint>
   # openstack [options]

Ensure you select the appropriate endpoint for your operation.
For example, if you want to work with servers, the ``OS_URL``
argument must be set to the compute endpoint.

.. note::

   At this time, the OpenStack client is unable to find endpoints in
   the service catalog when using a federated login.

--------------

.. include:: navigation.txt
