import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

class TrendsPlot:
    def __init__(self, tfobj):
        self.tfobj =  tfobj
        
    def plot_trends(self, df, num_cluster, width=15, height=5, title='Cluster'):
        
        # Load the data
        df = self.tfobj.BasicStats.get_stats_mean_df_by_group(df)
        # Standardize the data
        scaler = StandardScaler()
        scaled_values = scaler.fit_transform(df.T).T

        # Create scaled DataFrame
        scaled_df = pd.DataFrame(scaled_values, columns=df.columns, index=df.index)

        # Perform KMeans clustering
        n_clusters = num_cluster
        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', n_init='auto')
        clusters = kmeans.fit_predict(scaled_df)

        # Add the cluster labels to the DataFrame
        clustered_df = scaled_df.copy()
        # 不再重新排序列
        # adding the cluster column
        clustered_df['Cluster'] = clusters
        
        custom_params = {"axes.spines.right": False, "axes.spines.top": False}

        sns.set_theme(style="ticks", rc=custom_params)
        palette = sns.color_palette("dark", n_clusters)
        try:    
            fig, axs = plt.subplots(n_clusters, 1, figsize=(width, height*n_clusters))
            if n_clusters == 1:
                axs = [axs]
            for i in range(n_clusters):
                cluster_data = clustered_df[clustered_df['Cluster'] == i]
                avg_data = cluster_data.drop('Cluster', axis=1).mean()

                for j in range(cluster_data.shape[0]):
                    sns.lineplot(data=cluster_data.iloc[j, :-1], ax=axs[i], color='lightgrey', legend=False)

                sns.lineplot(data=avg_data, ax=axs[i], color=palette[i], linewidth=2)

                axs[i].set_title(f'{title} {i+1}')
                axs[i].set_xlabel('Group')
                axs[i].set_ylabel('Standardized Value')
                axs[i].tick_params(axis='x', rotation=90)  # Rotate x-axis labels

            plt.close()
            return fig, clustered_df
        except Exception as e:
            plt.close()
            raise e
