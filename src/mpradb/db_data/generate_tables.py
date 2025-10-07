import numpy as np
import pandas as pd
import os



def all_raw_counts_csv(db,out_path):
    all_counts_out_path = f"{out_path}all_raw_counts/"
    if not os.path.exists(all_counts_out_path):
        os.makedirs(all_counts_out_path)


    df1 = db[['reporter_id','run_type','sample_name','replicate_name','raw_count','normalized_count']].to_df()
    df2 = db[['reporter_id','reporter_name','insert_sequence']].to_df()
    df = df2.merge(df1, on = 'reporter_id')
    df.to_csv(f'{all_counts_out_path}all_raw_counts.csv',index=False)
    
    return


def unfiltered_tables(db,sample_data_groups,selector_out_path):
    unfiltered_path = f"{selector_out_path}unfiltered/"
    if not os.path.exists(unfiltered_path):
        os.makedirs(unfiltered_path)

    all_raw_df1 = db[['reporter_id','run_type','sample_name','replicate_name','raw_count','normalized_count']].where(db['sample_name'].in_(sample_data_groups)).to_df()

    all_raw_df2 = db[['reporter_id','reporter_name','insert_sequence']].to_df()

    all_raw_df = all_raw_df2.merge(all_raw_df1, on = 'reporter_id')

    all_raw_df.to_csv(f'{unfiltered_path}raw_counts.csv',index=False)

    translation_df1 = db[['reporter_id','sample_name','replicate_name','data_value']].where(db['sample_name'].in_(sample_data_groups)).to_df()

    raw_translation_df = translation_df1.merge(all_raw_df2,on='reporter_id').drop_duplicates()
    raw_translation_df.to_csv(f'{unfiltered_path}raw_translation.csv',index=False)
    
    mean_trans1 = db[['reporter_id','data_id','sample_name','processed_data_value']].where(db['sample_name'].in_(sample_data_groups)).to_df().drop_duplicates()
    mean_translation_df = mean_trans1.merge(all_raw_df1, on = 'reporter_id')
    mean_translation_df.to_csv(f'{unfiltered_path}mean_translation.csv',index=False)
    return


def filtered_tables(db,sample_data_groups,selector,selector_out_path):
    filtered_path = f"{selector_out_path}filtered/"
    if not os.path.exists(filtered_path):
        os.makedirs(filtered_path)

    selector_id = db['reporter_group_id'].where(db['reporter_group_name'] == selector).fetchone()
    all_raw_df1 = db[['reporter_id','run_type','sample_name','replicate_name','raw_count','normalized_count']].where((db['sample_name'].in_(sample_data_groups))&(db['reporter_group_id']==selector_id)).to_df()

    all_raw_df2 = db[['reporter_id','reporter_name','insert_sequence']].where(db['reporter_group_id']==selector_id).to_df()

    all_raw_df = all_raw_df2.merge(all_raw_df1, on = 'reporter_id')

    all_raw_df.to_csv(f'{filtered_path}raw_counts.csv',index=False)

    translation_df1 = db[['reporter_id','sample_name','replicate_name','data_value']].where((db['sample_name'].in_(sample_data_groups))&(db['reporter_group_id']==selector_id)).to_df()

    raw_translation_df = translation_df1.merge(all_raw_df2,on='reporter_id').drop_duplicates()
    raw_translation_df.to_csv(f'{filtered_path}raw_translation.csv',index=False)
    
    mean_trans1 = db[['reporter_id','data_id','sample_name','processed_data_value']].where((db['sample_name'].in_(sample_data_groups))&(db['reporter_group_id']==selector_id)).to_df().drop_duplicates()
    mean_translation_df = mean_trans1.merge(all_raw_df1, on = 'reporter_id')
    mean_translation_df.to_csv(f'{filtered_path}mean_translation.csv',index=False)
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


def generate_tables(db):

    out_path = f'{db.output_path}/tables/'

    if not os.path.exists(out_path):
        os.makedirs(out_path)


    all_raw_counts_csv(db,out_path)
    selector_wise_tables(db,out_path=out_path)


    return