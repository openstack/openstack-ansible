`Home <index.html>`__ OpenStack Ansible Installation Guide

Appendix D. Tips and Tricks
---------------------------

Ansible Forks
~~~~~~~~~~~~~

The default MaxSessions setting for the OpenSSH Daemon is 10. Each Ansible
fork makes use of a Session. By default Ansible sets the number of forks to 5,
but a deployer may wish to increase the number of forks used in order to
improve deployment performance in large environments.

This may be done on a permanent basis by adding the `forks`_ configuration
entry in ``ansible.cfg``, or for a particular playbook execution by using the
``--forks`` CLI parameter. For example, to execute the
``os-keystone-install.yml`` playbook using 10 forks:

.. code-block:: shell-session

    # openstack-ansible --forks 10 os-keystone-install.yml

.. _forks: http://docs.ansible.com/ansible/intro_configuration.html#forks

--------------

.. include:: navigation.txt
