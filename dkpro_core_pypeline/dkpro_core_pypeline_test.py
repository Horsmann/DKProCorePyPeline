import unittest
import tempfile
from dkpro_core_pypeline import MainClassBuilder, AnalysisEngine, CollectionReader


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
        e = AnalysisEngine(group = "de.tudarmstadt.ukp.dkpro.core",
			            artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
				       component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				         version = "1.10.0",
				         variant = "maxent")
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

if __name__ == '__main__':
    unittest.main()
