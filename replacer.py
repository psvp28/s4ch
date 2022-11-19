import pandas as pd
import numpy as np
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from tqdm import tqdm
import time
pd.options.mode.chained_assignment = None
tqdm.pandas()

reference_output_directory = # from tagset.py
output_directory_path    =  # directory here to output from tagset.py
concat_output = # here

data_list = glob.glob(output_directory_path + "/*.csv")
data_list = sorted(data_list)

concat_list = []
for i in data_list:
    concat_list.append(pd.read_csv(i,
                                   error_bad_lines=False,
                                   low_memory=False,
                                   lineterminator='\n'))

concat = pd.concat(concat_list).reset_index().drop(['Unnamed: 0', 'index'], axis=1)
concat['Time'] = pd.to_datetime(concat.Time)

concat.to_csv(concat_output)


reference_df = pd.read_csv(reference_output_directory+'/ref.csv',
                           error_bad_lines=False,
                           low_memory=False,
                           lineterminator='\n')

def repl(df, dict_name, dict_hash):
    df['Time'] = pd.to_datetime(df.Time)
    df_user_interactions = df.replace(dict_name)
    df_hash_interactions = df.replace(dict_hash)
    
    return df_user_interactions, df_hash_interactions

def gephiextract(workers=16):
    
    futures = []
    resultsi = []
    resultsh = []
    print('Im in')
    executor = ProcessPoolExecutor(max_workers=workers)
    
    iterator = pd.read_csv(concat_output,
                           error_bad_lines=False, 
                           low_memory=False, 
                           lineterminator='\n', 
                           chunksize=100000)
    ite = None

    try:
        ite = next(iterator)
    except StopIteration:
        ite = None

    time.sleep(1)
    
    with tqdm(total = 270*workers, desc='Submission approximately') as pbar:
        while ite is not None:
            sces = np.array_split(ite, workers)
            for sc in sces:
                idset = set(sc.Source).union(set(sc.Target))
                refdf = reference_df[reference_df['id'].isin(idset)]
                namedict = refdf.set_index('id').to_dict()['user_screen_name']
                hashdict = refdf.set_index('id').to_dict()['hashtags']
                futures.append(executor.submit(repl, sc, namedict, hashdict))
                pbar.update(1)
            
            try:
                ite = next(iterator)
            except StopIteration:
                ite = None
        
    
    with tqdm(total = len(futures), desc='Progress') as pbar2:
          for i in as_completed(futures):
                pbar2.update(1)
       
    for f in futures:
        try:
            useri, hashi = f.result()
            resultsi.append(useri)
            resultsh.append(hashi)
        except Exception as e:
            print(e)
            continue
        
    df_users = pd.concat(resultsi, ignore_index=True)
    df_users = df_users.groupby(by=['Source','Target']).agg({'Weight':'sum','Time':pd.Series.median}).reset_index()
    df_users['Type'] = 'Undirected'
    df_hash = pd.concat(resultsh, ignore_index=True)
    df_hash = df_hash.groupby(by=['Source','Target']).agg({'Weight':'sum','Time':pd.Series.median}).reset_index()
    df_hash['Type'] = 'Undirected'
    
    
    df_users.to_csv(output_directory_path+'/users.csv')
    df_hash.to_csv(output_directory_path+'/hash.csv')
    
    
    return resultsi, resultsh


if __name__ ==  '__main__':    
    gephiextract()
    print('DONE!')