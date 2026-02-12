import numpy as np
import pandas as pd
import os
from pyfaidx import Fasta

def insert_sequence_tables(db,out_path):
    insert_out_path = f"{out_path}insert_sequence_table/"
    if not os.path.exists(insert_out_path):
        os.makedirs(insert_out_path)
    insert_df = db[['reporter_name','reporter_id','insert_sequence','tags']].to_df()

    insert_df.to_csv(f'{insert_out_path}insert_sequence_list_table.csv',index=False)

    return

def all_raw_counts_csv(db,fasta_path,out_path):
    all_counts_out_path = f"{out_path}all_raw_counts/"
    if not os.path.exists(all_counts_out_path):
        os.makedirs(all_counts_out_path)

    df1 = db[['reporter_id','run_type','run_name','replicate_name','raw_count','normalized_count']].to_df()
    df2 = db[['reporter_id','reporter_name']].to_df()
    df = df2.merge(df1, on = 'reporter_id')
    df3 = db[['run_name','sample_name']].to_df()
    df = df.merge(df3, on = 'run_name')

    df['info'] = df.apply(lambda x:f"{x['sample_name']}_{x['run_type']}_{x['replicate_name'].split('-')[-1]}" , axis=1 )

    ndf = df.pivot(index='reporter_name', columns='info',values=['raw_count'])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)

    reporters_present_set = set(ndf['reporter_name'].tolist())

    fasta_file = Fasta(fasta_path)

    reporters_full_set = set(['#'.join(key.split('#')[:-1]) for key in fasta_file.keys()])

    reporters_absent_list = list(reporters_full_set - reporters_present_set)

    buffer = pd.DataFrame(0, index = range(len(reporters_absent_list)), columns = ndf.columns)
    buffer['reporter_name'] = reporters_absent_list

    ndf = pd.concat([ndf,buffer])

    ndf.to_csv(f'{all_counts_out_path}all_raw_counts.csv',index=False)
    print(f'Raw counts generated in {all_counts_out_path}')

    ndf = df.pivot(index='reporter_name', columns='info',values=['normalized_count'])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)
    buffer = pd.DataFrame(0, index = range(len(reporters_absent_list)), columns = ndf.columns)
    buffer['reporter_name'] = reporters_absent_list
    ndf = pd.concat([ndf,buffer])

    ndf.to_csv(f'{all_counts_out_path}all_normalized_counts.csv',index=False)
    print(f'Norm counts generated in {all_counts_out_path}')

    
    return


def unfiltered_tables(db,sample_data_groups,selector_out_path):
    unfiltered_path = f"{selector_out_path}unfiltered/"
    if not os.path.exists(unfiltered_path):
        os.makedirs(unfiltered_path)


    df1 = db[['reporter_id','run_type','run_name','replicate_name','raw_count','normalized_count']].to_df()
    df2 = db[['reporter_id','reporter_name']].to_df()
    df = df2.merge(df1, on = 'reporter_id')
    df3 = db[['run_name','sample_name']].to_df()
    df = df.merge(df3, on = 'run_name')

    df['info'] = df.apply(lambda x:f"{x['sample_name']}_{x['run_type']}_{x['replicate_name'].split('-')[-1]}" , axis=1 )

    df = df[df['sample_name'].isin(sample_data_groups)]

    ndf = df.pivot(index='reporter_name', columns='info',values=['raw_count',])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)
    ndf.to_csv(f'{unfiltered_path}raw_counts.csv',index=False)

    print(f'Raw counts generated in {unfiltered_path}')

    ndf = df.pivot(index='reporter_name', columns='info',values=['normalized_count'])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)

    ndf.to_csv(f'{unfiltered_path}normalized_counts.csv',index=False)
    print(f'Norm counts generated in {unfiltered_path}')

    
    tdf = db[['data_id','data_group_id','reporter_id','processed_data_value']].to_df()
    tdf = tdf.merge(db[['reporter_id','reporter_name']].to_df(),on='reporter_id')
    tdf = tdf.merge(db[['data_id','sample_name']].to_df(),on='data_id')
    tdf = tdf.merge(db[['replicate_id','replicate_name','data_id']].to_df(),on='data_id')
    tdf = tdf.merge(db[['data_group_id','data_group_type']].to_df(),on='data_group_id')

    print(f"translation table fetched in unfiltered")
    tdf = tdf[tdf['sample_name'].isin(sample_data_groups)]
    tdf['info'] = tdf.apply(lambda x:f"{x['sample_name']}_{x['replicate_name'].split('-')[-1]}" , axis=1 ) #{'_'.join(x['data_group_type'].split('_')[1:])}_
    mean_trans = tdf.groupby(by=['reporter_name','data_group_type','sample_name',],as_index=False).processed_data_value.mean()
    mean_trans = mean_trans.pivot(index=['reporter_name','data_group_type'], columns='sample_name',values='processed_data_value')
    mean_trans.columns = [f'mean_replicates_{col}' for col in mean_trans.columns]
    mean_trans.reset_index(inplace=True)
    ntdf = tdf.pivot(index=['reporter_name','data_group_type'], columns='info',values='processed_data_value')
    ntdf.reset_index(inplace=True)
    ntdf = ntdf.merge(mean_trans,on = ['reporter_name','data_group_type'])
    ntdf['data_group_type'] = ntdf['data_group_type'].apply(lambda x: '_'.join(x.split('_')[1:]))
    ntdf.to_csv(f'{unfiltered_path}translation.csv',index=False)
    print(f'Translation generated in {unfiltered_path}')

    return


