`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring Secure Shell (SSH) keys
-----------------------------------

Ansible uses Secure Shell (SSH) with public key authentication for
connectivity between the deployment and target hosts. To reduce user
interaction during Ansible operations, key pairs should not include
passphrases. However, if a passphrase is required, consider using the
**ssh-agent** and **ssh-add** commands to temporarily store the
passphrase before performing Ansible operations.

--------------

.. include:: navigation.txt
