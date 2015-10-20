`Home <index.html>`__ OpenStack Ansible Installation Guide

Using Identity Service to Identity Service federation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Identity Service (keystone) to Identity Service (keystone)
federation (K2K) the identity provider (IdP) and service provider (SP)
keystone instances exchange information securely to enable a user on
the IdP cloud to access resources of the SP cloud.

This section applies only to federation between Identity Service IdP
and Identity Service SP. It does not apply to non-keystone IdP.

.. note::
   For the Kilo release of OpenStack, K2K is only partially supported.
   It is possible to perform a federated login using command line clients and
   scripting, but Horizon does not support this functionality.

The K2K authentication flow involves the following steps:

#. The client logs in to the IdP with his credentials.
#. The client sends a request to the IdP to generate an assertion for a given
   SP. An assertion is a cryptographically signed XML document that identifies
   the user to the SP.
#. The client submits the assertion to the SP on the configured ``sp_url``
   endpoint. The Shibboleth service running on the SP receives the assertion
   and verifies it. If it is valid, it starts a session with the client and
   returns the session ID in a cookie.
#. The client now connects to the SP on the configured ``auth_url`` endpoint,
   providing the Shibboleth cookie with the session ID. The SP responds with
   an unscoped token that the client can use to access the SP.
#. The client connects to the keystone service on the SP with the unscoped
   token, and the desired domain and/or project, and receives a scoped token
   and the service catalog.
#. The client, now in possession of a token, can make API requests to the
   endpoints in the catalog.

Identity Service to Identity Service federation authentication wrapper
----------------------------------------------------------------------

Unfortunately, many of the steps above involve manually sending API requests.
The infrastructure for the command line utilities to perform all these steps
for the user does not yet exist.

To simplify the task of obtaining access to a SP cloud, OpenStack Ansible provides a script that wraps the above steps. The script is called ``federated-login.sh`` and is
used as follows::

    # ./scripts/federated-login.sh -p project [-d domain] sp_id

Where ``project`` is the project in the SP cloud that the user wants to access,
``domain`` is the domain in which the project lives (the default domain is
used if this argument is not given) and ``sp_id`` is the unique ID of the SP,
as given in the IdP configuration.

The script outputs the results of all the steps in the authentication flow to
the console, and at the end prints the available endpoints from the catalog
and the scoped token provided by the SP.

The endpoints and token can be used with the openstack command line client as
follows::

    # openstack --os-token=<token> --os-url=<service-endpoint> [options]

or alternatively::

    # export OS_TOKEN=<token>
    # export OS_URL=<service-endpoint>
    # openstack [options]

The user must select the appropriate endpoint for the desired
operation. For example, if the user wants to work with servers, the ``OS_URL``
argument must be set to the compute endpoint. At this time the openstack
client is unable to find endpoints in the service catalog when using a
federated login. This is likely to be supported in the near future.

--------------

.. include:: navigation.txt
