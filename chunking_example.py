from DKProCorePyPeline import *

reader = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.io.tei.TeiReader", 
					        group = "de.tudarmstadt.ukp.dkpro.core",
					     artifact = "de.tudarmstadt.ukp.dkpro.core.io.tei-asl",
					     language = "en", 
					      version = "1.10.0",
				  source_location = "/Users/toobee/Desktop/data/",
					     patterns = "*.xml")
					     					        
pos = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				         group = "de.tudarmstadt.ukp.dkpro.core",
				       version = "1.10.0",
				      artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
				       variant = "perceptron")
				       
chunk = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpChunker",
					       group = "de.tudarmstadt.ukp.dkpro.core",		       
					     version = "1.10.0",
					    artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
					    variant  = "default") 
				       
writer = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.io.conll.Conll2003Writer", 
				            group = "de.tudarmstadt.ukp.dkpro.core",
				          version = "1.9.0",
				         artifact = "de.tudarmstadt.ukp.dkpro.core.io.conll-asl",
				        overwrite = "true",
				  target_location = "/Users/toobee/Desktop/targetFolderConll",
				  target_encoding = "utf-8",
			   filename_extension = ".txt")

pipeline = DKProPipeline("template_maven")
pipeline.set_reader(reader)
pipeline.add_engine(pos)
pipeline.add_engine(chunk)
pipeline.add_engine(writer)
pipeline.execute()