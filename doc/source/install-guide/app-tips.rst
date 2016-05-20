`Home <index.html>`__ OpenStack-Ansible Installation Guide

===========================
Appendix D: Tips and tricks
===========================

Ansible forks
~~~~~~~~~~~~~

The default MaxSessions setting for the OpenSSH Daemon is 10. Each Ansible
fork makes use of a Session. By default, Ansible sets the number of forks to
5. However, you can increase the number of forks used in order to improve
deployment performance in large environments.

Note that a number of forks larger than 10 will cause issues for any playbooks
which make use of ``delegate_to`` or ``local_action`` in the tasks. It is
recommended that the number of forks are not raised when executing against the
Control Plane, as this is where delegation is most often used.

The number of forks used may be changed on a permanent basis by including
the appropriate change to the ``ANSIBLE_FORKS`` in your ``.bashrc`` file.
Alternatively it can be changed for a particular playbook execution by using
the ``--forks`` CLI parameter. For example, the following executes the nova
playbook against the control plane with 10 forks, then against the compute
nodes with 50 forks.

.. code-block:: shell-session

    # openstack-ansible --forks 10 os-nova-install.yml --limit compute_containers
    # openstack-ansible --forks 50 os-nova-install.yml --limit compute_hosts

For more information about forks, please see the following references:

* OpenStack-Ansible `Bug 1479812`_
* Ansible `forks`_ entry for ansible.cfg
* `Ansible Performance Tuning`_

.. _Bug 1479812: https://bugs.launchpad.net/openstack-ansible/+bug/1479812
.. _forks: http://docs.ansible.com/ansible/intro_configuration.html#forks
.. _Ansible Performance Tuning: https://www.ansible.com/blog/ansible-performance-tuning

--------------

.. include:: navigation.txt
