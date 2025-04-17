=======================
Messaging configuration
=======================

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


Standard deployment of RabbitMQ server
--------------------------------------

A single RabbitMQ server backend (e.g. server or cluster) is the
default deployment for OpenStack-Ansible (OSA). This broker messaging backend
provides the queue services for both RPC and Notification
communications through its integration with the oslo.messaging rabbit
driver. The `oslo-messaging.yml`_ file provides the default
configuration to associate the oslo.messaging RPC and Notify services
to the RabbitMQ server backend.

.. literalinclude:: ../../../../inventory/group_vars/all/oslo-messaging.yml
   :language: yaml
   :start-after: under the License.

.. _oslo-messaging.yml: https://opendev.org/openstack/openstack-ansible/src/branch/master/inventory/group_vars/all/oslo-messaging.yml


Managing RabbitMQ stream policy
-------------------------------

When deploying RabbitMQ with support for quorum and stream queues, the
retention behaviour for messages changes. Stream queues maintain an append only
log on disk of all messages received until a retention policy indicates they
should be disposed of. By default, this policy is set with a per-stream
`x-max-age` of 1800 seconds. However, as noted in the `RabbitMQ docs`_, this
only comes into effect ones a stream has accumulated enough messages to fill a
segment, which has a default size of 500MB.

If you would like to reduce disk usage, an additional policy can be applied via
OpenStack-Ansible as shown below:

.. literalinclude:: ../../../../inventory/group_vars/all/infra.yml
   :language: yaml
   :start-at: rabbitmq_policies
   :end-before: ## Galera options

Note however, that this policy will only apply if it is in place before any
stream queues are created. If these already exist, they will need to be
manually deleted and re-created by the relevant OpenStack service.

This issue is being tracked in an `oslo.messaging bug`_.

.. _RabbitMQ docs: https://www.rabbitmq.com/docs/streams#retention
.. _oslo.messaging bug: https://bugs.launchpad.net/oslo.messaging/+bug/2089845
