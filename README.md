# The shunPykeR's guide to single cell RNA-seq analysis

<img align="left" src="images/shunpiker_definition_logo.png" height=200 />
<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>


*Similar to [The Hitchhiker's_Guide to the Galaxy](https://en.wikipedia.org/wiki/The_Hitchhiker%27s_Guide_to_the_Galaxy), this guide has probably ended up in your "hands" due to a great catastrophe: your single cell data need to be analyzed and you don't know how to do it. Well, **DON'T PANIC**, this guide is here to help you skip all the hurdles of coding and decision making and let you get the most out of your data.*

*This guide starts with a click on the `Run` button. Once that is done, just keep clicking...*

<br/><br/>
<p align="center"> <img src="images/shunpiker_infographic.jpg" width=500/> </p>
<br/><br/>


###  This guide in a nutshell


This guide is a complete pipeline for the analysis of scRNA-seq datasets from start to finish in python. It has been simplified by hiding more complex code snipsets behind the scenes (within the `shunpiker_modules.py` file) allowing non computational scientists to perform a robust and thorough analysis of their scRNA-seq datasets with (relative) peace of mind. However, it can also be used by bioinformaticians that may want to adjust it and reuse it in their own way. 

Within this guide we have brought together a combination of already established scRNA-seq analysis tools, that we have put together in a logical order to simplify running your analysis. A general rule of thumb for analyzing your data would be to discard "unwanted" cells on a per sample basis, while removing not expressed genes across all your samples together.

Here is the list of tools that we implement across this guide:
- **scanpy**<sup>1</sup> provides the backbone of this pipeline and allows for visualization options (https://scanpy.readthedocs.io/en/stable/)
- **scrublet**<sup>2</sup> remove doublet cells (https://github.com/swolock/scrublet)
- **phenoGraph**<sup>3</sup> clusters cells based on their multi-dimensional enviroment (https://github.com/jacoblevine/PhenoGraph)


**Step 1** in this notebook guides you through fully analyzing one sample from scratch to finish, and also store the results for integration with other samples if necessary. If you only have one sample, then **Step 1** is all you need. You can then skip to **Step 3** and **Step 4** to explore more visualization options for your data and perform differential expression analysis between your clusters of interest. If you have more than one sample, store good quality cells per sample using **Step 1** and then move to **Step 2** to integrate all your samples together. Then again move to **Step 3** and **Step 4** as described above.


- **Step 1** Perform quality control and clean up each sample from scratch
- **Step 2** Intergrate together multiple "clean" samples
- **Step 3** Explore visualization alternatives
- **Step 4** Apply differential expression analysis
- **Step 5** TBA


See the complete Jupyter notebook [here]("./The shunPykeR's guide to scRNA-seq analysis").
