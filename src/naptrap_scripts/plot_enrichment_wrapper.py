
import argparse
from random import sample
from mpradb.db_plot import plot_enrichment
from mpradb.database.mpra_db import MPRA_DB


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',type = str,help = 'database path')
    parser.add_argument('--out',type = str,help='Database output path')
    parser.add_argument('--fig',type=str,default=None,help='Figure save path (Defaults to output path)')
    parser.add_argument('--selector',type=str,help='Selector to plot enrichment of (Only 1 selector can be plotted at a time)')
    parser.add_argument('--samples', nargs='*',default=None,help='Samples to plot, Samples must be present within the given selector (requires 1-2 samples seperated by a comma)')
    parser.add_argument('--klen',type=int,default=6,help='Length of Kmers to plot, klen length must be within range of that provided in buildb.toml (Defaults to 6)')
    parser.add_argument('--fig_format',type=str,default=None,help='Format to save the figures in (png, pdf, svg, etc), defaults to svg')
    args = parser.parse_args()

    db_path = args.db
    output_path = args.out
    fig_save_path = args.fig
    selector_name = args.selector
    sample_names = args.samples
    klen = args.klen
    fig_save_format = args.fig_format

    if  (sample_names == None) or len(sample_names) > 2:
        raise ValueError(f"Must provide 1-2 samples... Provided samples = {sample_names}")

    if fig_save_format != None:

        fig_save_format = fig_save_format.split('.')[-1]

    db = MPRA_DB(db_path=db_path,schema_path='doc/db_schema.sql',output_path = output_path)

    plot_enrichment.plot_enrichment(db=db, selector_name=selector_name,fig_save_path=fig_save_path,sample_names=sample_names, klen = klen,fig_save_format = fig_save_format)
    

if __name__ == '__main__':
    main()

