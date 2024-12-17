import requests
import os
import pandas as pd
import time
import csv
import sys
import re
import datetime
from textblob import TextBlob

input_file = r"/Process_Summer_Code/Raw Pull Data"
pull_file = r"/Process_Summer_Code/pull.csv"
project_file = r"/Process_Summer_Code/project.csv"
user_file=r"/Process_Summer_Code/user.csv"
f_pull_file = r"/Process_Summer_Code/pull_false.csv"
f_project_file = r"/Process_Summer_Code/project_false.csv"
f_user_file=r"/Process_Summer_Code/user_false.csv"
error_file=r"/Process_Summer_Code/error.csv"

t_pull_file = r"/Process_Summer_Code/pull_true.csv"
t_project_file = r"/Process_Summer_Code/project_true.csv"
t_user_file=r"/Process_Summer_Code/user_true.csv"
max_int = 2**31- 1
csv.field_size_limit(max_int)

pull_handle = open(pull_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
pull_writer = csv.writer(pull_handle)

project_handle = open(project_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
project_writer = csv.writer(project_handle)

user_handle = open(user_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
user_writer = csv.writer(user_handle)

error_handle = open(error_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
error_writer = csv.writer(error_handle)


f_pull_handle = open(f_pull_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
f_pull_writer = csv.writer(f_pull_handle)

f_project_handle = open(f_project_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
f_project_writer = csv.writer(f_project_handle)

f_user_handle = open(f_user_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
f_user_writer = csv.writer(f_user_handle)

t_pull_handle = open(t_pull_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
t_pull_writer = csv.writer(t_pull_handle)

t_project_handle = open(t_project_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
t_project_writer = csv.writer(t_project_handle)

t_user_handle = open(t_user_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
t_user_writer = csv.writer(t_user_handle)

pull_writer.writerow(["pr_id","pr_title", "pr_body", "is_merged", "pr_number", "pr_url", "pr_html_url", "pr_state", "additions", "deletions",
                      	"pr_changed_files", "pr_commits_count", "pr_comments_count", "pr_review_comments_count", "pr_labels_count", "pr_assignees_count",
                        "pr_labels", "pr_created_at", "pr_closed_at", "time_taken", "time_delta", "pr_review_comments", "pr_commits", "contributor", "contributor_id",
                        "contributor_email","contributor_type", "contributions", "contributor_public_repos", "contributor_private_repos", "contributor_followings", 
                        "contributor_followers","comments", "positive", "negative", "neutral"])
project_writer.writerow(["Project_ID","Name", "Full_name", "Language", "Forks", "Stars", "Watchers", "contributors", "commits", "issues", "branches", "PRs_count", 
                         "contributor", "pullrequests"																			
])
user_writer.writerow(["id","Pulls","Accepted pulls","Rejected Pulls", "Projects","Num Ext Pulls", "External Pulls","Comments",
                       "Positive", "Negative", "Neutral","Public Repositories","Following","Followers"])
f_pull_writer.writerow(["pr_id","pr_title", "pr_body", "is_merged", "pr_number", "pr_url", "pr_html_url", "pr_state", "additions", "deletions",
                      	"pr_changed_files", "pr_commits_count", "pr_comments_count", "pr_review_comments_count", "pr_labels_count", "pr_assignees_count",
                        "pr_labels", "pr_created_at", "pr_closed_at", "time_taken", "time_delta", "pr_review_comments", "pr_commits", "contributor", "contributor_id",
                        "contributor_email","contributor_type", "contributions", "contributor_public_repos", "contributor_private_repos", "contributor_followings", 
                        "contributor_followers","comments", "positive", "negative", "neutral"])
f_project_writer.writerow(["Project_ID","Name", "Full_name", "Language", "Forks", "Stars", "Watchers", "contributors", "commits", "issues", "branches", "PRs_count", 
                         "contributor", "pullrequests"																			
])
f_user_writer.writerow(["id","Pulls","Accepted pulls","Rejected Pulls","Projects","Num Ext Pulls", "External Pulls",
                        "Comments", "Positive", "Negative", "Neutral","Public Repositories","Following","Followers"])

t_pull_writer.writerow(["pr_id","pr_title", "pr_body", "is_merged", "pr_number", "pr_url", "pr_html_url", "pr_state", "additions", "deletions",
                      	"pr_changed_files", "pr_commits_count", "pr_comments_count", "pr_review_comments_count", "pr_labels_count", "pr_assignees_count",
                        "pr_labels", "pr_created_at", "pr_closed_at", "time_taken", "time_delta", "pr_review_comments", "pr_commits", "contributor", "contributor_id",
                        "contributor_email","contributor_type", "contributions", "contributor_public_repos", "contributor_private_repos", "contributor_followings", 
                        "contributor_followers","comments", "positive", "negative", "neutral"])
t_project_writer.writerow(["Project_ID","Name", "Full_name", "Language", "Forks", "Stars", "Watchers", "contributors", "commits", "issues", "branches", "PRs_count", 
                         "contributor", "pullrequests"																			
])
t_user_writer.writerow(["id","Pulls","Accepted pulls","Rejected Pulls","Projects","Num Ext Pulls", "External Pulls",
                        "Comments", "Positive", "Negative", "Neutral","Public Repositories","Following","Followers"])


#error_handle = open(error_file, 'w', encoding='UTF-8', newline='',errors='ignore')
#writer_error = csv.writer(error_handle)
def extract_project_name(url):
     if "pull" not in url:
          return "",0
     name=url.split("/")
     num=name[-1]
     if "#" in num:
          l_num= num.strip().split("#")
          num=l_num[0]
          
     if len(name) >3 and num.isdigit():
        project= name[-4]+"/"+name[-3]
        #number=num
        return project
     return ""
def preprocess_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\b\w{1,2}\b', '', text)  # Remove short words (optional)
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    #text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    return text
def get_sentiment(text):
      r_text = preprocess_text(text)
      score = TextBlob(r_text).sentiment.polarity
      if score<0:
            return 'negative'
      elif score >0:
            return 'positive'
      else:
            return 'neutral'
def process_string(inp):
      result=[]
      #out= re.findall(r"\{(.*?)\}",inp)
      out= re.findall(r"comment_body':(.*?)comment_created",inp)
      positive=0
      negative=0
      neutral=0

      
      for x in out:
            
            result.append(x)
            sentiment = get_sentiment(x)
            if sentiment =='positive':
                  positive +=1
            elif sentiment == 'negative':
                  negative +=1
            else:
                  neutral +=1
      #print(result)     
      #print("**************************")
      return result,positive,negative,neutral
def process_id(inp):
      result=[]
      #print(inp)
      #out= re.findall(r"\{(.*?)\}",inp)
      out= re.findall(r"id':(.*?),",inp)
      #print(out)
      
      for x in out:
            
            result.append(x)
      #print(result)     
      #print("**************************")
      return result
def extract_id(inp):
      result=[]
      #print(inp)
      #out= re.findall(r"\{(.*?)\}",inp)
      out= re.findall(r"id':(.*?),",inp)
      #print(out)
      
      for x in out:
            
            result.append(x)
      #print(result)     
      #print("**************************")
      return result


def process_file(file_in):
    #print(file_in)
    input_handle = open(file_in, mode='r',encoding='UTF-8',newline='',errors='ignore')
    first_line =True
    empty_line = False
    project_info =False
    num_pulls =0
    num_project =0
    num_ext_pulls=0
    num_accept_pull=0
    num_reject_pull=0
    positive=0
    negative=0
    neutral=0
    ext_pulls=[]
    pull_ids=set()
    project_name=set()
    comments = []
    isFalse=False
    c_id=""
    public_repo=""
    following=""
    follower=""
    
    try: 
        csv_dict = [row for row in csv.reader(input_handle)]
        if len(csv_dict)<=1:
              input_handle.close()
              print(file_in)
              return
        for line in csv_dict:
          try:
            if first_line :
                first_line = False
                continue
            if len(line)==0:
                  empty_line=True 
                  continue
            if empty_line and line[0] == 'Project_ID':
                  project_info = True
                  continue
            l_comments=[]
            if project_info:
                  project_writer.writerow(line)
                  if isFalse and num_reject_pull >= num_accept_pull:
                        f_project_writer.writerow(line)
                  else:
                        t_project_writer.writerow(line)
                  num_project += 1
                  pulls = process_id(line[12])
                  name=line[2]
                  for x in pulls:
                        n=x.strip()
                        if n not in pull_ids and name in project_name:
                              num_ext_pulls +=1
                              ext_pulls.append(n)
            else: 
                  
                  if line[3] != "True" and line[3] != "False":
                        #print("test")
                        continue
                  if c_id =="" and line[24] is not None:
                        c_id = line[25]
                  num_pulls += 1
                  p_name = extract_project_name(line[6])
                  project_name.add(p_name)
                  pull_ids.add(line[0])
                  #print(line[22])
                  val,pos,neg,neu = process_string(line[21])
                  positive += pos
                  negative += neg
                  neutral += neu
                  #val=""
                  for x in val:
                        #print(x)
                        #if x.get('comment_body') is not None:
                        comments.append(x)
                        l_comments.append(x)
                  line.append(l_comments)
                  line.append(pos)
                  line.append(neg)
                  line.append(neu)
                  pull_writer.writerow(line)
                  #print(line[3])
                  #print(type(line[3]))
                  if line[3] == "False":
                        isFalse=True
                        #print("False")
                        f_pull_writer.writerow(line)
                        num_reject_pull +=1
                  else:
                        t_pull_writer.writerow(line)
                        num_accept_pull+=1
                  length = len(line)
                  if length > 31:
                        if line[28] is not None or line[28] != "":
                              public_repo=line[28]
                        if line[30] is not None or line[30] != "":
                              following =line[30]
                        if line[31] is not None or line[31] != "":
                              follower =line[31] 
          except Exception as e:
                print(f"Line error occured: {e}")
                error_writer.writerow([line])
        user= [c_id,num_pulls,num_accept_pull,num_reject_pull,num_project,num_ext_pulls,ext_pulls,
               comments,positive,negative,neutral,public_repo,following,follower]
        
        user_writer.writerow(user)
        #print(c_id)
        #print(num_pulls)
        if isFalse and num_reject_pull >= num_accept_pull:
              f_user_writer.writerow(user)
        else: 
              t_user_writer.writerow(user)

        input_handle.close()        
      
    except Exception as e:
         print(f"Error occured: {e}")
         error_writer.writerow([file_in,e])
         #print(e.__class__)
         input_handle.close()


if __name__ == "__main__":
	input_files = []
	if os.path.isdir(input_file):
		
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file)))
	for file_in in input_files:
        
		process_file(file_in)
	
    
	user_handle.close()
      
 
	project_handle.close()
     
	pull_handle.close()
f_pull_handle.close()
f_user_handle.close()
f_project_handle.close()

t_pull_handle.close()
t_user_handle.close()
t_project_handle.close()
error_handle.close()

      