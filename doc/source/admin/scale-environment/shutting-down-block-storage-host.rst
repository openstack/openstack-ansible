Shutting down the Block Storage host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a LVM backed Block Storage host needs to be shut down:

#. Disable the ``cinder-volume`` service:

   .. code-block:: console

      # cinder service-list --host CINDER SERVICE NAME INCLUDING @BACKEND
      # cinder service-disable CINDER SERVICE NAME INCLUDING @BACKEND \
      cinder-volume --reason 'RAM maintenance'

#. List all instances with Block Storage volumes attached:

   .. code-block:: console

      # mariadb cinder -BNe 'select instance_uuid from volumes where deleted=0 '\
      'and host like "%<cinder host>%"' | tee /home/user/running_instances

#. Shut down the instances:

   .. code-block:: console

      # cat /home/user/running_instances | xargs -n1 nova stop

#. Verify the instances are shutdown:

   .. code-block:: console

      # cat /home/user/running_instances | xargs -n1 nova show | grep -F vm_state

#. Shut down the Block Storage host:

   .. code-block:: console

      # shutdown -h now

#. Replace the failed hardware and validate the new hardware is functioning.

#. Enable the ``cinder-volume`` service:

   .. code-block:: console

      # cinder service-enable CINDER SERVICE NAME INCLUDING @BACKEND cinder-volume

#. Verify the services on the host are reconnected to the environment:

   .. code-block:: console

      # cinder service-list --host CINDER SERVICE NAME INCLUDING @BACKEND

#. Start your instances and confirm all of the instances are started:

   .. code-block:: console

      # cat /home/user/running_instances | xargs -n1 nova start
      # cat /home/user/running_instances | xargs -n1 nova show | grep -F vm_state
