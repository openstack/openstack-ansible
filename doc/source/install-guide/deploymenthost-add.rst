`Home <index.html>`_ OpenStack-Ansible Installation Guide

Configuring the operating system
--------------------------------

Install additional software packages and configure NTP.

#. Install additional software packages if not already installed during
   operating system installation:

   .. code-block:: shell-session

       # apt-get install aptitude build-essential git ntp ntpdate \
         openssh-server python-dev sudo

#. Configure NTP to synchronize with a suitable time source.

--------------

.. include:: navigation.txt
