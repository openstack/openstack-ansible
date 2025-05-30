Shutting down the Compute host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a Compute host needs to be shut down:

#. Disable the ``nova-compute`` binary:

   .. code-block:: console

      # nova service-disable --reason "Hardware replacement" HOSTNAME nova-compute

#. List all running instances on the Compute host:

   .. code-block:: console

      # nova list --all-t --host <compute_name> | awk '/ACTIVE/ {print $2}' > \
      /home/user/running_instances && for i in `cat /home/user/running_instances`; do nova stop $i ; done

#. Use SSH to connect to the Compute host.

#. Confirm all instances are down:

   .. code-block:: console

      # virsh list --all

#. Shut down the Compute host:

   .. code-block:: console

      # shutdown -h now

#. Once the Compute host comes back online, confirm everything is in
   working order and start the instances on the host. For example:

   .. code-block:: console

      # cat /home/user/running_instances
      # do nova start $instance
        done

#. Enable the ``nova-compute`` service in the environment:

   .. code-block:: console

      # nova service-enable HOSTNAME nova-compute
