import pandas as pd
import numpy as np
from collections import Counter
import math
import ast
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from tqdm import tqdm
import time
pd.options.mode.chained_assignment = None  # SetCopyWarning disabled


tweets_file_path    =   # here
hashtags_list_path   =   # here
reference_output_directory = # input to replacer.py
output_directory_path    = # here
number_of_workers   =   16 # or here according to your processor cores. Recommended 2*(cores-1)

input = pd.read_csv(tweets_file_path,
                  error_bad_lines=False,
                  low_memory=False,
                  lineterminator='\n').drop('Unnamed: 0', axis=1)

def split_df_ori(df: pd.DataFrame):
    original = df[df["in_reply_to_screen_name"].isna() & df["rt_created_at"].isna() & df["quoted_status_id"].isna()]
    reply = df[df["in_reply_to_user_id"].notna() & df["quoted_status_id"].isna()]
    quote = df[df["quoted_status_id"].notna() & df["rt_created_at"].isna()]
    return pd.concat([original,quote,reply])

ori = split_df_ori(tweets_file_path)

reference_df = ori[['id','user_screen_name','hashtags']]
reference_df['hashtags'] = reference_df.hashtags.apply(lambda x: tuple(literal_eval(x)))
reference_df.to_csv(reference_output_directory+'/ref.csv')


with open(hashtags_list_path) as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

set_hashtags = sorted(set(lines))

def intercheck(tagset, hashtag):
    if hashtag in tagset:
        return True
    else:
        return False

def liteval(x):
    try:
        return ast.literal_eval(str(x))   
    except Exception as e:
        print(e)
        return []
    
def counter_cosine_similarity(c1, c2):
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)

def length_similarity(c1, c2):
    lenc1 = sum(c1.values())
    lenc2 = sum(c2.values())
    return min(lenc1, lenc2) / float(max(lenc1, lenc2))

def similarity_score(s1, s2):
    l1, l2 = list(s1) , list(s2)
    c1, c2 = Counter(l1), Counter(l2)
    
    return length_similarity(c1, c2) * counter_cosine_similarity(c1, c2)    


def process(df_extracto, index1, tags1):
    comparelist = []
    listo = []
    for index2 in range(index1,len(df_extracto)):
        tags2 = df_extracto.tagset[index2]
        comparelist.append(1 - similarity_score(tags1,tags2))

    most_sim = np.nanmin(comparelist)
    jmins = np.where(comparelist == most_sim)
    for jmin in jmins:
        for j in jmin:
            d = {'Source': df_extracto.loc[j,'id'], 
                 'Target': df_extracto.loc[index1,'id'], 
                 'Type': 'Directed', 
                 'Weight': 1 - most_sim, 
                 'Time':df_extracto.loc[index1,'created_at']}

            listo.append(d)
    
    return listo



def gephiextract(hstg, workers = number_of_workers):
    ori['tagset'] = ori.hashtags.apply(lambda x: liteval(x))
    condition = ori.tagset.apply(lambda x: intercheck(x, hstg) & (len(x) > 1))
    df_extract = ori[condition]
    df_extract = df_extract.drop_duplicates(subset='id_str')
    df_extract['created_at'] = pd.to_datetime(df_extract['created_at'])
    df_extract = df_extract.sort_values(by='created_at')
    df_extract = df_extract.reset_index()
    
    
    hashtag = hstg
    futures = []
    results = []
    print('Im in')
    executor = ProcessPoolExecutor(max_workers=workers)
    
    indexiter = enumerate(df_extract.tagset)
    indextag = None

    try:
        indextag = next(indexiter)
    except StopIteration:
        indextag = None

    time.sleep(1)
    
    with tqdm(total = len(df_extract), desc='Submission of ' + hstg) as pbar:
        while indextag is not None:
            index1, tags1 = indextag
            futures.append(executor.submit(process, df_extract, index1, tags1))
            pbar.update(1)
            try:
                indextag = next(indexiter)
            except StopIteration:
                indextag = None
        
    
    with tqdm(total = len(futures), desc='Progress of ' + hstg) as pbar2:
          for i in as_completed(futures):
                pbar2.update(2)
       
    for f in futures:
        try:
            results.extend(f.result())
        except Exception as e:
            print(e)
            continue
        
    df_network = pd.DataFrame(data=results, columns = ['Source','Target','Type','Weight','Time'])
    
    if len(df_network) > 0:
        df_network.to_csv(output_directory_path+str(hashtag)+'.csv')
        print('written #', hashtag)
    else:
        print('Something went wrong')
    
    return results


if __name__ ==  '__main__':
    pbarh = tqdm(total = len(set_hashtags), desc='Total')
    
    for hasht in set_hashtags:
        print('###############################################')
        time.sleep(0.5)
        print(hasht)
        time.sleep(0.5)
        gephiextract(hasht)
        print('')
        print('')
        print('')
        print('')
        print('###############################################')
        print('')
        print('')
        print('')
        print('')
        pbarh.update(1)
        
        
    pbarh.close()
    
    print('DONE!')
