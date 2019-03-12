# DKProPyPeline
API to call Java-DKPro (DKPro Python Pipeline) from Python

The code builds a Java/Maven project in the background and requires a working Java/Maven setup to be used.

Java DKPro Core pipeline version
```java
 public static void main(String[] args) throws Exception
    {
        CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
            StringReader.class, 
            StringReader.PARAM_LANGUAGE, "en",
            StringReader.PARAM_DOCUMENT_TEXT, "This is a text. Isn't this cool?");

        AnalysisEngineDescription segmenter = AnalysisEngineFactory
                .createEngineDescription(BreakIteratorSegmenter.class);

        AnalysisEngineDescription pos = AnalysisEngineFactory.createEngineDescription(
                OpenNlpPosTagger.class, OpenNlpPosTagger.PARAM_VARIANT, "maxent");

        AnalysisEngineDescription writer = AnalysisEngineFactory.createEngineDescription(
                Conll2003Writer.class, Conll2003Writer.PARAM_TARGET_LOCATION,
                ".../outputFile.txt", Conll2003Writer.PARAM_TARGET_ENCODING, "utf-8",
                Conll2003Writer.PARAM_OVERWRITE, true);

        SimplePipeline.runPipeline(reader, segmenter, pos, writer);
    }
```

becomes the following Pyhton DKPro Core pipeline

```python
reader = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.io.text.StringReader", 
					        group = "de.tudarmstadt.ukp.dkpro.core",
					     artifact = "de.tudarmstadt.ukp.dkpro.core.io.text-asl",
					     language = "en", 
					      version = "1.10.0",
					  document_id = "123",
				    document_text = "This is a text. Isn't this cool?")
segmenter = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.tokit.BreakIteratorSegmenter",
					           group = "de.tudarmstadt.ukp.dkpro.core",
					         version = "1.10.0",
					        artifact = "de.tudarmstadt.ukp.dkpro.core.tokit-asl")
pos = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.opennlp.OpenNlpPosTagger", 
				         group = "de.tudarmstadt.ukp.dkpro.core",
				       version = "1.10.0",
				      artifact = "de.tudarmstadt.ukp.dkpro.core.opennlp-asl",
				       variant = "maxent")
writer = DKProComponent(component = "de.tudarmstadt.ukp.dkpro.core.io.conll.Conll2003Writer", 
				            group = "de.tudarmstadt.ukp.dkpro.core",
				          version = "1.9.0",
				         artifact = "de.tudarmstadt.ukp.dkpro.core.io.conll-asl",
				        overwrite = "true",
				      write_chunk = "false",
			   write_named_entity = "false",
				  target_location = "/Users/toobee/Desktop/targetFolderConll",
				  target_encoding = "utf-8",
			   filename_extension = ".txt")

pipeline = DKProPipeline("template_maven")
pipeline.set_reader(reader)
pipeline.add_engine(segmenter)
pipeline.add_engine(pos)
pipeline.add_engine(writer)
pipeline.execute()
```

<h2>Specifying a component</h2>
A component consists of at least four parameters. 
```
component, which is the fully qualified path of the component's Java class (i.e., the import of the class in the Java file)
artifact, the artifact id of the Maven artifact  in which the component is located
group, the group id of the Maven artifact
version, the version of the Maven artifact
```

<h2>Providing parameters</h2>
Java-styled `CollectionReader` or `AnalysisEngine` parameters are provided as named parameters in python. A Java parameter `MyEngine.PARAM_SOURCE_LOCATION, '/usr/home/data.txt'` becomes `source_location = '/usr/home/data.txt'`.
