Release Notes
*************

Most installs require only using bq-admin setup.  Certain upgrades require specific 
actions on the part of the system administrator.



0.5.1.1
    * Bug in Turbogears setup does not allow Export to function properly.
      You must patch the tg/configuration.py::

         app = RegistryManager(app)
         app = RegistryManager(app, True)
      
