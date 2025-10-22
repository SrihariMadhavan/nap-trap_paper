import argparse
import subprocess
from pathlib import Path
import os

def main():
    
    parser = argparse.ArgumentParser(prog='NaP-TRAP pipeline', description='NaP-TRAP pipeline command')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    builddb_parser = subparsers.add_parser('build', help='Build the NaP-TRAP MPRA database (and generate the count and translation tables)')
    builddb_parser.add_argument('--toml_path', help = 'Path to the "build.toml" file (Absolute path), with instructions to build the database')
    
    count_reads_parser = subparsers.add_parser('count', help='Command to count the reads for each insert in the alignment files (Required prior `build` command to generate the DB and tables)')
    count_reads_parser.add_argument('-i',type = str,help = 'regex for pipseq files')
    count_reads_parser.add_argument('-o',type = str,help = 'output path')
    count_reads_parser.add_argument('-e',type = str,help = 'experiment id')
    count_reads_parser.add_argument('-t',type = str, help = 'temporary directory')
    count_reads_parser.add_argument('-p',type = str, help = 'number of processors')
    count_reads_parser.add_argument('--paired', action = 'store_true',default=False, help = 'does the sam file contain paired end mapped reads ')
    count_reads_parser.add_argument('-d1',type = str, default= '100', help = 'edit distance')
    count_reads_parser.add_argument('-m1', type = str, default = '10', help = 'minimum matches')
    count_reads_parser.add_argument('-d2',type = str, default= '100', help = 'edit distance')
    count_reads_parser.add_argument('-m2', type= str, default = '10', help = 'minimum matches')

    read_count_decision_parser = subparsers.add_parser('read_cutoff', help='Command to plot the number of inserts by read count (Optional but helpful in deciding cutoff in selectors)')
    read_count_decision_parser.add_argument('-i',type = str,help = 'count file paths (regex)')
    read_count_decision_parser.add_argument('-o',type = str,help = 'output directory')
    read_count_decision_parser.add_argument('-f',type = str,help = 'figure save format (defaults to svg)',default='svg')
    read_count_decision_parser.add_argument('-d',type = str,help = 'run name to analyse (Optional),run name must match the name of the replicate files',default='None')
 
    plot_enrichment_parser = subparsers.add_parser('plot_enrichment', help='Plot the enrichment of kmer features')
    plot_enrichment_parser.add_argument('--db',type = str,help = 'database path')
    plot_enrichment_parser.add_argument('--out',type = str,help='Database output path')
    plot_enrichment_parser.add_argument('--fig',type=str,default='None',help='Figure save path (Defaults to output path)')
    plot_enrichment_parser.add_argument('--selector',type=str,help='Selector to plot enrichment of (Only 1 selector can be plotted at a time)')
    plot_enrichment_parser.add_argument('--samples', nargs='*',default='None',help='Samples to plot, Samples must be present within the given selector (requires 1-2 samples seperated by a comma)')
    plot_enrichment_parser.add_argument('--klen',type=str,default='6',help='Length of Kmers to plot, klen length must be within range of that provided in buildb.toml (Defaults to 6)')
    plot_enrichment_parser.add_argument('--fig_format',type=str,default='svg',help='Format to save the figures in (png, pdf, svg, etc), defaults to svg')
 

    plot_replicates_parser = subparsers.add_parser('plot_replicates', help="Plot the correlation between sample replicates")
    plot_replicates_parser.add_argument('--db',type = str,help = 'database path')
    plot_replicates_parser.add_argument('--out',type = str,help='Database output path')
    plot_replicates_parser.add_argument('--fig',type=str,default='None',help='Figure save path (Defaults to output path)')
    plot_replicates_parser.add_argument('--selector',type=str,help='Selector to plot replicates of (Only 1 selector can be plotted at a time)')
    plot_replicates_parser.add_argument('--samples', nargs='*',default='None',help='List of samples to plot. If not used, plots all samples in the selector')
    plot_replicates_parser.add_argument('--fig_format',type=str,default='svg',help='Format to save the figures in (png, pdf, svg, etc), defaults to svg')


    args = parser.parse_args()
    
    if args.command == 'build':
        script_dir = Path(__file__).parent

        tomlpath = Path(args.toml_path)
        absolute_toml_path = tomlpath.resolve()

        build_db_path = str(script_dir / 'build_db.py')
        cmd = ['python', build_db_path, '--toml_path', absolute_toml_path]
        
        result = subprocess.run(cmd, cwd=str(script_dir.parent.parent))
        
    elif args.command == 'count':
        script_dir = Path(__file__).parent
        count_reads_path = str(script_dir / 'count_reads.py')
        cmd = ['python', count_reads_path, '-i', args.i , '-o', args.o , '-e' , args.e , '-t' , args.t ,
                '-p' , args.p  , '-d1', args.d1 , '-m1' , args.m1 , '-d2' , args.d2 , '-m2' , args.m2]
        if args.paired:
            cmd.extend('--paired')
        result = subprocess.run(cmd, cwd=os.getcwd())   

    elif args.command == 'read_cutoff':
        script_dir = Path(__file__).parent
        read_cutoff_path = str(script_dir / 'read_cutoff_decision.py')
        cmd = ['python', read_cutoff_path, '-i', args.i , '-o' , args.o , '-f' , args.f , '-d' , args.d]
        result = subprocess.run(cmd, cwd=os.getcwd())

    elif args.command == 'plot_replicates':
        script_dir = Path(__file__).parent
        print(script_dir)
        plot_replicates_path = str(script_dir / 'plot_replicates_wrapper.py')
        print(plot_replicates_path)
        cmd = ['python', plot_replicates_path, '--db', args.db , '--out', args.out ,
                '--fig' , args.fig , '--selector' , args.selector , '--samples' ,
                  ','.join(args.samples) if isinstance(args.samples,list) else args.samples ,
                  '--fig_format', args.fig_format ]
        result = subprocess.run(cmd, cwd=os.getcwd())  

    elif args.command == 'plot_enrichment':
        script_dir = Path(__file__).parent
        plot_enrichment_path = str(script_dir / 'plot_enrichment_wrapper.py')
        cmd = ['python', plot_enrichment_path, '--db', args.db , '--out', args.out ,
                '--fig' , args.fig , '--selector' , args.selector , '--samples' ,
                  ','.join(args.samples) if isinstance(args.samples,list) else args.samples ,
                    '--klen', args.klen , '--fig_format', args.fig_format ]
        print(cmd)
        result = subprocess.run(cmd, cwd=os.getcwd())    
    else:
        parser.print_help()

    return


if __name__ == '__main__':
    main()