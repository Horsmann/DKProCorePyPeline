import unittest
import tempfile
from dkpro_core_pypeline import *

def get_dummy_engine():
    return AnalysisEngine(group = "de.tudarmstadt.ukp.dkpro.core",
			           artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
			          component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				        version = "1.10.0",
				        variant = "maxent")

def get_maven_information_from_dummy():
    e = get_dummy_engine()
    return e.get_group(), e.get_artifact(), e.get_version()


class TestMainClassBuilder(unittest.TestCase):

    def setUp(self):
        self.template = tempfile.mkdtemp()
        self.workspace = tempfile.mkdtemp()
        self.mainBuilder = MainClassBuilder(self.template, self.workspace)
    
    def test_get_file_system_location(self):
        location = self.mainBuilder.get_file_system_location()
        self.assertTrue(location.endswith("src/main/java/python/pipeline/MainClass.java"))
        
    def test_boolean_as_string(self):
        self.assertTrue(self.mainBuilder.boolean_as_string("true"))
        self.assertTrue(self.mainBuilder.boolean_as_string("false"))
        self.assertFalse(self.mainBuilder.boolean_as_string("True"))
        self.assertFalse(self.mainBuilder.boolean_as_string("1"))
        
    def test_engine_to_java(self):
        e = get_dummy_engine()
        engine_java = self.mainBuilder.engine_to_java(e, 0) 
        expected = "        AnalysisEngineDescription ae0 = AnalysisEngineFactory." + \
                     "createEngineDescription(OpenNlpPosTagger.class, " + \
                     "OpenNlpPosTagger.PARAM_VARIANT, \"maxent\");\n"

        self.assertEqual(expected, engine_java)
    
    def test_reader_java(self):
        reader = CollectionReader(group = "de.tudarmstadt.ukp.dkpro.core",
		        			   artifact = "de.tudarmstadt.ukp.dkpro.core.io.text-asl",
				              component = "de.tudarmstadt.ukp.dkpro.core.io.text.StringReader", 
					           language = "en", 
					            version = "1.10.0",
					        document_id = "123",
				          document_text = "This is a text. Isn't this cool?")
        reader_java = self.mainBuilder.reader_to_java(reader)
        expected = "        CollectionReaderDescription reader = " + \
                  "CollectionReaderFactory.createReaderDescription(StringReader.class," + \
                  " StringReader.PARAM_DOCUMENT_ID, \"123\", " + \
                  "StringReader.PARAM_DOCUMENT_TEXT, \"This is a text. Isn't this cool?\","+ \
                  " StringReader.PARAM_LANGUAGE, \"en\");\n" 
        self.assertEqual(expected, reader_java)

class TestPomXmlBuilder(unittest.TestCase):
    
    def setUp(self):
        self.template = tempfile.mkdtemp()
        self.workspace = tempfile.mkdtemp()    
        self.pom = PomXmlBuilder(self.template, self.workspace)
    
    def test_get_added_dependencies(self):
        # should be empty
        self.assertEqual(0, len(self.pom.get_added_dependencies()))
        
        # add one dependency
        group, artifact, version = get_maven_information_from_dummy()
        self.pom.add_dependency(group, artifact, version)
        
        dependencies = self.pom.get_added_dependencies()
        self.assertEqual(1, len(dependencies))
        
        expected = "        <dependency>\n" + \
                   "            <groupId>de.tudarmstadt.ukp.dkpro.core</groupId>\n" + \
                   "            <artifactId>de.tudarmstadt.ukp.dkpro.core.opennlp-asl</artifactId>\n" + \
                   "            <version>1.10.0</version>\n" + \
                   "        </dependency>\n"
        self.assertEqual(expected, dependencies[0])
        
class TestDKProCoreComponent(unittest.TestCase):

    def setUp(self):
        self.comp = get_dummy_engine()
    
    def test_get_configuration(self):
        config = self.comp.get_additional_parameter()
        self.assertEqual(1, len(config))
        
        self.assertEqual("variant", config[0][0])
        self.assertEqual("maxent", config[0][1])
        
    def test_getters(self):
        self.assertEqual("OpenNlpPosTagger", self.comp.get_short_name())
        self.assertEqual("de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", self.comp.get_import_path())
        self.assertEqual("1.10.0", self.comp.get_version())
        self.assertEqual("de.tudarmstadt.ukp.dkpro.core.opennlp-asl", self.comp.get_artifact())
        self.assertEqual("de.tudarmstadt.ukp.dkpro.core", self.comp.get_group())
        
                

if __name__ == '__main__':
    unittest.main()
