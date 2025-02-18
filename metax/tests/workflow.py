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

else:
    from ..utils.version import __version__
    from ..taxafunc_analyzer.analyzer import TaxaFuncAnalyzer
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
        self.data_preprocess_params: dict = {"outlier_params":{}, "data_preprocess_params":{}, "peptide_num_threshold":{}, "quant_method":'sum'}
        self.set_data_preprocess_params()
        
        self.tfa = TaxaFuncAnalyzer(
            df_path=otf_path,
            meta_path=meta_path,
            peptide_col_name=peptide_col_name,
            protein_col_name=protein_col_name,
            sample_col_prefix=sample_col_prefix,
            any_df_mode=any_df_mode,
            custom_col_name=custom_col_name,
        )
        self.filter_func_list()
        self.BasicPlot = BasicPlot(self.tfa)
        
        
        
    def set_data_preprocess_params(self,
                                   outlier_params = {'detect_method': 'missing-value', 'handle_method': 'fillzero',
                                            "detection_by_group" : None, "handle_by_group": None},
                                    data_preprocess_params = {
                                                            'normalize_method': 'None', 
                                                            'transform_method': "None",
                                                            'batch_meta': 'None', 
                                                            'processing_order': ['transform', 'normalize', 'batch']},
                                    peptide_num_threshold = {'taxa': 3, 'func': 3, 'taxa_func': 3},
                                    quant_method='sum'):
        
        self.data_preprocess_params = {
            "outlier_params": outlier_params,
            "data_preprocess_params": data_preprocess_params,
            "peptide_num_threshold": peptide_num_threshold,
            "quant_method": quant_method
        }
        
    def filter_func_list(self):
        func_list = self.tfa.func_list
        if not func_list:
            raise ValueError("tfa.func_list is empty. Please set the function list first.")
        
        remove_list = ['protein_id', 'EC_DE', 'EC_AN', 'EC_CC', 'EC_CA', 
                       'KEGG_Pathway', 'KEGG_ko', 'None_func']
        func_list = [i for i in func_list if i not in remove_list]
        self.tfa.func_list = func_list
            
    
        
    def create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        else:
            # check if the directory is not empty
            if os.listdir(self.output_dir):
                logging.warning(f"Output directory {self.output_dir} is not empty. Files might be overwritten.")
        os.makedirs(os.path.join(self.output_dir, "basic_plots"), exist_ok=True)
                           
        
    def plot_taxa_stats_pie(self):
        logging.info("Plotting taxa stats pie...")
        fig = self.BasicPlot.plot_taxa_stats_pie(theme='Auto',  res_type='pic')
        fig.savefig(os.path.join(self.output_dir, "basic_plots/taxa_stats_pie.png"))
        
        
    def plot_taxa_number_bar(self, min_peptide_num: int = 3):
        logging.info("Plotting taxa number bar...")
        fig = self.BasicPlot.plot_taxa_number(theme='Auto', peptide_num=min_peptide_num,
                                                   res_type='pic').get_figure()
        fig.savefig(os.path.join(self.output_dir, "basic_plots/taxa_number_bar.png"))
        
    def plot_prop_stats_for_each_func(self):
        logging.info("Plotting prop stats for each function...")
        # create a directory to store the plots for fucntions
        func_dir = os.path.join(self.output_dir, 'basic_plots/function_proption_stats')
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)
            
        for func in self.tfa.func_list: # type: ignore
            logging.info(f"Plotting prop stats: {func}...")
            fig =self.BasicPlot.plot_prop_stats(func_name = func, res_type='pic').get_figure()
            fig.savefig(os.path.join(func_dir, f"{func}.png"))
            
    
    def create_taxa_tables(self):
        logging.info("Creating taxa tables...")
        taxa_dir = os.path.join(self.output_dir, "taxa_tables")
        if not os.path.exists(taxa_dir):
            os.makedirs(taxa_dir)
        for i in ['m','s','g', 'f', 'o', 'c', 'p', 'd']:
            logging.info(f"Creating taxa table: {i}...")
            df_temp_taxa = self.tfa._create_taxa_table_only_from_otf(level=i, **self.data_preprocess_params)
            # remove "peptide_num" column if it exists
            df_temp_taxa = df_temp_taxa.drop(columns=['peptide_num'], errors='ignore')
            df_temp_taxa.to_csv(os.path.join(taxa_dir, f"taxa_table_{i}.tsv"), sep='\t', index=False)
            logging.info(f"Taxa table {i} created.")
        logging.info("All taxa tables created.")
    
    def create_function_tables(self):
        logging.info("Creating function tables...")
        func_dir = os.path.join(self.output_dir, "function_tables")
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)

        for func_name in self.tfa.func_list: # type: ignore
            df_temp_func = self.tfa._create_func_table_only_from_otf(func_name=func_name, func_threshold=1.00,
                        keep_unknow_func=False,
                        split_func=False, split_func_params = {'split_by': '|', 'share_intensity': False},
                        **self.data_preprocess_params)

            df_temp_func = df_temp_func.drop(columns=['peptide_num'], errors='ignore')
            df_temp_func.to_csv(os.path.join(func_dir, f"function_table_{func_name}.tsv"), sep='\t', index=False)
            logging.info(f"Function table {func_name} created.")
        logging.info("All function tables created.")
    
    def create_otf_tables(self):
        logging.info("Creating OTF tables...")
        otf_dir = os.path.join(self.output_dir, "otf_tables")
        if not os.path.exists(otf_dir):
            os.makedirs(otf_dir)
         #only for species level for now
        logging.info("Creating OTF table: species level...")
        create_protein_table_flag = True
        for func_name in self.tfa.func_list: # type: ignore
            logging.info(f"Creating OTF table for function: {func_name}...")
            self.tfa.set_func(func_name)
            self.tfa.set_multi_tables(level='s', 
                    keep_unknow_func=False,
                    sum_protein=create_protein_table_flag, 
                    sum_protein_params = {'method': 'anti-razor', 'by_sample': False, 'rank_method': 'unique_counts', 'greedy_method': 'heap', 'peptide_num_threshold': 3},
                    split_func=False, split_func_params = {'split_by': '|', 'share_intensity': False},
                    taxa_and_func_only_from_otf=False, func_threshold=1.00,
                    **self.data_preprocess_params)
            if create_protein_table_flag:
                create_protein_table_flag = False
                df_protein = self.tfa.get_df('protein')
                df_protein.to_csv(os.path.join(otf_dir, "protein_table.tsv"), sep='\t', index=False)
                
            df_temp_otf = self.tfa.get_df('taxa_func')
            df_temp_otf.to_csv(os.path.join(otf_dir, f"otf_table_{func_name}.tsv"), sep='\t', index=False)
                

        
    # # TODO:
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
    
    
    def plot_basic_without_setting_otf(self):
        logging.info("Plotting basic plots without setting OTF object...")
        self.plot_taxa_stats_pie()
        self.plot_taxa_number_bar()
        self.plot_prop_stats_for_each_func()
        # create taxa and function tables
        self.create_taxa_tables()
        self.create_function_tables()
        # create OTFs table
        self.create_otf_tables()
        
        




if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    otf_path = os.path.join(current_dir, "../data/example_data/Example_OTF.tsv")
    meta_path = os.path.join(current_dir, "../data/example_data/Example_Meta.tsv")
    output_dir = os.path.join(current_dir, "../../.local_tests/report_output")
    # create a workflow object
    workflow = OTFAnalysisWorkflow(
        otf_path = otf_path,
        meta_path = meta_path,
        output_dir = output_dir

    )
    
    # plot the basic plots
    workflow.plot_basic_without_setting_otf()
    
    logging.info("OTF Analysis workflow finished.")