`Home <index.html>`_ OpenStack-Ansible Installation Guide

Cached Ansible facts issues
---------------------------

At the beginning of a playbook run, information about each host, such as its
Linux distribution, kernel version, and network interfaces, is gathered. To
improve performance, particularly in larger deployments, these facts can be
cached.

OpenStack-Ansible enables fact caching by default.

`Fact Caching`_ can be disabled or reconfigured through options in ``ansible.cfg``.

.. _Fact Caching: http://docs.ansible.com/ansible/playbooks_variables.html#fact-caching

Forcing regeneration of cached facts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a host's kernel is upgraded or additional network interfaces or bridges are
created on the host, its cached facts may be incorrect. This can lead to
unexpected errors while running playbooks, and require that the cached facts be
regenerated.

Run the following command to remove currently cached facts:

.. code-block:: shell-session

   # rm /etc/openstack_deploy/ansible_facts/*

New facts will be gathered and cached during the next playbook run.

--------------

.. include:: navigation.txt
