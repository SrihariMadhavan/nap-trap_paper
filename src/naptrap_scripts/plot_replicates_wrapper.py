import argparse
from random import sample
from mpradb.db_plot import plot_replicates, plot_replicate_heatmap
from mpradb.database.mpra_db import MPRA_DB


def main():
    
    parser = argparse.ArgumentParser(description= "Plot the correlation between sample replicates")
    parser.add_argument('--db',type = str,help = 'database path')
    parser.add_argument('--out',type = str,help='Database output path')
    parser.add_argument('--fig',type=str,default='None',help='Figure save path (Defaults to output path)')
    parser.add_argument('--selector',type=str,help='Selector to plot replicates of (Only 1 selector can be plotted at a time)')
    parser.add_argument('--samples', nargs='*',default=['None'],help='List of samples to plot. If not used, plots all samples in the selector')
    parser.add_argument('--fig_format',type=str,default='svg',help='Format to save the figures in (png, pdf, svg, etc), defaults to svg')

    args = parser.parse_args()

    db_path = args.db
    output_path = args.out
    fig_save_path = args.fig if args.fig != 'None' else None
    selector_name = args.selector
    sample_names = args.samples if 'None' not in args.samples  else None

    fig_save_format = args.fig_format



    fig_save_format = fig_save_format.split('.')[-1]


    db = MPRA_DB(db_path=db_path,schema_path='doc/db_schema.sql',output_path = output_path)

    plot_replicates.plot_replicates(db=db, selector_name=selector_name,output_path = fig_save_path,sample_names = sample_names,fig_save_format=fig_save_format)
    plot_replicate_heatmap.plot_replicate_heatmap(db=db,selector_name=selector_name,output_path = fig_save_path, sample_names = sample_names, fig_save_format = fig_save_format)
    

if __name__ == '__main__':
    main()