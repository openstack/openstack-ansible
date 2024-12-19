========================
Hybrid messaging example
========================

This section provides an overview of hybrid messaging deployment
concepts and describes the necessary steps for a working
OpenStack-Ansible (OSA) deployment where RPC and Notify communications
are separated and integrated with different messaging server backends.

oslo.messaging library
----------------------

The oslo.messaging library is part of the OpenStack Oslo project that
provides intra-service messaging capabilities. The library supports
two communication patterns (RPC and Notify) and provides an abstraction
that hides the details of the messaging bus operation from the OpenStack
services.

Notifications
+++++++++++++

Notify communications are an asynchronous exchange from notifier to
listener. The messages transferred typically correspond to
information updates or event occurrences that are published by an
OpenStack service. The listener need not be present when the
notification is sent as notify communications are temporally
decoupled. This decoupling between notifier and listener requires that
the messaging backend deployed for notifications provide message
persistence such as a broker queue or log store. It is noteworthy that
the message transfer is unidirectional from notifier to listener and
there is no message flow back to the notifier.

RPC
+++

The RPC is intended as a synchronous exchange between a client and
server that is temporally bracketed. The information transferred
typically corresponds to a request-response pattern for service
command invocation. If the server is not present at the time the
command is invoked, the call should fail. The temporal coupling
requires that the messaging backend deployed support the
bi-directional transfer of the request from caller to server and the
associated reply sent from the server back to the caller. This
requirement can be satisfied by a broker queue or a direct messaging
backend server.

Messaging transport
+++++++++++++++++++

The oslo.messaging library supports a messaging
`transport plugin`_ capability such that RPC and Notify communications
can be separated and different messaging backend servers can be deployed.

.. _transport plugin: https://docs.openstack.org/oslo.messaging/latest/reference/transport.html

The oslo.messaging drivers provide the transport integration for the
selected protocol and backend server. The following table summarizes
the supported oslo.messaging drivers and the communication services they
support.

.. code-block:: text

   +----------------+-----------+-----------+-----+--------+-----------+
   | Oslo.Messaging | Transport |  Backend  | RPC | Notify | Messaging |
   |     Driver     | Protocol  |  Server   |     |        |   Type    |
   +================+===========+===========+=====+========+===========+
   |     rabbit     | AMQP V0.9 | rabbitmq  | yes |   yes  |   queue   |
   +----------------+-----------+-----------+-----+--------+-----------+
   |     kafka      |  kafka    |  kafka    |     |   yes  |   queue   |
   | (experimental) |  binary   |           |     |        |  (stream) |
   +----------------+-----------+-----------+-----+--------+-----------+


Standard deployment of rabbitmq server
--------------------------------------

A single rabbitmq server backend (e.g. server or cluster) is the
default deployment for OSA. This broker messaging backend
provides the queue services for both RPC and Notification
communications through its integration with the oslo.messaging rabbit
driver. The `oslo-messaging.yml`_ file provides the default
configuration to associate the oslo.messaging RPC and Notify services
to the rabbitmq server backend.

.. literalinclude:: ../../../../inventory/group_vars/all/oslo-messaging.yml
   :language: yaml
   :start-after: under the License.

.. _oslo-messaging.yml: https://github.com/openstack/openstack-ansible/blob/master/inventory/group_vars/all/oslo-messaging.yml
