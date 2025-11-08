import requests
import json, math, sys, time
import openai
import re
from openai import AzureOpenAI
from dotenv import load_dotenv
import os, time, glob
from tqdm import tqdm
from statistics import mode
from sklearn.metrics import confusion_matrix
import pandas as pd
from tqdm import tqdm

load_dotenv()

def query_o1(prompt):
    client = AzureOpenAI(
      azure_endpoint = os.getenv("o1_endpoint"), 
      api_key=os.getenv("o1_key"),  
      api_version="2024-02-01"
    )
    
    response = client.chat.completions.create(
        model=os.getenv("o1_mini"), # model = "deployment_name".
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

def load_query_template(path="./query_template2.txt"):
    with open(path, "r") as f:
        query_template = f.read()
    return query_template

def write_to_file(filepath, content):
    with open(filepath, "a") as f:
        f.write(content)

def tag_comments(comment_list):
    tagged_comments = [f"<comment>{i}<\comment>\n" for i in comment_list]
    tagged_comments_str = "".join(tagged_comments)
    return tagged_comments_str

def extract_ann_exp(response):
    pattern = r"<ann>(.*?)</ann> <exp>(.*?)</exp>"
    
    response_list = response.split("\n")
    # AttributeError if one of them does not follow the patter or No match was found
    ann_batch = [re.search(pattern, i).group(1) for i in response_list]
    exp_batch = [re.search(pattern, i).group(2) for i in response_list]
    return ann_batch, exp_batch

def get_response(prompt, query_func, num_comments):
    retry = True; 
    max_retries_api_error = 10; num_retries_api_error = 0
    max_retries_bad_request = 5; num_retries_bad_request = 0

    while retry:
        try:
            response = query_func(prompt)
            retry = False
            
        except openai.BadRequestError as e:
            print(e); print(f"{num_retries_bad_request}/{max_retries_bad_request} tries more ...")
            if num_retries_bad_request < max_retries_bad_request: 
                time.sleep(1.3**num_retries_bad_request); num_retries_bad_request+=1
            else:
                response = "<ann>BadRequestError</ann> <exp>BadRequestError</exp>\n" * num_comments
                retry = False
            
        except (openai.RateLimitError, KeyError, openai.Timeout, openai.APIConnectionError, openai.APIError) as e:
            print(e); print(f"{num_retries_api_error}/{max_retries_api_error} tries more ...")
            if num_retries_api_error < max_retries_api_error: 
                time.sleep(1.3**num_retries_api_error); num_retries_api_error+=1
            else:
                response = "<ann>APIError</ann> <exp>APIError</exp>\n" * num_comments
                retry = False

    return response

def annotate_comments(ids_all, comments_all, filepath, 
                      batch_size=5, query_func=query_o1, return_results=False):
    
    query_template = load_query_template()
    write_to_file(filepath, "id\tannotation\texplanation\ttime\n")
    all_csv_content = ""
    for start in tqdm(range(0, len(comments_all), batch_size)):
        retry = True; max_retries = 10; num_retries = 0
        
        ids_batch = ids_all[start: start+batch_size]
        comments_batch = comments_all[start: start+batch_size]
        tagged_comments = tag_comments(comments_batch)

        assert len(ids_batch) == len(comments_batch), f"{len(ids_batch)} ids, {len(comments_batch)} comments"

        num_comments = len(comments_batch)
        prompt = query_template + tagged_comments
        response = get_response(prompt, query_func, num_comments)
        try:
            ann_batch, exp_batch = extract_ann_exp(response)
        except AttributeError:
            ann_batch, exp_batch = ['None']*num_comments, ['None']*num_comments

        assert num_comments == len(ids_batch), f"{len(ids_batch)} ids, {num_comments} comments"
        
        time_list = [time.time()]*num_comments
        
        try:
            csv_content = [f"{ids_batch[i]}\t'{ann_batch[i]}'\t{exp_batch[i]}\t{time_list[i]}\n" for i in range(num_comments)]
            csv_content = "".join(csv_content)
            all_csv_content += csv_content
            write_to_file(filepath, csv_content)
        except IndexError as e:
            print(e)
            print(f"expected {num_comments}")
            print(f"but got {len(ids_batch)} ids_batch, {len(ann_batch)} ann_batch, {len(exp_batch)} exp_batch, {len(time_list)} time_list")
        
    if return_results: return all_csv_content

def get_annotated_id(persons_folder):
    saved_gpt_ann = glob.glob(f"{persons_folder}/*.txt")
    annotated_ids = []
    for gpt_ann in saved_gpt_ann:
        ann_df = pd.read_csv(gpt_ann, delimiter="\t")
        annotated_ids += list(ann_df['id'])
    return set(annotated_ids)

def get_selection(df, persons_folder):
    annotated_ids = list(set(get_annotated_id(persons_folder)))
    selection = list(~df["id"].isin(annotated_ids))
    return selection

def main(comments_csv_path, output_folder):
    
    df = pd.read_csv(comments_csv_path)
    # df = df.sample(n=250000, random_state=43)

    print("filtering annotated ids out ...")
    selection = get_selection(df, output_folder)
    df = df[selection].reset_index(drop=True)
    
    print(f"Annotating {len(df)} out of {len(selection)} comments")

    ids_all = list(df['id'])
    comments_all = list(df['text'])
    start_time = time.time()
    
    annotate_comments(ids_all, comments_all, 
                  f"{output_folder}/gpt_annotations_{start_time}.txt", 
                  batch_size=5, query_func=query_o1)


if __name__ == "__main__":
    comments_csv_path = sys.argv[1]
    output_folder = sys.argv[2]

    main(comments_csv_path, output_folder)

