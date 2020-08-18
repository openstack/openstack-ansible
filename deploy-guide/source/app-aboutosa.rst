.. _app-aboutosa:

=======================
About OpenStack-Ansible
=======================

OpenStack-Ansible (OSA) uses the `Ansible <https://www.ansible.com/how-ansible-works>`_
IT automation engine to deploy an OpenStack environment on Ubuntu, Debian
and CentOS.

For isolation and ease of maintenance, you can install OpenStack components
into machine containers.

The OpenStack-Ansible manifesto
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All the design considerations (the container architecture, the ability to
override any code, the network considerations, etc.) of this project are
listed in our :dev_docs:`architecture reference <reference/architecture/index.html>`.

Why choose OpenStack-Ansible?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Supports the major Linux distributions Ubuntu, CentOS, Debian.
* Supports the major CPU architectures x86, ppc64, s390x (WIP).
* Offers automation for upgrades between major OpenStack releases.
* Uses OpenStack defaults for each of the project roles, and provides
  extra wiring and optimised configuration when combining projects
  together.
* Does not implement its own DSL, and uses wherever possible Ansible
  directly. All the experience acquired using Ansible can be used in
  openstack-ansible, and the other way around.
* You like to use reliable, proven technology. We try to run OpenStack
  with a minimum amount of packages that are not provided by distributions
  or the OpenStack community. Less dependencies and distribution tested
  software make the project more reliable.
* You want to be able to select how to deploy on your hardware: deploy
  partially on metal, fully on metal, or fully in machine containers.

When **not** to choose OpenStack-Ansible?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If your company is already invested with other configuration management
  systems, Puppet or Chef, and does not want to use Ansible we recommend
  re-using your knowledge and experimenting with a different
  OpenStack deployment project.
* You want to deploy OpenStack with 100% application containers.
  We currently support machine containers, with lxc and we will support
  *systemd-nspawn* in the future (WIP). If you want to go 100% Docker,
  there are other projects in the OpenStack community that can
  help you.
