# -*- coding: utf-8 -*-
from dkpro_core_pypeline.dkpro_core_pypeline import *
from os.path import expanduser
user_home = expanduser("~")

reader = CollectionReader(component = "de.tudarmstadt.ukp.dkpro.core.io.text.StringReader", 
					          group = "de.tudarmstadt.ukp.dkpro.core",
					       artifact = "de.tudarmstadt.ukp.dkpro.core.io.text-asl",
					       language = "en", 
					        version = "1.10.0",
					    document_id = "123",
				      document_text = "This is a text. Isn't this cool?")
segmenter = AnalysisEngine(component = "de.tudarmstadt.ukp.dkpro.core.tokit.BreakIteratorSegmenter",
					           group = "de.tudarmstadt.ukp.dkpro.core",
					         version = "1.10.0",
					        artifact = "de.tudarmstadt.ukp.dkpro.core.tokit-asl")
pos = AnalysisEngine(component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				         group = "de.tudarmstadt.ukp.dkpro.core",
				       version = "1.10.0",
				      artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
				       variant = "maxent")
writer = AnalysisEngine(component = "de.tudarmstadt.ukp.dkpro.core.io.conll.Conll2003Writer", 
				            group = "de.tudarmstadt.ukp.dkpro.core",
				          version = "1.9.0",
				         artifact = "de.tudarmstadt.ukp.dkpro.core.io.conll-asl",
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
