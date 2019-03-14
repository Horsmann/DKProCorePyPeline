import tempfile
import os
import subprocess
import re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# file output
fh = logging.FileHandler('log.txt')
fh.setLevel(logging.DEBUG)

# console output
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-5s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

class CommandExecutor:
    @staticmethod
    def execute(cmd):
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode:
            logger.error("Command failed: [%s]" % ' '.join(cmd))
            logger.error("Error message of failed command: %s" % result.stdout)
            raise ValueError(result.stdout)

class UIMAPipeline:
    """A DKPro pipeline. The template folder contains the prototype for a 
    Java Main class and a pom.xml"""
    def __init__(self):
        self.template_path = os.path.dirname(__file__) + "/template_maven"
        self.working_directory = tempfile.TemporaryDirectory()
        self.main = MainClassBuilder(self.template_path, self.working_directory.name)
        self.pom = PomXmlBuilder(self.template_path, self.working_directory.name)
    
    def set_reader(self, reader):
        self.main.set_reader(reader)
        self.pom.add(reader)
    
    def add_engine(self, engine):
        self.main.add_engine(engine)
        self.pom.add_dependency(engine)
        
    def execute(self):
        """ Generates a Java class with the specified components and creates
         the corresponding pom.xml"""
        self.main.generate()
        self.pom.generate()
        
        logger.debug("Using pom located at [%s]" % self.pom.target_file)
        logger.info("Running 'mvn clean install'")
        compile_cmd = ['mvn', 'clean', 'install', '-f', self.pom.target_file]
        CommandExecutor.execute(compile_cmd)
        logger.info("...completed 'mvn clean install'")
        
        logger.info("Running 'mvn exec:java'")        
        main_class_project_relative = re.sub("/", ".", self.main.target_package) + "." + self.main.TEMPLATE_CLASS_NAME
        exec_main_parameter = "-Dexec.mainClass=" + main_class_project_relative
        execute_cmd = ['mvn', 'exec:java', exec_main_parameter, '-f', self.pom.target_file]
        CommandExecutor.execute(execute_cmd)
        logger.info("...completed 'mvn exec:java'")

class MainClassBuilder:
    """ Constructs a Java class file which contains a main() method that contains the
    DKPro Core SimplePipeline"""
    def __init__(self, template_folder, working_directory):
        self.TEMPLATE_CLASS_NAME = "MainClass"
        self.main_class = template_folder+"/" + self.TEMPLATE_CLASS_NAME + ".java"
        self.project_structure = "src/main/java"
        self.target_package = "python/pipeline"
        self.target_directory = working_directory + "/" + \
                                self.project_structure + "/" + \
                                self.target_package 
        self.target_file = self.target_directory + "/" + \
                           self.TEMPLATE_CLASS_NAME + ".java"
        self.reader = None
        self.engines = []
        
        #ensure that nested folders in temp dir exist
        self.make_dirs(self.target_directory)
        logger.debug("MainClassBuilder [target_file: %s]" % self.target_file)
        
    def get_file_system_location(self):
        return self.target_file    
        
    def make_dirs(self, directory):    
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def set_reader(self, reader):
        self.reader = reader
    
    def add_engine(self, engine):
        self.engines.append(engine)    
        
    def boolean_as_string(self, value):    
        """ Returns True if value is a java-style boolean (true/false) as string"""
        return value == "true" or value == "false"

    def engine_to_java(self, engine, i):
        """ The provided engine is transformed into a valid 
        Java AnalysisEngineDescription """
        engine_entry = "        AnalysisEngineDescription ae"+str(i)+ \
                       " = AnalysisEngineFactory.createEngineDescription(" + \
                       engine.get_short_name() + ".class"
        for k, v in engine.get_additional_parameter():
            if isinstance(v, str) and not self.boolean_as_string(v):
                v = "\"" + v + "\""                    
            parameter_pair = engine.get_short_name() + ".PARAM_" + k.upper() + ", " + v
            engine_entry += ", " + parameter_pair
            logger.debug("Adding parameter pair [%s]" % parameter_pair)
        engine_entry += ");\n"
        return engine_entry
    
    def reader_to_java(self, reader):
        coll_reader = "        CollectionReaderDescription reader = " + \
                      "CollectionReaderFactory.createReaderDescription(" 
        coll_reader += reader.get_short_name() + ".class"

        for k,v in reader.get_additional_parameter():
            if isinstance(v, str) and not self.boolean_as_string(v):
                v = "\"" + v + "\""                    
            parameter_pair = reader.get_short_name() + ".PARAM_" + k.upper() + ", " + v
            coll_reader += ", " + parameter_pair
            logger.debug("Adding parameter pair [%s]" % parameter_pair)
        coll_reader+=");\n"        
        return coll_reader
    
    def generate(self):
        lines=[]
        with open(self.main_class, 'r', encoding='utf-8') as f:
            for line in f:
            
                if "IMPORT-INJECTION" in line:
                    lines.append("import " + self.reader.get_import_path() + ";\n")
                    for engine in self.engines:
                        lines.append("import " + engine.get_import_path() + ";\n")
                    continue
            
                if "PIPELINE-INJECTION-POINT" in line:
                    
                    # Add reader
                    logger.debug("Injecting reader component")
                    coll_reader = self.reader_to_java(self.reader)
                    lines.append(coll_reader)
                    
                    # Add engines
                    for i, engine in enumerate(self.engines):
                        logger.debug("Injecting engine component for [%s]" % engine.get_short_name())
                        engine_entry = self.engine_to_java(engine, i)
                        lines.append(engine_entry)
                        
                    # Add simple pipeline call    
                    pipeline_call = "        SimplePipeline.runPipeline(reader"
                    for i, _ in enumerate(self.engines):
                        pipeline_call+=", ae"+str(i)
                    pipeline_call+=");"
                    lines.append(pipeline_call)
                    continue
                
                lines.append(line)
        with open(self.target_file, 'w', encoding='utf-8') as f:
            for l in lines:
                f.write(l)

