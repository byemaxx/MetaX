# MetaX

**MetaX** is a novel tool for linking peptide sequences with taxonomic and functional information in **Metaproteomics**. We introduce the ***Operational Taxon-Function (OTF)*** concept to explore microbial roles and interactions ("**who is doing what and how**") within ecosystems. 

MetaX also features <u>statistical modules</u> and <u>plotting tools</u> for analyzing peptides, taxa, functions, proteins, and taxon-function contributions across groups.

📥[Download MetaX](#download--installation)


![abstract](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/abstract.png)

## Operational Taxon-Function (OTF)

**Operational Taxon-Function (OTF) Unit**: An operational unit which represents the association between specific taxa and biological functions. 

![OTF_Structure](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/OTF_Structure.png)

## OTF Analyzer

The Tools in OTF Analyzer

![compostion](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/composition.png)

## OTF Examples

Linking Taxa and Functions in different levels of the hierarchy, and various functional categories. e.g., **Species-KO**, **Genus-CAZy**, **Phylum-EC**, etc. Lots of visualization tools can be selected.

**Network**

**Dots** represent <u>taxa</u> and **squares** represent <u>functions</u> in the network.

- <img src="https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/tf_link_net.png" alt="OTF" style="zoom: 50%;" />



**Heatmap**

Show all Taxa of a function.

- <img src="https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/taxa_func_link_heatmap.png" alt="tf_link_heatmap" style="zoom:50%;" />

**Bar**

Show all functions of a taxon

- <img src="https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/taxa_func_link_bar.png" alt="tf_link_bar" style="zoom:50%;" />

**OTF Heatmap**

Show OTFS intensity in groups(samples), e.g., **Species-KO** OTF Heatmap

<img src="https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/otf_heatmap.png" alt="otf_heatmap" style="zoom:50%;" />

## Download & Installation
- **Desktop Version** (Recommended)

  > The desktop version comes fully set up and ready to use, including all required dependencies and a graphical user interface.
  >
  > <a href="https://shiny2.imetalab.ca/shiny/rstudio/metax_download/" target="_blank">Download the MetaX Desktop Version</a>

<br>

- **Command-line version**

    > Install via [PyPI](https://pypi.org/project/MetaXTools/):
    >
    > ```bash
    > python -m pip install MetaXTools
    > ```
    > 
    > After installation, launch the GUI by typing `metax` in your terminal.



## Guidebook

- `Desktop Version(desktop)`:
  - Refer to the <a href="https://byemaxx.github.io/MetaX/" target="_blank">MetaX Cookbook</a> for detailed instructions on how to use MetaX with the graphical user interface.
  <br>
- `Command-line version`:
  - Read the example documentation in the [Notebook](https://github.com/byemaxx/MetaX/blob/main/Docs/example.ipynb) for detailed instructions and examples.


## Citing
If you use MetaX in your research, please cite the following publication:

> **Operational Taxon-Function Framework in MetaX: Unveiling Taxonomic and Functional Associations in Metaproteomics**. 
> *Wu, Q., Ning, Z., Zhang, A., Zhang, X., Sun, Z., & Figeys, D.* (2025).  Analytical Chemistry. DOI:  <a href="https://doi.org/10.1021/acs.analchem.4c06645" target="_blank">10.1021/acs.analchem.4c06645</a>.

