import tempfile
import os
import subprocess
import re

class DKProPipeline:
    def __init__(self, template_folder):
        self.working_directory = tempfile.TemporaryDirectory()
        #self.working_directory = "/Users/toobee/Desktop/myTmp"
        self.main = MainClassBuilder(template_folder, self.working_directory.name)
        self.pom = PomXmlBuilder(template_folder, self.working_directory.name)
    
    def set_reader(self, reader):
        self.main.set_reader(reader)
        self.pom.add(group=reader.get_group(), 
                     artifact=reader.get_artifact(), 
                    version=reader.get_version())
    
    def add_engine(self, engine):
        self.main.add_engine(engine)
        self.pom.add(group=engine.get_group(), artifact=engine.get_artifact(), version=engine.get_version())
        
    def execute(self):
        self.main.generate()
        self.pom.generate()
        
        compile_cmd = ['mvn', 'clean', 'install', '-f', self.pom.target_file]
        subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
                
        main_class_project_relative = re.sub("/", ".", self.main.target_package) + "." + self.main.TEMPLATE_CLASS_NAME
        exec_main_parameter = "-Dexec.mainClass=" + main_class_project_relative
        execute_cmd = ['mvn', 'exec:java', exec_main_parameter, '-f', self.pom.target_file]
        subprocess.check_output(execute_cmd, stderr=subprocess.STDOUT)                

class MainClassBuilder:
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
        print(self.target_file)
        self.reader = None
        self.engines = []
        
        #ensure that nested folders in temp dir exist
        self.make_dirs(self.target_directory)
        
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
                    coll_reader = """CollectionReaderDescription reader = 
                    CollectionReaderFactory.createReaderDescription("""
                    coll_reader += self.reader.get_short_name() + ".class"

                    for k,v in self.reader.get_configuration():
                        if isinstance(v, str) and not self.boolean_as_string(v):
                            v = "\"" + v + "\""                    
                        coll_reader += ", " + self.reader.get_short_name() + ".PARAM_" + k.upper() + ", " + v
                
                    coll_reader+=");\n"
                    lines.append(coll_reader)
                    
                    # Add engines
                    for i, engine in enumerate(self.engines):
                        engine_entry = "AnalysisEngineDescription ae"+str(i)+ \
                                       " = AnalysisEngineFactory.createEngineDescription(" + \
                                       engine.get_short_name() + ".class"
                        for k, v in engine.get_configuration():
                            if isinstance(v, str) and not self.boolean_as_string(v):
                                v = "\"" + v + "\""                    
                            engine_entry += ", " + engine.get_short_name() + ".PARAM_" + k.upper() + ", " + v
                        engine_entry += ");\n"
                        lines.append(engine_entry)
                        
                    # Add simple pipeline call    
                    pipeline_call = "SimplePipeline.runPipeline(reader"
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
    
    def add(self, group, artifact, version):
        self.dependencies.append(
        "<dependency>\n" +
        "<groupId>"  + group + "</groupId>\n" + 
        "<artifactId>" + artifact + "</artifactId>\n" +
        "<version>"  + version + "</version>\n" +
        "</dependency>\n")
        
    def generate(self):
        pom_lines=[]
        with open(self.template_pom, 'r', encoding='utf-8') as f:
            for line in f:
                if "INJECTION-POINT" in line:
                    for dependency in self.dependencies:
                        pom_lines.append(dependency)
                else:
                    pom_lines.append(line)
        with open(self.target_file, 'w', encoding='utf-8') as f:
            for line in pom_lines:
                f.write(line)