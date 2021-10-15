# reading in SEQC results

import warnings, numpy as np, pandas as pd, scipy.sparse as sp, scanpy as sc, csv, matplotlib, matplotlib.pyplot as plt, tarfile, phenograph, seaborn as sns
from matplotlib import rcParams
from MulticoreTSNE import MulticoreTSNE as TSNE
from scipy.sparse import csgraph
from sklearn.metrics import adjusted_rand_score
#import ipywidgets
#from ipyfilechooser import FileChooser

sc.settings.verbosity = 0 # verbosity: errors (0), warnings (1), info (2), hints (3)  # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.set_figure_params(dpi=80, dpi_save=300, color_map='viridis', vector_friendly=True, transparent=True)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
sc.logging.print_header()
print("phenograph==", phenograph.__version__)


def import_seqc_data(path, sample_name):
    PATH_TO_COUNT_CSV = path + sample_name
    # import csv
    raw_counts = pd.read_csv(PATH_TO_COUNT_CSV, index_col=0, header=0)
    # and label the index column with name 'cell_barcodes'
    raw_counts.index.name = 'cell_barcodes'
    # convert indices to strings instead of integers for compatibility with scanpy
    raw_counts.index = raw_counts.index.astype(str)
    # python automatically converts duplicate column names to numbered column names,
    # e.g. 'X', 'X.1', 'X.2' etc. We can import the original column names from our CSV file:
    with open(PATH_TO_COUNT_CSV, "r") as f:
        reader = csv.reader(f)
        original_column_names = next(reader)
    # remove the first entry of this list, it belongs to the index column
    gene_names = original_column_names[1:]
    # now transpose the dataframe (for compatibility with panda's groupby function), 
    # then group by gene names, and add up the counts for genes with the same name
    raw_counts_transposed = raw_counts.T
    raw_counts_transposed_clean = raw_counts_transposed.groupby(gene_names, axis='index', sort=False).agg('sum')
    # transpose back
    raw_counts_clean = raw_counts_transposed_clean.T
    # remove CLUSTER column:
    if 'CLUSTER' in raw_counts_clean.columns:
        raw_counts_clean.drop(columns='CLUSTER', inplace=True)
    # convert index type to string for compatibility with scanpy
    raw_counts_clean.index = raw_counts_clean.index.astype('str')
    adata = sc.AnnData(X = raw_counts_clean)
    return adata


# we will calculate some standard qc (quality control) metrics using the scanpy calculate_qc_metrics function. To see which qc metrics it calculates, take a look at the .obs and .var dataframes after running the command. We add the inplace=True argument to ensure that scanpy adds the results of this command to our adata object.

def calc_QC_metrics(anndata_object):
    # calculate some standard qc metrics with 
    sc.pp.calculate_qc_metrics(anndata_object, inplace=True)
    #store all unfiltered/unprocessed data prior to downstream analysis
    anndata_object.obs['original_total_counts'] = anndata_object.obs['total_counts']
    anndata_object.obs['log10_original_total_counts'] = np.log10(anndata_object.obs['original_total_counts'])
    mito_genes = anndata_object.var_names.str.startswith('MT-')
    # for each cell compute fraction of counts in mito genes vs. all genes
    #anndata_object.obs['mito_frac'] = np.sum(anndata_object[:, mito_genes].X, axis=1) / np.sum(anndata_object.X, axis=1)
    anndata_object.obs['mito_frac'] = np.sum(anndata_object[:, mito_genes].X, axis=1) / np.sum(anndata_object.X, axis=1)
    # you will need to set the path here to the RB_genes file (download from here)
    path_to_RB_genes_file = '/data/brinkvd/kousaa/scRNAseq-repository/Data/RB_genes'
    with open(path_to_RB_genes_file,'r') as file:
        lines = file.readlines()
    RB_genes = [x.rstrip('\n') for x in lines]
    RB_genes_in_data = []
    data_genes = list(anndata_object.var.index)
    for gene in RB_genes:
        if gene in data_genes:
            RB_genes_in_data.append(gene)
    anndata_object_RB = anndata_object[:,RB_genes_in_data]
    RB_counts = np.sum(anndata_object_RB.X, axis=1)
    RBP_frac = RB_counts / anndata_object.obs['original_total_counts']
    anndata_object.obs['RBP_frac'] = RBP_frac
    
    

# plotting distribution of highly experssed gene colored by RBP fraction
def observe_RBP_effect(anndata_object):
    random_high_gene = np.random.choice(anndata_object.var.index[anndata_object.var['mean_counts']>1])
    scatter = sc.pl.scatter(
        anndata_object, x='total_counts',y=random_high_gene,
        title=random_high_gene + ' expression vs library size\n (colored by RBP fraction)', 
        color='RBP_frac',
        show=True
    )
    return(scatter)