def filtered_tables(db,sample_data_groups,selector,selector_out_path):
    filtered_path = f"{selector_out_path}filtered/"
    if not os.path.exists(filtered_path):
        os.makedirs(filtered_path)

    selector_id = db['reporter_group_id'].where(db['reporter_group_name'] == selector).fetchone()
    selector_reporters = db['reporter_name'].where(db['reporter_group_id']==selector_id).to_list()
    df1 = db[['reporter_id','run_type','run_name','replicate_name','raw_count','normalized_count']].to_df()
    df2 = db[['reporter_id','reporter_name']].to_df()
    df = df2.merge(df1, on = 'reporter_id')
    df3 = db[['run_name','sample_name']].to_df()
    df = df.merge(df3, on = 'run_name')

    df['info'] = df.apply(lambda x:f"{x['sample_name']}_{x['run_type']}_{x['replicate_name'].split('-')[-1]}" , axis=1 )

    df = df[(df['sample_name'].isin(sample_data_groups)) & (df['reporter_name'].isin(selector_reporters))]

    ndf = df.pivot(index='reporter_name', columns='info',values=['raw_count',])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)
    ndf.to_csv(f'{filtered_path}raw_counts.csv',index=False)


    ndf = df.pivot(index='reporter_name', columns='info',values=['normalized_count'])

    ndf.columns = [f"{col[1]}_{col[0]}" for col in ndf.columns]
    ndf.reset_index(inplace=True)
    ndf.fillna(0,inplace=True)

    ndf.to_csv(f'{filtered_path}normalized_counts.csv',index=False)
    print(f'Norm counts generated in {filtered_path}')



    tdf = db[['data_id','data_group_id','reporter_id','processed_data_value']].to_df()
    tdf = tdf.merge(db[['reporter_id','reporter_name']].to_df(),on='reporter_id')
    tdf = tdf.merge(db[['data_id','sample_name']].to_df(),on='data_id')
    tdf = tdf.merge(db[['replicate_id','replicate_name','data_id']].to_df(),on='data_id')
    tdf = tdf.merge(db[['data_group_id','data_group_type']].to_df(),on='data_group_id')

    print(f"translation table fetched in unfiltered")
    tdf = tdf[(tdf['sample_name'].isin(sample_data_groups)) & (tdf['reporter_name'].isin(selector_reporters))]
    tdf['info'] = tdf.apply(lambda x:f"{x['sample_name']}_{x['replicate_name'].split('-')[-1]}" , axis=1 ) #{'_'.join(x['data_group_type'].split('_')[1:])}_
    mean_trans = tdf.groupby(by=['reporter_name','data_group_type','sample_name',],as_index=False).processed_data_value.mean()
    mean_trans = mean_trans.pivot(index=['reporter_name','data_group_type'], columns='sample_name',values='processed_data_value')
    mean_trans.columns = [f'mean_replicates_{col}' for col in mean_trans.columns]
    mean_trans.reset_index(inplace=True)
    ntdf = tdf.pivot(index=['reporter_name','data_group_type'], columns='info',values='processed_data_value')
    ntdf.reset_index(inplace=True)
    ntdf = ntdf.merge(mean_trans,on = ['reporter_name','data_group_type'])
    ntdf['data_group_type'] = ntdf['data_group_type'].apply(lambda x: '_'.join(x.split('_')[1:]))
    ntdf.to_csv(f'{filtered_path}translation.csv',index=False)
    print(f'Translation generated in {filtered_path}')
    return



def selector_specific_tables(db,selector,selector_out_path):

    reporter_group_id = db[['reporter_group_id']].where(db['reporter_group_name'] == selector).fetchone()

    data_groups = set(db[['data_group_id']].where(db['reporter_group_id'] == reporter_group_id).to_list())
    sample_data_groups = set(db['sample_name'].where(db['data_group_id'].in_(data_groups)).to_list())

    reporter_group_id = db[['reporter_group_id']].where(db['reporter_group_name'] == selector).fetchone()

    data_groups = set(db[['data_group_id']].where(db['reporter_group_id'] == reporter_group_id).to_list())
    sample_data_groups = set(db['sample_name'].where(db['data_group_id'].in_(data_groups)).to_list())

    unfiltered_tables(db,sample_data_groups,selector_out_path)
    filtered_tables(db,sample_data_groups=sample_data_groups,selector=selector,selector_out_path=selector_out_path)
    return


def selector_wise_tables(db,out_path):

    selector_df = db[['reporter_group_name','reporter_group_type']].to_df()
    selector_df = selector_df[selector_df['reporter_group_type']=='selector']
    selector_list = selector_df['reporter_group_name'].tolist()

    for selector in selector_list:
        selector_out_path = f"{out_path}{selector}_tables/"
        if not os.path.exists(selector_out_path):
            os.makedirs(selector_out_path)

        selector_specific_tables(db,selector=selector,selector_out_path=selector_out_path)
    return


def generate_tables(db,fasta_path):

    out_path = f'{db.output_path}/tables/'

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    insert_sequence_tables(db,out_path)
    all_raw_counts_csv(db=db,fasta_path=fasta_path,out_path=out_path)
    selector_wise_tables(db,out_path=out_path)


    return