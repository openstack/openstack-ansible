`Home <index.html>`_ OpenStack-Ansible Installation Guide

Galera cluster recovery
-----------------------

When one or all nodes fail within a galera cluster you may need to
re-bootstrap the environment. To make take advantage of the
automation Ansible provides simply execute the ``galera-install.yml``
play using the **galera-bootstrap** to auto recover a node or an
entire environment.

#. Run the following Ansible command to show the failed nodes:

   .. code-block:: shell-session

       # openstack-ansible galera-install --tags galera-bootstrap


Upon completion of this command the cluster should be back online an in
a functional state.


--------------

.. include:: navigation.txt
