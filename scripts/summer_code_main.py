import requests
import os
import pandas as pd
import time
import csv
import logging.handlers
from github import Auth,Github, RateLimitExceededException, BadCredentialsException, BadAttributeException,GithubException, UnknownObjectException,BadUserAgentException
auth=Auth.Token("")#Github token
g = Github(auth=auth,retry=10, timeout=15, per_page=100)

input_file = r"/summer_code_final.csv"
output_file = r"/summer_code"
error_file=r"/summer_code/error.csv"

input_handle = open(input_file, mode='r',encoding='UTF-8',newline='',errors='ignore')

error_handle = open(error_file, 'w', encoding='UTF-8', newline='',errors='ignore')
writer_error = csv.writer(error_handle)

#set up logging console and file
log = logging.getLogger("gsoc_bot")
log.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
#log_str_handler = logging.StreamHandler()
#log_str_handler.setFormatter(log_formatter)
#log.addHandler(log_str_handler)
if not os.path.exists("logs"):
	os.makedirs("logs")
log_file_handler = logging.handlers.RotatingFileHandler(os.path.join("logs", "gsoc_bot.log"), maxBytes=1024*1024*16, backupCount=5)
log_file_handler.setFormatter(log_formatter)
log.addHandler(log_file_handler)


def extract_project_PR(project_full_name,number):
    
    new_pr={}
    while True:
        try:
            
            log.info(f'Extracting data from {project_full_name} repo')
            repo = g.get_repo(project_full_name)
            pr=repo.get_pull(number)
            #PRs_list = repo.get_pulls(state='all', sort='created', base='master')

            #for pr in PRs_list:
            try:
                    log.info(g.rate_limiting)
                    
                    log.info(f'Extracting data from PR # {pr.number}')
                    # Review Comments on the Pull requests
                    review_comments = []
                    if pr.get_comments().totalCount>0:
                        for comment in pr.get_comments():
                            cmt = {
                                'comment_id': comment.id,
                                'comment_body': comment.body,
                                'comment_created': comment.created_at,
                                'commenter': comment.user.login,
                                'type': comment.user.type
                            }
                            review_comments.append(cmt)
                    df_commits=[]
                    if pr.get_commits().totalCount>0:
                        for commit in pr.get_commits():
                            cmt = {
                            'commit_sha': commit.sha,
                            'committer_username': commit.author.login if commit.author is not None else '',
                            'committer_name': commit.author.name if commit.author is not None else '',
                            'committer_email': commit.author.email if commit.author is not None else '',
                            'commit_date': commit.author.created_at if commit.author is not None else '',
                            
                            }
                            df_commits.append(cmt)
                    df_labels=[]
                    if pr.get_labels().totalCount >0:
                         for label in pr.get_labels():
                              cmt={
                                   'name':label.name
                                   }
                              df_labels.append(cmt)
                    
                    time_ts=""
                    time_taken=0.0
                     
                    created=pr.created_at
                    closed=pr.closed_at
                    if created is not None and closed is not None:
                        time_t= closed-created
                        time_taken=time_t.total_seconds()
                        time_ts=str(time_t)
                        
                    new_pr= {
                        'pr_id': pr.id, # PRs features
                        'pr_title': pr.title,
                        'pr_body': pr.body,
                        'is_merged':pr.is_merged(),
                        'pr_number': pr.number,
                        'pr_url': pr.url,
                        'pr_html_url': pr.html_url,
                        'pr_state': pr.state,
                        'additions': pr.additions,
                        'deletions': pr.deletions,
                        'pr_changed_files': pr.changed_files,
                        'pr_commits_count': pr.commits,
                        'pr_comments_count': pr.comments,
                        'pr_review_comments_count': pr.review_comments,
                        'pr_labels_count': len([l.name for l in pr.labels]),
                        'pr_assignees_count': len(pr.assignees),
                        'pr_labels': [l.name for l in pr.labels],
                        'pr_created_at': created,
                        'pr_closed_at': closed,
                        'time_taken':time_taken,
                        'time_delta':time_ts,
                        'pr_review_comments': review_comments,
                        'pr_commits':df_commits,
                        'pr_labels':df_labels,
                        'contributor': pr.user.name,  # Contributor's information
                        'contributor_id': pr.user.id,
                        'contributor_email': pr.user.email,
                        'contributor_type': pr.user.type,
                        'contributions':pr.user.contributions,
                        'contributor_public_repos': pr.user.public_repos,
                        'contributor_private_repos': pr.user.owned_private_repos,
                        'contributor_followings': pr.user.following,
                        'contributor_followers': pr.user.followers,
                    }
                    #df_PR.append(new_pr)
                    #df_PR.append(extract_project_info(repo,pr.user.id))
            except RateLimitExceededException as e:
                    print(e.status)
                    print('Rate limit exceeded')
                    log.warning(f"{e.status}: PR Rate limit exceeded")
                    time.sleep(300)
                    continue
            except BadCredentialsException as e:
                    print(e.status)
                    print('Bad credentials exception')
                    log.warning(f"{e.status}: PR Bad credentials exception")
                    break
            except UnknownObjectException as e:
                    print(e.status)
                    print('Unknown object exception')
                    log.warning(f"{e.status}: PR Unknown status exception for {project_full_name} {number}")
                    log.warning(f"details: {e.message}")
                    break
            except GithubException as e:
                    print(e.status)
                    print('General exception')
                    log.warning(f"{e.status}: PR General exception")
                    break
            except requests.exceptions.ConnectionError as e:
                    print('Retries limit exceeded')
                    print(str(e))
                    log.warning(f"{str(e)}: PR Retries limit exceeded")
                    time.sleep(10)
                    continue
            except requests.exceptions.Timeout as e:
                    print(str(e))
                    print('Time out exception')
                    log.warning(f"{str(e)}: PR Timeout exception")
                    time.sleep(10)
                    continue

        except RateLimitExceededException as e:
            print(e.status)
            print('Rate limit exceeded')
            log.warning(f"{e.status}: PR project Rate limit exceeded")
            time.sleep(300)
            continue
        except BadCredentialsException as e:
            print(e.status)
            print('Bad credentials exception')
            log.warning(f"{e.status}: PR project Bad credentials exception")
            break
        except UnknownObjectException as e:
            print(e.status)
            print('Unknown object exception')
            log.warning(f"{e.status}: PR Project Unknown status exception for {project_full_name} {number}")
            log.warning(f"details: {e.message}")
            break
        except GithubException as e:
            print(e.status)
            print('General exception')
            log.warning(f"{e.status}: PR project general exception")
            break
        except requests.exceptions.ConnectionError as e:
            print('Retries limit exceeded')
            print(str(e))
            log.warning(f"{str(e)}: PR project Retries limit exceeded")
            time.sleep(10)
            continue
        except requests.exceptions.Timeout as e:
            print(str(e))
            print('Time out exception')
            log.warning(f"{str(e)}: Time out exception")
            time.sleep(10)
            continue
        break
    '''
    df_PRs = pd.DataFrame(df_PR)
    p_name=project_full_name.split("/")[1]
    filename=p_name+ "_"+str(number)+".csv"
    print(filename)
    df_PRs.to_csv(filename, sep=',', encoding='utf-8', index=True)
    '''
    return new_pr