class PomXmlBuilder:
    def __init__(self, template_folder, working_directory):
        self.dependencies=[]
        self.template_pom = template_folder+"/pom.xml"
        self.target_file = working_directory + "/pom.xml"

    def add_dependency(self, component):
        self.add_dependency(self. component.get_group(), 
                                  component.get_artifact(),
                                  component.get_version())
        
         
    def add_dependency(self, group, artifact, version):
        self.dependencies.append(
        "        <dependency>\n" +
        "            <groupId>"  + group + "</groupId>\n" + 
        "            <artifactId>" + artifact + "</artifactId>\n" +
        "            <version>"  + version + "</version>\n" +
        "        </dependency>\n")
        
    def get_file_system_location(self):
        return self.target_file  
        
    def get_added_dependencies(self):
        return self.dependencies
        
    def generate(self):
        already_included_dependencies=set()
        pom_lines=[]
        with open(self.template_pom, 'r', encoding='utf-8') as f:
            for line in f:
                if "INJECTION-POINT" in line:
                    for dependency in self.dependencies:
                        if dependency in already_included_dependencies:
                            continue
                        pom_lines.append(dependency)
                        already_included_dependencies.add(dependency)
                else:
                    pom_lines.append(line)
        with open(self.target_file, 'w', encoding='utf-8') as f:
            for line in pom_lines:
                f.write(line)

class DKProCoreComponent():
   """A generic DKPro Component which represents a CollectionReaderDescription or AnalysisEngineDescription"""
   def __init__(self, **kwargs):
       self.__required=["component", "group", "version", "artifact"]
       self.__dict=kwargs

       # check that all required information is available
       for required_key in self.__required:
           if required_key not in kwargs:
               raise ValueError("Required parameter [%s] is missing" % required_key)
        

   def get_additional_parameter(self):
        """ Returns the parameters, which are unique to a component.
        The returned parameters will not include: 'artifact', 'group', 'version' 
        and 'component'. The parameters are returned in alphabetic order"""
        config_parameters=[]
        for k,v in self.__dict.items():
            if k in self.__required:
                continue
            config_parameters.append((k,v))
        config_parameters.sort(key=lambda x:x[0])
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

class CollectionReader(DKProCoreComponent):
    pass
    
class AnalysisEngine(DKProCoreComponent):
    pass    