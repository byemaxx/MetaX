# MetaX

**MetaX** is a novel tool for linking peptide sequences with taxonomic and functional information in **Metaproteomics**. We introduce the ***Operational Taxon-Function (OTF)*** concept to explore microbial roles and interactions ("**who is doing what and how**") within ecosystems. 

MetaX also features <u>statistical modules</u> and <u>plotting tools</u> for analyzing peptides, taxa, functions, proteins, and taxon-function contributions across groups.


![abstract](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/abstract.png)

## Operational Taxon-Function (OTF)

**Operational Taxon-Function (OTF) Unit**: An operational unit which represents the association between specific taxa and biological functions. 

![OTF_Structure](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/OTF_Structure.png)

## OTFs Network

Linking Taxa and Functions in different levels of the hierarchy, and different functional categories. e.g., **Species-KO**, **Genus-CAZy**, **Phylum-EC**, etc.

- ![OTF](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/tf_link_net.png)



e.g. The **KEGG Pathways** linked to ***Roseburia hominis***

- ![tf_link_net_2](https://github.com/byemaxx/MetaX/raw/main/Docs/MetaX_Cookbook.assets/tf_link_net_2.png)



## Download
### `Desktop Version(Recommended)`:
The desktop version comes fully set up and ready to use, including all required dependencies and a graphical user interface.

<a href="https://shiny2.imetalab.ca/shiny/rstudio/metax_download/" target="_blank">Download MetaX Desktop Version</a>


<br>

### `Command-line version`:
Clone the repository to your local machine and install the required dependencies.
  ```bash
  python -m pip install MetaXTools
  ```


## Getting Started
- `Desktop Version(desktop)`:
  - Refer to the <a href="https://byemaxx.github.io/MetaX/" target="_blank">MetaX Cookbook</a> for detailed instructions on how to use MetaX wtih the graphical user interface.
  <br>
- `Command-line version`:
  - Read the example documentation in the [Notebook](https://github.com/byemaxx/MetaX/blob/main/Docs/example.ipynb) for detailed instructions and examples.


## Citing MetaX
- If you use MetaX in your research, please cite the following publication:
  - **MetaX: A peptide centric metaproteomic data analysis platform using Operational Taxa-Functions (OTF)**. *Wu, Q., Ning, Z., Zhang, A., Zhang, X., Sun, Z., & Figeys, D.* (2024).  bioRxiv. DOI:  <a href="https://doi.org/10.1101/2024.04.19.590315" target="_blank">10.1101/2024.04.19.590315</a>.

