from pyecharts import options as opts
from pyecharts.charts import Bar
from .get_distinct_colors import GetDistinctColors
from matplotlib import pyplot as plt


class BarPlot:
    def __init__(self, tfobj, theme='white'):
        self.tfa =  tfobj
        self.get_distinct_colors = GetDistinctColors().get_distinct_colors
        self.theme = theme

    # plot intensity line for each sample
    # Example: plot_intensity_line(sw, func_name=func_name, taxon_name=taxon_name, fig_size=(30,20))

    def rename_taxa(self, df):
        first_index = df.index[0]
        index_list = df.index.tolist()
        if 'd__' in first_index:
            if '<' not in first_index:
                new_index_list = [i.split('|')[-1] for i in index_list]
            else:
                new_index_list = [
                    f'{i.split(" <")[0].split("|")[-1]} <{i.split(" <")[1][:-1]}>'
                    for i in index_list
                ]
            df.index = new_index_list
        return df

    def _add_group_name_to_sample(self, df):
        #rename columns (sample name)
        col_names = df.columns.tolist()
        meta_df = self.tfa.meta_df
        meta_name = self.tfa.meta_name
        groups_list = []
        new_col_names = []
        for i in col_names:
            group = meta_df[meta_df['Sample'] == i]
            group = group[meta_name].values[0]
            new_col_names.append(f'{i} ({group})')
            groups_list.append(group)
        df.columns = new_col_names
        return df
    
    def _get_modfied_df(self, df= None, 
                        taxon_name:str|None=None, sample_list:list|None = None, 
                        func_name:str|None =None, peptide_seq=None, 
                        rename_taxa:bool=False, rename_sample:bool=True, 
                        plot_mean:bool=False, sub_meta:str="None", plot_percent:bool=False):
        """
        Get modified df for plotting
        Returns:
        - df: pd.DataFrame
        - rename_sample: bool
        """
        if df is None:
            df = self.tfa.GetMatrix.get_intensity_matrix(taxon_name=taxon_name, func_name=func_name, 
                                                         peptide_seq=peptide_seq, sample_list= sample_list)
            if df.empty:
                raise ValueError('No data to plot')
        
        if plot_mean:
            if sub_meta != "None":
                print(f'Using sub_meta: {sub_meta}, ignore plot_mean')
            else:
                df = self.tfa.BasicStats.get_stats_mean_df_by_group(df)
                
            rename_sample = False

        # rename taxa
        if rename_taxa:
            df = self.rename_taxa(df)
        #rename columns (sample name)
        if rename_sample and sub_meta == "None":
            df = self._add_group_name_to_sample(df)

        if plot_percent:
            # transform to percentage of each column
            df = df.div(df.sum(axis=0), axis=1) * 100
            
        return df, rename_sample
        
    
    def plot_intensity_bar_sns(self, taxon_name:str|None=None, sample_list:list|None = None, 
                           func_name:str|None =None, peptide_seq=None, 
                           width:int=12, height:int=8, df= None, 
                           title:str|None =None, rename_taxa:bool=False, 
                           show_legend:bool=True, font_size:int=10,
                           rename_sample:bool=True, plot_mean:bool=False,
                           plot_percent:bool=False, sub_meta:str="None", plt_theme:str='Auto'):
        
        df, rename_sample = self._get_modfied_df(df, taxon_name, sample_list, func_name, peptide_seq, 
                                                 rename_taxa, rename_sample, plot_mean, sub_meta, plot_percent)
        if sub_meta != "None":
            df, _ = self.tfa.BasicStats.get_combined_sub_meta_df(df=df, sub_meta=sub_meta, rename_sample=rename_sample, plot_mean=plot_mean)
        
        colormap = GetDistinctColors().get_distinct_colors(len(df.index))
        if plt_theme == 'Auto':
            plt.style.use('default')
        else:
            plt.style.use(plt_theme)
            
        fig, ax = plt.subplots(figsize=(width, height))
        df.T.plot(kind='bar', stacked=True, ax=ax, color=colormap, width=0.95)

        ax.set_title(title, fontsize=font_size)
        ax.set_xlabel('Group' if plot_mean else 'Sample', fontsize=font_size)
        ax.set_ylabel('Percentage' if plot_percent else 'Intensity', fontsize=font_size)
        ax.tick_params(axis='both', which='major', labelsize=font_size)
        if show_legend:            
            ax.legend(title='Taxa' if rename_taxa else 'Sample', title_fontsize=font_size, fontsize=font_size, loc='center left', bbox_to_anchor=(1, 0.5))
        else:
            ax.get_legend().remove()
            
        plt.tight_layout()
        plt.show()
        
        return fig
    
    
    
    def plot_intensity_bar_js(self, taxon_name:str|None=None, sample_list:list|None = None, 
                           func_name:str|None =None, peptide_seq=None, 
                           width:int=1200, height:int=800, df= None, 
                           title:str|None =None, rename_taxa:bool=False, 
                           show_legend:bool=True, font_size:int=10,
                           rename_sample:bool=True, plot_mean:bool=False,
                           plot_percent:bool=False, sub_meta:str="None",
                           show_all_labels:tuple = (False, False), use_3d:bool=False
                           ):
        df, rename_sample = self._get_modfied_df(df, taxon_name, sample_list, func_name, peptide_seq,
                                                 rename_taxa, rename_sample, plot_mean, sub_meta, plot_percent)

        if use_3d:
            if sub_meta == "None":
                use_3d = False
                print('sub_meta must be provided for 3D bar plot, use 2D bar plot instead')
            
        col_num = len(df)
            
        # Create title
        if title is None:
            if peptide_seq is not None:
                title = f'The intensity of {peptide_seq}'
            else:
                renamed_taxon = taxon_name.split('|')[-1] if rename_taxa and taxon_name else taxon_name
                
                # If only taxon_name exists
                if renamed_taxon and not func_name:
                    title = f'{renamed_taxon}'
                
                # If only func_name exists
                elif func_name and not renamed_taxon:
                    title = f'{func_name}'
                
                # If both taxon_name and func_name exist
                elif renamed_taxon and func_name:
                    title = f'{renamed_taxon}\n{func_name}'
                
        
        global_opts_params = {
            "legend_opts": opts.LegendOpts(
                type_="scroll",
                page_icon_size=8,
                selector=[
                    {"type": "all", "title": "All"},
                    {"type": "inverse", "title": "Inverse"},
                ],
                pos_left="right",
                orient="vertical",
                pos_top="5%",
                border_width=0,
                textstyle_opts=opts.TextStyleOpts(font_size=font_size),
            )
            if show_legend
            else opts.LegendOpts(is_show=False),
            "datazoom_opts": [
                opts.DataZoomOpts(
                    type_="inside",
                    range_start=0,
                    range_end=100,
                )
            ],
            "toolbox_opts": opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="left",
                pos_top="bottom",
                feature=opts.ToolBoxFeatureOpts(
                    save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                        type_="png",
                        background_color="black" if self.theme == 'dark' else "white",
                        pixel_ratio=3,
                        title="Save as PNG",
                    ),
                    restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                    data_zoom=opts.ToolBoxFeatureDataZoomOpts(
                        zoom_title="Zoom", back_title="Back"
                    ),
                    data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                    magic_type=opts.ToolBoxFeatureMagicTypeOpts(
                        line_title="Line",
                        bar_title="Bar",
                        stack_title="Stack",
                        tiled_title="Tiled",
                    ),
                ),
            ),
            "title_opts": opts.TitleOpts(title=f"{title}", pos_left="center"),
            "xaxis_opts": opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(
                    rotate=25,
                    font_size=font_size,
                    interval=0 if show_all_labels[0] else None,
                ),
            ),
            "yaxis_opts": opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(
                    font_size=font_size, 
                    interval=0 if show_all_labels[1] else None,
                ),
                max_=100.02
                if plot_percent
                else None,  # set max value to 100.02 rather than 100: the sum of some columns may more than 100 due to float number
            ),
        }
        
        
        if not use_3d:
            if sub_meta != "None":
                df, _ = self.tfa.BasicStats.get_combined_sub_meta_df(df=df, sub_meta=sub_meta, rename_sample=rename_sample, plot_mean=plot_mean)
            colors = self.get_distinct_colors(col_num, convert=True)
                
            c = (
                Bar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px", theme=self.theme))
                .add_xaxis(list(df.columns))
            )

            for i, name in enumerate(df.index):
                color = colors[i]
                c.add_yaxis(name, list(df.loc[name, :]), 
                            stack="stack1", 
                            category_gap="5%", 
                            itemstyle_opts=opts.ItemStyleOpts(color=color, border_type=None, border_width=0),
                            emphasis_opts=opts.EmphasisOpts(focus='series'),
                            )


                c.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

            c.set_global_opts(**global_opts_params)
            return c
        
        else: # plot 3D bar plot
            from pyecharts.charts import Bar3D

            sample_groups = {sample: self.tfa.get_group_of_a_sample(sample, self.tfa.meta_name) for sample in df.columns}
            individual_groups = {sample: self.tfa.get_group_of_a_sample(sample, sub_meta) for sample in df.columns}

            # sort groups
            unique_meta_groups = sorted(list(set(sample_groups.values())))
            unique_individual_groups = sorted(list(set(individual_groups.values())))
            
            # assign color to each item
            item_colors = GetDistinctColors().get_distinct_colors(num=len(df.index), convert=True)

            # 合并同一meta和submeta的样本，计算平均值
            grouped_data = df.T.groupby([sample_groups, individual_groups]).mean().T

            data = []
            for _, (meta_group, submeta_group) in enumerate(grouped_data.columns):
                meta_group_index = unique_meta_groups.index(meta_group)
                submeta_group_index = unique_individual_groups.index(submeta_group)
                for index, item in enumerate(grouped_data.index):
                    z = grouped_data.at[item, (meta_group, submeta_group)]
                    color = item_colors[index]
                    data.append([meta_group_index, submeta_group_index, z, color, item, meta_group, submeta_group])


            bar3d = Bar3D(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px", theme=self.theme))

            for index, item in enumerate(grouped_data.index):
                series_data = []
                for d in data:
                    x = d[0]
                    y = d[1]
                    z = d[2]
                    color = d[3]
                    item_name = d[4]
                    meta_group = d[5]
                    submeta_group = d[6]

                    if item == item_name:
                        series_data.append([x, y, z, meta_group, submeta_group])

                bar3d.add(
                    series_name=item,
                    data=series_data,
                    shading="lambert",
                    xaxis3d_opts=opts.Axis3DOpts(data=unique_meta_groups, type_="category", name=" ", 
                                                 axislabel_opts=opts.LabelOpts(rotate=45, 
                                                                               font_size=font_size, 
                                                                               interval=0 if show_all_labels[0] else None,
                                                                               color="white" if self.theme == 'dark' else None,
                                                                               )),
                    yaxis3d_opts=opts.Axis3DOpts(data=unique_individual_groups, type_="category", name=" ", 
                                                 axislabel_opts=opts.LabelOpts(font_size=font_size,
                                                                               interval=0 if show_all_labels[1] else None,
                                                                               color="white" if self.theme == 'dark' else None,
                                                                               )),
                    zaxis3d_opts=opts.Axis3DOpts(type_="value", name=" "),
                    itemstyle_opts=opts.ItemStyleOpts(color=item_colors[index], border_type=None, border_width=0),
                )


            bar3d.set_series_opts(stack="stack1")

            global_opts_params["toolbox_opts"] = opts.ToolboxOpts(
                is_show=True,
                orient="vertical",
                pos_left="left",
                pos_top="bottom",
                feature=opts.ToolBoxFeatureOpts( 
                                                save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(type_="png", 
                                                                                                background_color="black" if self.theme == 'dark' else "white", 
                                                                                                pixel_ratio=3, 
                                                                                                title="Save as PNG"),
                                                restore=opts.ToolBoxFeatureRestoreOpts(title="Restore"),
                                                data_zoom=opts.ToolBoxFeatureDataZoomOpts(zoom_title="Zoom", 
                                                                                        back_title="Back"),
                                                data_view=opts.ToolBoxFeatureDataViewOpts(title="Data View"),
                                                magic_type=opts.ToolBoxFeatureMagicTypeOpts(line_title="Line", 
                                                                                            bar_title="Bar", 
                                                                                                stack_title="Stack",
                                                                                                tiled_title="Tiled"),
                                                
                                                ),
                )
            global_opts_params.pop("datazoom_opts")
            global_opts_params.pop("xaxis_opts")
            global_opts_params.pop("yaxis_opts")
            
            bar3d.set_global_opts(**global_opts_params)
            
            return bar3d
            
            
            
            
            
            
            
            
            
    
    

