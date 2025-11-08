import os
import json
import openai
import time
from dotenv import load_dotenv
import argparse
import pandas as pd


def query(context, prompt, tweets, n, outname, deployment_name, iterative=False, followup=None):
    if os.path.isfile(outname):
        og_df = pd.read_csv(outname)
    else:
        og_df = pd.DataFrame({"tweet": [], "gpt label": []})

    tweetlist = []
    labellist = []

    for t in tweets:
        prompt += "<tweet>%s</tweet>\n" % t

    for _ in range(n):
        retry = True
        n_retries = 0
        while retry:
            try:
                response = openai.ChatCompletion.create(
                            engine = deployment_name,
                            temperature = 0,
                            messages=[
                                        {"role": "system", "content": context},
                                        {"role": "user", "content": prompt} 
                                     ]
                                )
                message = response['choices'][0]['message']['content']
                if iterative:
                    prompt2 = "Based on your reasoning above, answer the question in one word by saying \"yes\",\"no\", or \"unsure\" once for each tweet, where \"yes\" means that the tweet refers to opioids. Separate your answers by commas. Only give this in your response; do not add other content." 
                    print(message)
                    time.sleep(2)
                    response = openai.ChatCompletion.create(
                                engine = deployment_name,
                                temperature = 0,
                                messages=[
                                            {"role": "system", "content": context},
                                            {"role": "user", "content": prompt},
                                            {"role": "assistant", "content": message},
                                            {"role": "user", "content": prompt2}
                                         ]
                                    )
                    message = response['choices'][0]['message']['content']
                elif followup:
                    time.sleep(2)
                    response = openai.ChatCompletion.create(
                                engine = deployment_name,
                                temperature = 0,
                                messages=[
                                            {"role": "system", "content": context},
                                            {"role": "user", "content": prompt},
                                            {"role": "assistant", "content": message},
                                            {"role": "user", "content": followup}
                                         ]
                                    )
                    message = response['choices'][0]['message']['content']
            except openai.error.InvalidRequestError, :
                labels = ["ContentRestrictionError"] * len(tweets)
                retry = False
            except (openai.error.RateLimitError, KeyError, openai.error.Timeout, openai.error.APIConnectionError, openai.error.APIError):
                if n_retries >= 10:
                    labels = ["APIError"] * len(tweets)
                    retry = False
                else:
                    time.sleep(3)
                    print("retrying...")
                    retry = True
                    n_retries += 1
            else:
                labels = message.split(",")
                retry = False
        if len(labels) != len(tweets):
            print("ERROR: mismatch in labels and tweets. aborting")
            print(len(tweets))
            print(message)
            return
        for i in range(len(tweets)):
            tweetlist.append(tweets[i])
            labellist.append(labels[i])
        time.sleep(2)
    df = pd.DataFrame({"tweet": tweetlist, "gpt label": labellist})
    updated_df = pd.concat([og_df, df], ignore_index=True)
    updated_df.to_csv(outname, sep=",", index=False)



def main(args):
    '''
    if os.path.isfile(args.outname):
        print("WARNING: outfile already exists. aborting.")
        return
    '''
    load_dotenv()

    openai.api_key = os.getenv("AZURE_OPENAI_KEY")
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_type = 'azure' # from quickstart documentation
    openai.api_version = '2023-05-15' # from quickstart documentation

    deployment_name = os.getenv("DEPLOYMENT_NAME")

    if args.term == "fenty":
        drug_name = "fentanyl"
        alternate = "Fenty Beauty the makeup brand"
    elif args.term == "lean":
        drug_name = "codeine"
        alternate = "the action of leaning on something"
    elif args.term == "smack":
        drug_name = "heroin"
        alternate = "the action of smacking something"
    elif not args.term is None:
        print("not yet able to handle this term... aborting.")
        return
    
    if args.context is None:
        context = "You are an AI assistant that helps people find information. You are particularly hip with online slang and know everything about how people talk on social media platforms like Facebook, Twitter, Reddit, and TikTok."
    else:
        context = args.context

    if not args.prompt is None:
        prompt = "%s\n" % args.prompt
    elif args.term is None:
        prompt = "I am going to give you a series of tweets, delimited with the xml tags <tweet></tweet>. For each tweet, I want you to tell me if the the tweet is talking about opioids. Give your answer by saying \"yes\" or \"no\" once for each tweet, where \"yes\" means that the tweet refers to opioids. Separate your answers by commas. Only give this in your response; do not add other content.\n"
    else:
        prompt = "I am going to give you a series of tweets, delimited with the xml tags <tweet></tweet>. For each tweet, I want you to tell me if the word \"%s\" is being used to mean %s, or not (e.g. if it is being used to talk about %s). Give your answer by saying \"yes\" or \"no\" once for each tweet, where \"yes\" means that \"%s\" is referring to %s. Separate your answers by commas. Only give this in your response; do not add other content.\n" % (args.term, drug_name, alternate, args.term, drug_name)


    # prev_tweets = pd.read_csv(args.outname)["tweet"].unique().tolist()
    tweets = []

    if not args.json is None:
        inputf = open(args.json,"r")
        lines = inputf.read().split("\n")
    elif not args.txt is None:
        inputf = open(args.txt, "r")
        lines = inputf.read().split("\n")
    elif not args.csv is None:
        inputdf = pd.read_csv(args.csv,header=None)
        lines = inputdf[0].tolist()
    else:
        print("Error. no input provided. exiting...")
        return

    if args.individual:
        tweets_per_query = 1
    elif args.iterative:
        tweets_per_query = 3
    else:
        tweets_per_query = 5

    for line in lines:
        if len(line) == 0:
            continue
        if not args.json is None:
            j = json.loads(line)
            curr_tweet = j["text"]
        else:
            curr_tweet = line
        # if curr_tweet in prev_tweets:
        #     continue
        tweets.append(curr_tweet)
        if len(tweets) == tweets_per_query:
           query(context, prompt, tweets, args.n, args.outname, deployment_name, args.iterative, args.followup)
           tweets = []
    if len(tweets) > 0:
        query(context, prompt, tweets, args.n, args.outname, deployment_name, args.iterative, args.followup)
    if args.csv is None:
        inputf.close()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, default=3, help="number of query repetitions")
    parser.add_argument("--json", type=str, help="input json file")
    parser.add_argument("--txt", type=str, help="input txt file; will only be used if no json provided")
    parser.add_argument("--csv", type=str, help="input csv file, in pandas-readable format; will only be used if no json or txt provided")
    parser.add_argument("--outname", type=str, default="output.txt",help="name of output file")
    parser.add_argument("--context", type=str, help="system context to use")
    parser.add_argument("--prompt", type=str, help="prompt to use -- will override term argument")
    parser.add_argument("--term", type=str, help="ambiguous term to query for; if this option is not used, will look for drug relevance without particular keyword")
    parser.add_argument("--iterative", action="store_true", help="flag to do iterative prompting")
    parser.add_argument("--followup", type=str, help="followup prompt to ask after first prompt and keep answers from")
    parser.add_argument("--individual", action="store_true", help="flag to only query one tweet at a time")
    args = parser.parse_args()
    main(args)
