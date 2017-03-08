============================
RabbitMQ cluster maintenance
============================

This is a draft RabbitMQ cluster maintenance page for the proposed
OpenStack-Ansible operations guide.


.. note::

   There is currently an Ansible bug in regards to ``HOSTNAME``. If
   the host ``.bashrc`` holds a var named ``HOSTNAME``, the container where the
   ``lxc_container`` module attaches will inherit this var and potentially
   set the wrong ``$HOSTNAME``. See
   `the Ansible fix <https://github.com/ansible/ansible/pull/22246>`_ which will
   be released in Ansible version 2.3.

Create a RabbitMQ cluster
~~~~~~~~~~~~~~~~~~~~~~~~~

Check the RabbitMQ cluster status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stop and restart a RabbitMQ cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RabbitMQ and mnesia
~~~~~~~~~~~~~~~~~~~

Repair a partitioned RabbitMQ cluster for a single-node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Repair a partitioned RabbitMQ cluster for a multi-node cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