#extract_project_PR('100daysofdevops/100daysofdevops',7)


def extract_project_info(project,contributor):
    ls_project=[]
    df_p={}
    while True:
            try:
                #g = Github(retry=2, timeout=5)
                log.info(f'Extracting data from {project} repo')
                repo = g.get_repo(project)
                PRs = repo.get_pulls(state='all')
                contributor_PR= [pr for pr in PRs if pr.user.id==contributor]
                c_prs=[]
                for c in contributor_PR:
                     
                     time_taken=0.0
                     time_ts=""
                     
                     created=c.created_at
                     closed=c.closed_at
                     if created is not None and closed is not None:
                          #print("getting out time")
                          time_t= closed-created
                          #print(time_t)
                          time_taken=time_t.total_seconds()
                          time_ts=str(time_t)
                         # print(time_taken)
                          
                     df={
                          "id":c.id,
                          "number":c.number,
                          "closed": closed,
                          "created":created,
                          "time_taken":time_taken,
                          "time_delta":time_ts,
                          "additions":c.additions,
                          "deletions":c.deletions,
                          "state":c.state
                     }
                     c_prs.append(df)
                df_p = {
                    'Project_ID': repo.id,
                    'Name': repo.name,
                    'Full_name': repo.full_name,
                    'Language': repo.language,
                    'Forks': repo.forks_count,
                    'Stars': repo.stargazers_count,
                    'Watchers': repo.subscribers_count,
                    'contributors':repo.get_contributors(anon='true').totalCount,
                    'commits':repo.get_commits().totalCount,
                    'issues':repo.get_issues().totalCount,
                    'branches':repo.get_branches().totalCount,
                    'PRs_count': PRs.totalCount,
                    'contributor pullrequests':c_prs
                }
                #ls_project.append(df_p)
                
            except RateLimitExceededException as e:
                print(e.status)
                print('Rate limit exceeded')
                log.warning(f"{e.status}: Rate limit exceeded")
                time.sleep(300)
                continue
            except BadCredentialsException as e:
                print(e.status)
                print('Bad credentials exception')
                log.warning(f"{e.status}: Bad credentials exceptipn")
                break
            except UnknownObjectException as e:
                print(e.status)
                print('Unknown object exception')
                log.warning(f"{e.status}: unknown status exception for {project} {contributor}")
                log.warning(f"details: {e.message}")
                break
            except GithubException as e:
                print(e.status)
                print('General exception')
                log.warning(f"{e.status}: General exception")
                break
            except requests.exceptions.ConnectionError as e:
                print('Retries limit exceeded')
                print(str(e))
                log.warning(f"{str(e)}: Retries limit exceeded")
                time.sleep(10)
                continue
            except requests.exceptions.Timeout as e:
                print(str(e))
                print('Time out exception')
                log.warning(f"{str(e)}: Time out exception")
                time.sleep(10)
                continue
            break
    return df_p
    #df_project = pd.DataFrame(ls_project)
    #df_project.to_csv('project_dataset_2.csv', sep=',', encoding='utf-8', index=True)
