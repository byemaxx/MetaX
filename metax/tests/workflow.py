# This file is used to generate the genral result of the OTF Analysis workflow
import os
import sys
import json # laod and stroe the config file

import logging
logging.basicConfig(
    level=logging.INFO,  # set log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # set log format
    datefmt='%Y-%m-%d %H:%M:%S',  # set date format
    filename= None # output log to console
)
# create logger
logger = logging.getLogger(__name__)

# if not run as script, import the necessary MetaX modules by absolute path
logging.info("Importing MetaX modules...")
if __name__ == '__main__':
    # Use absolute path to import the module
    metax_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # set parent dir as the root dir
    metax_dir = os.path.dirname(metax_dir)
    print(metax_dir)
    sys.path.append(metax_dir)
    
    from metax.utils.version import __version__
    from metax.taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
    from metax.utils.metax_updater import Updater
    from metax.taxafunc_ploter.heatmap_plot import HeatmapPlot
    from metax.taxafunc_ploter.basic_plot import BasicPlot
    from metax.taxafunc_ploter.volcano_plot_js import VolcanoPlotJS
    from metax.taxafunc_ploter.volcano_plot import VolcanoPlot
    from metax.taxafunc_ploter.tukey_plot import TukeyPlot
    from metax.taxafunc_ploter.bar_plot_js import BarPlot
    from metax.taxafunc_ploter.sankey_plot import SankeyPlot
    from metax.taxafunc_ploter.network_plot import NetworkPlot
    from metax.taxafunc_ploter.trends_plot import TrendsPlot
    from metax.taxafunc_ploter.trends_plot_js import TrendsPlot_js
    from metax.taxafunc_ploter.pca_plot_js import PcaPlot_js
    from metax.taxafunc_ploter.diversity_plot import DiversityPlot
    from metax.taxafunc_ploter.sunburst_plot import SunburstPlot
    from metax.taxafunc_ploter.treemap_plot import TreeMapPlot


    from metax.peptide_annotator.metalab2otf import MetaLab2OTF
    from metax.peptide_annotator.peptable_annotator import PeptideAnnotator

    from metax.database_builder.database_builder_own import build_db
    from metax.database_updater.database_updater import run_db_update
    from metax.database_builder.database_builder_mag import download_and_build_database
    
    
else:
    from ..utils.version import __version__
    from ..taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
    from ..utils.metax_updater import Updater
    from ..taxafunc_ploter.heatmap_plot import HeatmapPlot
    from ..taxafunc_ploter.basic_plot import BasicPlot
    from ..taxafunc_ploter.volcano_plot_js import VolcanoPlotJS
    from ..taxafunc_ploter.volcano_plot import VolcanoPlot
    from ..taxafunc_ploter.tukey_plot import TukeyPlot
    from ..taxafunc_ploter.bar_plot_js import BarPlot
    from ..taxafunc_ploter.sankey_plot import SankeyPlot
    from ..taxafunc_ploter.network_plot import NetworkPlot
    from ..taxafunc_ploter.trends_plot import TrendsPlot
    from ..taxafunc_ploter.trends_plot_js import TrendsPlot_js
    from ..taxafunc_ploter.pca_plot_js import PcaPlot_js
    from ..taxafunc_ploter.diversity_plot import DiversityPlot
    from ..taxafunc_ploter.sunburst_plot import SunburstPlot
    from ..taxafunc_ploter.treemap_plot import TreeMapPlot


    from ..peptide_annotator.metalab2otf import MetaLab2OTF
    from ..peptide_annotator.peptable_annotator import PeptideAnnotator

    from ..database_builder.database_builder_own import build_db
    from ..database_updater.database_updater import run_db_update
    from ..database_builder.database_builder_mag import download_and_build_database






class OTFAnalysisWorkflow:
    def __init__(
        self,
        otf_path: str,
        meta_path: str | None = None,
        output_dir: str = "output",
        peptide_col_name: str = "Sequence",
        protein_col_name: str = "Proteins",
        sample_col_prefix: str = "Intensity",
        any_df_mode: bool = False,
        custom_col_name: str = "Custom",
    ):

        self.output_dir = output_dir
        self.create_output_dir()
        
        logging.info("Initializing TaxaFuncAnalyzer to create the OTF object...")
        self.otf = TaxaFuncAnalyzer(
            df_path=otf_path,
            meta_path=meta_path,
            peptide_col_name=peptide_col_name,
            protein_col_name=protein_col_name,
            sample_col_prefix=sample_col_prefix,
            any_df_mode=any_df_mode,
            custom_col_name=custom_col_name,
        )
        self.BasicPlot = BasicPlot(self.otf)
        
    def create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            # check if the directory is not empty
            if os.listdir(self.output_dir):
                logging.warning(f"Output directory {self.output_dir} is not empty. Files might be overwritten.")
                           
        
    def plot_taxa_stats_pie(self):
        logging.info("Plotting taxa stats pie...")
        fig = self.BasicPlot.plot_taxa_stats_pie(theme='Auto',  res_type='pic')
        fig.savefig(os.path.join(self.output_dir, "taxa_stats_pie.png"))
        
        
    def plot_taxa_number_bar(self, min_peptide_num: int = 3):
        logging.info("Plotting taxa number bar...")
        fig = self.BasicPlot.plot_taxa_number(theme='Auto', peptide_num=min_peptide_num,
                                                   res_type='pic').get_figure()
        fig.savefig(os.path.join(self.output_dir, f"taxa_number_bar(min {min_peptide_num} pep).png"))
        
    def plot_prop_stats_for_each_func(self):
        logging.info("Plotting prop stats for each function...")
        # create a directory to store the plots for fucntions
        func_dir = os.path.join(self.output_dir, 'function_proption_stats')
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)
            
        for func in self.otf.func_list: # type: ignore
            logging.info(f"Plotting prop stats: {func}...")
            fig =self.BasicPlot.plot_prop_stats(func_name = func, res_type='pic').get_figure()
            fig.savefig(os.path.join(func_dir, f"{func}.png"))
            
    def plot_basic_without_setting_otf(self):
        logging.info("Plotting basic plots without setting OTF object...")
        self.plot_taxa_stats_pie()
        self.plot_taxa_number_bar()
        self.plot_prop_stats_for_each_func()
    
    
    # TODO:
    # create taxa, function, otfs, peptides directory respectively to store the results(tabele and figs)
    
    ## BASIC
    # PCA (peptide, function, taxa, otf)
    # corrlation 
    # bar of number, 
    # violin of intensity
    # upset plot
    # Alpha diversity
    # Beta diversity
    # Taxa composition(trermap, sankey, sunburst)
    ## ADVANCED
    # top 20 taxa, function, otfs bar,sankey
    
    ## Create a HTML file to show the results




if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    otf_path = os.path.join(current_dir, "../data/example_data/Example_OTF.tsv")
    meta_path = os.path.join(current_dir, "../data/example_data/Example_Meta.tsv")
    output_dir = os.path.join(current_dir, "output")
    # create a workflow object
    workflow = OTFAnalysisWorkflow(
        otf_path = otf_path,
        meta_path = meta_path,
        output_dir = output_dir

    )
    
    # plot the basic plots
    workflow.plot_basic_without_setting_otf()
    
    logging.info("OTF Analysis workflow finished.")