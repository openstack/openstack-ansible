`Home <index.html>`__ OpenStack Ansible Installation Guide

Configure Active Directory Federation Services (ADFS) 3.0 as an identity provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install ADFS:

* `Prerequisites for ADFS from Microsoft Technet <https://technet.microsoft.com/library/bf7f9cf4-6170-40e8-83dd-e636cb4f9ecb>`_
* `ADFS installation procedure from Microsoft Technet <https://technet.microsoft.com/en-us/library/dn303423>`_

Configuring ADFS
----------------

#. The ADFS Server must already trust the service provider's (SP) keystone
   certificate. It is recommended to have the ADFS CA (or a
   public CA) sign a certificate request for the keystone service.
#. In the ADFS Management Console, choose ``Add Relying Party Trust``.
#. Select ``Import data about the relying party published online or on a
   local network`` and enter the URL for the SP Metadata (
   for example, ``https://<SP_IP_ADDRESS or DNS_NAME>:5000/Shibboleth.sso/Metadata``)

   .. note::
      ADFS may give a warning message that some of the content gathered from metadata
      was skipped because is not supported by ADFS.

#. Continuing the wizard, select ``Permit all users to access this
   relying party``.
#. In the ``Add Transform Claim Rule Wizard``, select ``Pass Through or
   Filter an Incoming Claim``.
#. Name the rule (for example, ``Pass Through UPN``) and select the ``UPN``
   Incoming claim type.
#. Click :guilabel:`OK` to apply the rule and finalize the setup.

References
----------
* http://blogs.technet.com/b/rmilne/archive/2014/04/28/how-to-install-adfs-2012-r2-for-office-365.aspx
* http://blog.kloud.com.au/2013/08/14/powershell-deployment-of-web-application-proxy-and-adfs-in-under-10-minutes/
* https://ethernuno.wordpress.com/2014/04/20/install-adds-on-windows-server-2012-r2-with-powershell/

--------------

.. include:: navigation.txt
