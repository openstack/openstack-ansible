====================
Distribution support
====================

.. _supported-distros:

Supported distributions
=======================

The list of supported distributions can be found in the
:deploy_guide:`Deployment Guide <deploymenthost.html>`

Minimum requirements for OpenStack-Ansible roles
================================================

Existing and new distributions are expected to meet the following requirements
in order for them to be accepted in the individual OpenStack-Ansible roles:

* Pass functional tests

Graduation
==========

For a distribution to be considered supported by the OpenStack-Ansible
project, it has to meet the following minimum requirements:

* The necessary steps for bootstrapping the operating system have to be
  documented in the :deploy_guide:`Deployment Guide <index.html>`.
* The integration repository contains at least one job which passes the
  Temptest testing framework.

Voting
======

Distributions can be promoted to voting jobs on individual roles once they move
to the `Graduation` phase and their stability has been confirmed by the core
OpenStack-Ansible developers. Similar to this, voting can also be enabled in
the integration repository for all the scenarios or a specific one.
