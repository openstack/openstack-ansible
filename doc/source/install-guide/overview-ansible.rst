`Home <index.html>`_ OpenStack-Ansible Installation Guide

Ansible
-------

OpenStack-Ansible Deployment uses a combination of Ansible and
Linux Containers (LXC) to install and manage OpenStack. Ansible
provides an automation platform to simplify system and application
deployment. Ansible manages systems using Secure Shell (SSH)
instead of unique protocols that require remote daemons or agents.

Ansible uses *playbooks* written in the YAML language for orchestration.
For more information, see `Ansible - Intro to
Playbooks <http://docs.ansible.com/playbooks_intro.html>`_.

In this guide, we refer to the host running Ansible playbooks as
the *deployment host* and the hosts on which Ansible installs OSA as the
*target hosts*.

A recommended minimal layout for deployments involves five target
hosts in total: three infrastructure hosts, one compute host, and one
logging host. All hosts require three network interfaces. More
information on setting up target hosts can be found in `the section
called "Host layout" <overview-hostlayout.html>`_.

For more information on physical, logical, and virtual network
interfaces within hosts see `the section called "Host
networking" <overview-hostnetworking.html>`_.

--------------

.. include:: navigation.txt
