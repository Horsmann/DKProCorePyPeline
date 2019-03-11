class DKProComponent():
   def __init__(self, **kwargs):
       self.__required=["component", "group", "version", "artifact"]
       self.__dict=kwargs

       # check that all required information is available
       for required_key in self.__required:
           if required_key not in kwargs:
               raise ValueError("Required parameter [%s] is missing" % required_key)
        

   def get_configuration(self):
        config_parameters=[]
        for k,v in self.__dict.items():
            if k in self.__required:
                continue
            config_parameters.append((k,v))
        return config_parameters
        
   def get_group(self):
        return self.__dict["group"]
    
   def get_artifact(self):
        return self.__dict["artifact"]
    
   def get_version(self):
        return self.__dict["version"]        
        
   def get_import_path(self):
        return self.__dict["component"]
    
   def get_short_name(self):
        return self.__dict["component"].split(".")[-1] 
                