def extract_pull_number(url):
     if "pull" not in url:
          return "",0
     name=url.split("/")
     num=name[-1]
     if "#" in num:
          l_num= num.strip().split("#")
          num=l_num[0]
          
     if len(name) >3 and num.isdigit():
        project= name[-4]+"/"+name[-3]
        number=num
        return project,int(number)
     return "",0
def extract_pull_list(input):
     out=[]
     if(input.startswith('[')):
        input= input.strip("[]")
        out= [i.strip().strip("'") for i in input.split(',')]

     else:
          out.append(input)
     out= [extract_pull_number(i) for i in out]
     return out
track=0
if not os.path.exists(output_file):
      os.makedirs(output_file)
for line in csv.reader(input_handle):
    track+=1
    log.info(f"processing line: {track}")
    if track %100 ==0:
         print(track)
    try:
      name=line[3].strip().replace(" ","_")
      pulls=extract_pull_list(line[8])
      file_name=name+"_"+line[0]+".csv"
      file_name=os.path.join(output_file,file_name)
      output_handle = open(file_name, 'w', encoding='UTF-8', newline='',errors='ignore')
      writer_out = csv.writer(output_handle)
      projects=[]
      contributor=0
      first_pull=True
      first_project=True
      first_line=True
      for project,number in pulls:
            if project == "":
                  if first_line:
                       first_line=False
                       writer_error.writerow(line)
                  continue
            pr= extract_project_PR(project,number)
            if first_pull:
                 writer_out.writerow(pr.keys())
                 first_pull=False
            writer_out.writerow(pr.values())
            if project not in projects:
                  projects.append(project)
            if contributor ==0 or contributor==None:
                  contributor = pr['contributor_id']
            time.sleep(20)
      writer_out.writerow([])
      for project in projects:
            
            p_info = extract_project_info(project,contributor)
            if first_project:
                 writer_out.writerow(p_info.keys())
                 first_project=False
            writer_out.writerow(p_info.values())
            time.sleep(10)
      output_handle.close()
    except Exception as e:
         print(f"Error occured: {e}")
         log.warning(f"error: {e} ")
         writer_error.writerow(line)
         output_handle.close()
input_handle.close()
error_handle.close()
       
            

                  
#extract_pull_list("https://github.com/mixxxdj/mixxx/pull/2930")        
#extract_pull_number("https://github.com/scorelab/Codelabz/pulls?q=author%3Asakkshm26")