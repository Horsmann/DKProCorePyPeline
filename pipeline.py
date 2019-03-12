from dkpro_core_pypeline.dkpro_core_pypeline import *
from os.path import expanduser
user_home = expanduser("~")

reader = CollectionReader(group = "de.tudarmstadt.ukp.dkpro.core",
					   artifact = "de.tudarmstadt.ukp.dkpro.core.io.text-asl",
				      component = "de.tudarmstadt.ukp.dkpro.core.io.text.StringReader", 
					   language = "en", 
					    version = "1.10.0",
					document_id = "123",
				  document_text = "This is a text. Isn't this cool?")
segmenter = AnalysisEngine(group = "de.tudarmstadt.ukp.dkpro.core",
                        artifact = "de.tudarmstadt.ukp.dkpro.core.tokit-asl",
					   component = "de.tudarmstadt.ukp.dkpro.core.tokit.BreakIteratorSegmenter",
					     version = "1.10.0")
pos = AnalysisEngine(group = "de.tudarmstadt.ukp.dkpro.core",
				  artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
				 component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				   version = "1.10.0",
				   variant = "maxent")
writer = AnalysisEngine(group = "de.tudarmstadt.ukp.dkpro.core",
				     artifact = "de.tudarmstadt.ukp.dkpro.core.io.conll-asl",
				    component = "de.tudarmstadt.ukp.dkpro.core.io.conll.Conll2003Writer", 
				      version = "1.9.0",
                    overwrite = "true",
				  write_chunk = "false",
		   write_named_entity = "false",
			  target_location = user_home + "/Desktop/dkpro_output_folder",
			  target_encoding = "utf-8",
		   filename_extension = ".txt")

pipeline = UIMAPipeline()
pipeline.set_reader(reader)
pipeline.add_engine(segmenter)
pipeline.add_engine(pos)
pipeline.add_engine(writer)
pipeline.execute()