# plotting distribution of highly experssed gene colored by RBP fraction
def observe_library_size_effect(anndata_object):
    high_expr_genes = anndata_object.var.index[anndata_object.var['mean_counts']>1]
    random_high_gene = np.random.choice(high_expr_genes)
    scatter = sc.pl.scatter(anndata_object,x='total_counts',y=random_high_gene,title=random_high_gene, show=True)
    return(scatter)

def remove_RBs(anndata_object):
    path_to_RBP_genes_file = '/data/brinkvd/kousaa/scRNAseq-repository/Data/RB_genes'
    with open(path_to_RBP_genes_file,'r') as file:
        lines = file.readlines()
    RBP_genes = [x.rstrip('\n') for x in lines]
    RBP_genes_in_data = []
    non_RBP_genes_in_data = []
    data_genes = list(anndata_object.var.index)
    for gene in data_genes:
        if gene in RBP_genes:
            RBP_genes_in_data.append(gene)
        else:
            non_RBP_genes_in_data.append(gene)
    # keep only non RBP genes
    adata_RBP_free = anndata_object[:,non_RBP_genes_in_data]
    # set your anndata_object to the filtered dataset
    anndata_object = adata_RBP_free
    return(anndata_object)
    
def observe_variance(anndata_object):
    fig = plt.figure(figsize=(10,5))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    # variance per principal component
    x = range(len(anndata_object.uns['pca']['variance_ratio']))
    y = anndata_object.uns['pca']['variance_ratio']
    ax1.scatter(x,y,s=4)
    ax1.set_xlabel('PC')
    ax1.set_ylabel('Fraction of variance explained\n')
    ax1.set_title('Fraction of variance explained per PC\n')
    # cumulative variance explained
    cml_var_explained = np.cumsum(anndata_object.uns['pca']['variance_ratio'])
    x = range(len(anndata_object.uns['pca']['variance_ratio']))
    y = cml_var_explained
    ax2.scatter(x,y,s=4)
    ax2.set_xlabel('PC')
    ax2.set_ylabel('Cumulative fraction of variance\nexplained')
    ax2.set_title('Cumulative fraction of variance\nexplained by PCs')
    fig.tight_layout()
    plot = plt.show
    return(plot)

    
# define a function that will give us the relevant output for the input k
def calc_clustering_characteristics(k,PCA):
    results = pd.Series()
    results['k'] = k
    results['communities'], results['graph'], results['Q'] = phenograph.cluster(PCA, k=k)
    # this piece calculates how many not-connected clusters there are 
    results['n_components'], label_components = csgraph.connected_components(results['graph'], directed = False)
    return results

def inspect_clustering_chars(ks, cluster_chars):
    fig = plt.figure(figsize=(15,5))
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    # plot the number of connected components for each k, and 
    # identify minimum value of k for which graph is fully connected:
    dot_size = 5
    x = ks
    y = np.log10([x['n_components'] for x in cluster_chars])
    ax1.plot(x,y,color='k',marker='o',linestyle='dashed',
        linewidth=1, markersize=5)
    #sns.despine() (don't know what this is for...)
    ax1.set_xlim(0,np.max(x))
    ax1.set_ylim(0,np.max(y)*1.1)
    ax1.set_xlabel('k')
    ax1.set_ylabel('log10(# connected components)')
    ax1.set_title('Minimum k for connected graph: {}'.format(ks[y==0][0]),size=14)
    
    # inspect and plot Q dynamics:
    dot_size = 5
    x = ks
    y = [x['Q'] for x in cluster_chars]
    ax2.plot(x,y,color='k',marker='o',linestyle='dashed',linewidth=1, markersize=5)
    #sns.despine() (don't know what this is for...)
    ax2.set_xlim(0,np.max(x))
    ax2.set_ylim(0,np.max(y)*1.1)
    ax2.set_xlabel('k')
    ax2.set_ylabel('Q modularity score')
    ax2.set_title('Q modularity score for different ks',fontsize=15)
    
    Rand_index_df = pd.DataFrame(np.zeros((len(ks), len(ks))),index=ks,columns=ks)
    Rand_index_df.index.name='k1'
    Rand_index_df.columns.name='k2'
    row_ind = 0
    for run1 in range(len(ks)):
        col_ind = 0
        for run2 in range(len(ks)):
            Rand_index_df.iloc[row_ind,col_ind] = adjusted_rand_score(cluster_chars[run1]['communities'],cluster_chars[run2]['communities'])
            col_ind = col_ind+1
        row_ind = row_ind+1
        
    # plot heatmap
    ax3.set_xlabel('k1')
    ax3.set_ylabel('k2')
    ax3.set_title('Adjusted Rand Score',fontsize=15)
    sns.set(font_scale=1)
    sns.heatmap(Rand_index_df, cmap=('coolwarm'), square=True, vmin=0, vmax=1)
    
    fig.tight_layout()
    plot = plt.show()
    return(Rand_index_df)