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
                ".../outputFolder/", Conll2003Writer.PARAM_TARGET_ENCODING, "utf-8",
                Conll2003Writer.PARAM_OVERWRITE, true);

        SimplePipeline.runPipeline(reader, segmenter, pos, writer);
    }
```

becomes the following Pyhton DKPro Core pipeline

```python
reader = CollectionReader(group = "de.tudarmstadt.ukp.dkpro.core", # Maven group id
                       artifact = "de.tudarmstadt.ukp.dkpro.core.io.text-asl", # Maven artifact id
                      component = "de.tudarmstadt.ukp.dkpro.core.io.text.StringReader", # Java import of class 		
		        version = "1.10.0", # Maven version of artifact
	               language = "en", # StringReader parameter
                    document_id = "123", # StringReader parameter
	          document_text = "This is a text. Isn't this cool?") # StringReader parameter
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
                    overwrite = "true",  # PARAM_OVERWRITE in Java
	          write_chunk = "false", # PARAM_WRITE_CHUNK in Java
           write_named_entity = "false", # PARAM_WRITE_NAMED_ENTITY in Java
              target_location = ".../outputFolder/", # ..etc.
	      target_encoding = "utf-8")

pipeline = UIMAPipeline()
pipeline.set_reader(reader)
pipeline.add_engine(segmenter)
pipeline.add_engine(pos)
pipeline.add_engine(writer)
pipeline.execute()
```

<h2>Specifying a component</h2>
A component consists of at least four parameters. 

```
a) component - which is the fully qualified path of the component (i.e., the import of the class in the Java file)
b) artifact - the artifact id of the Maven artifact in which the component is located
c) group - the group id of the Maven artifact
d) version - the version of the Maven artifact
```

<h2>Providing parameters</h2>

Java-styled `CollectionReader` or `AnalysisEngine` parameters are provided as named parameters in python. 

A Java parameter `MyEngine.PARAM_SOURCE_LOCATION, '/usr/home/data.txt'` becomes `source_location = '/usr/home/data.txt'`.
`PARAM_` is omitted but the name of the following parameter must be exactly identical to the Java version otherwise an exception will be thrown.

<h2>Requirements</h2>

```
1) Java compiler and runtime

2) Maven

3) Both tools must be setup correctly to work on the command line or shell environment

4) Python3
```

The required Java version depends on the DKPro version you are using but everything from 1.8+ works (version 1.10.0)
