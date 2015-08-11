How to prepare Active Directory Federation Services (ADFS) 3.0 as an Identity Provider
===============================================

**Requirements**:

1. `Pre-requisites from Microsoft Technet <https://technet.microsoft.com/library/bf7f9cf4-6170-40e8-83dd-e636cb4f9ecb>`_

2. `Install Procedure from Microsoft Technet <https://technet.microsoft.com/en-us/library/dn303423>`_

1. The ADFS Server must already trust the Service Provider's (SP) Keystone
   certificate. The best way to ensure this is to have the ADFS CA (or a
   public CA) sign a certificate request for the Keystone service.
2. In the ADFS Management Console, choose ``Add Relying Party Trust``.
3. Select ``Import data about the relying party published online or on a
   local network`` and enter the URL for the SP Metadata:
   for example, ``https://<sp ip address or dns name>:5000/Shibboleth.sso/Metadata``
4. Continuing the wizard, select ``Permit all users to access this
   relying party``.
5. In the ``Add Transform Claim Rule Wizard``, select ``Pass Through or
   Filter an Incoming Claim``.
6. Name the rule (for example, ``Pass Through UPN``) and select the ``UPN``
   Incoming claim type.
7. Click OK to apply the rule and finalize the setup.

Setup an AIO ADFS Server
------------------------
This setup is not for production use - it is only for development and testing purposes.

TODO(odyssey4me)

Useful References
-----------------
* http://blogs.technet.com/b/rmilne/archive/2014/04/28/how-to-install-adfs-2012-r2-for-office-365.aspx
* http://blog.kloud.com.au/2013/08/14/powershell-deployment-of-web-application-proxy-and-adfs-in-under-10-minutes/
* https://ethernuno.wordpress.com/2014/04/20/install-adds-on-windows-server-2012-r2-with-powershell/
