import pandas as pd
import numpy as np
from matplotlib.collections import LineCollection
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import math
import inspect

class TrendsPlot:
    def __init__(self, tfobj):
        self.tfobj = tfobj

    def prepare_trends(self, df, num_cluster):
        
        # Load the data
        df = self.tfobj.BasicStats.get_stats_mean_df_by_group(df)
        # Standardize the data
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(df.T).T

        # Create scaled DataFrame
        scaled_df = pd.DataFrame(scaled_values, columns=df.columns, index=df.index)

        # Perform KMeans clustering
        n_clusters = num_cluster
        kmeans_kwargs = dict(n_clusters=n_clusters, init='k-means++')
        kmeans_signature = inspect.signature(KMeans)
        n_init_param = kmeans_signature.parameters.get("n_init")
        if n_init_param is not None and n_init_param.default == 'auto':
            kmeans_kwargs["n_init"] = 'auto'
        else:
            kmeans_kwargs["n_init"] = 10
        kmeans = KMeans(**kmeans_kwargs)
        clusters = kmeans.fit_predict(scaled_df)

        # Add the cluster labels to the DataFrame
        clustered_df = scaled_df.copy()
        clustered_df['Cluster'] = clusters

        return clustered_df

    def plot_trends(self, df, num_cluster, width=15, height=5, title='Cluster', font_size=10,
                    num_col=1, clustered_df=None):
        if clustered_df is None:
            clustered_df = self.prepare_trends(df, num_cluster)
        n_clusters = num_cluster
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}
        sns.set_theme(style="ticks", rc=custom_params)
        palette = sns.color_palette("dark", n_clusters)

        try:
            # Calculate the number of rows based on num_col
            num_row = math.ceil(n_clusters / num_col)
            
            fig, axs = plt.subplots(num_row, num_col, figsize=(width, height * num_row))
            axs = np.atleast_1d(axs).ravel()  # Flatten the axs array for easy iteration

            for i in range(n_clusters):
                cluster_data = clustered_df[clustered_df['Cluster'] == i]
                avg_data = cluster_data.drop('Cluster', axis=1).mean()

                values = cluster_data.drop(columns='Cluster').to_numpy(dtype=float)
                x = np.arange(values.shape[1])
                segments = np.empty((len(values), len(x), 2), dtype=float)
                segments[:, :, 0] = x
                segments[:, :, 1] = values
                axs[i].add_collection(LineCollection(segments, colors='lightgrey', linewidths=1.5))
                axs[i].plot(x, avg_data.to_numpy(), color=palette[i], linewidth=2)
                axs[i].set_xticks(x, labels=[str(column) for column in avg_data.index])
                axs[i].autoscale_view()

                axs[i].set_title(f'{title} {i+1}', fontsize=font_size+2, fontweight='bold')
                axs[i].set_xlabel('Group', fontsize=font_size-2)
                axs[i].set_ylabel('Standardized Value', fontsize=font_size-2)
                axs[i].tick_params(axis='x', rotation=90)  # Rotate x-axis labels
                axs[i].tick_params(axis='both', which='major', labelsize=font_size)

            # Remove any empty subplots if n_clusters is not a perfect multiple of num_col
            for ax in axs[n_clusters:]:
                ax.remove()

            plt.tight_layout()
            plt.close()
            return fig, clustered_df
        except Exception as e:
            plt.close()
            raise e
