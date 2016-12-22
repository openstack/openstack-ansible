=======
Backups
=======

This is a draft backups page for the proposed OpenStack-Ansible
operations guide.

Checking for recent back ups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before adding new nodes to your OpenStack-Ansible environment, it is possible
to confirm that a recent back up resides inside the ``holland_backups``
repository:

#. Log in to the Infra host where the Galera service creates backups.

#. Run the :command:``ls -ls`` command to view the contents of the
   back up files:

   .. code::

      <node-ID>-Infra01~#: ls -ls /openstack/backup/XXXX_galera_containe

Backup of /etc/openstack_deploy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Details about our inventory backup we are already doing, but also more
content can go there on how to backup and restore this.

Backup of Galera data
~~~~~~~~~~~~~~~~~~~~~

Backup your environment
~~~~~~~~~~~~~~~~~~~~~~~

Backup procedure
----------------
