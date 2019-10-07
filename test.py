#!/usr/bin/env python3

import sys, re, requests, json
from subprocess import PIPE, Popen

refname = sys.argv[1]
oldrev  = sys.argv[2]
newrev  = sys.argv[3]

pattern = re.compile(r'\[([A-Z]+?-\d+?)\]')
jira_api_url = 'https://poyntc.atlassian.net/rest/api/latest/issue/'
jira_login = 'illia.yushko@poynt.co'
jira_pass = 'UUQokeowTZVh9nYnnonY25F1'

print("Enforcing Policies...")
print('%s commits => from %s to %s' % (refname, oldrev[:6], newrev[:6]))

#Gets all commit hashes from branch
def get_commit_hashes():
    return Popen("git rev-list " +
    oldrev + ".." + newrev, shell=True, stdout=PIPE).stdout.read().decode('utf-8').strip().split("\n")

#Gets all commit comments from branch
def get_commit_comments():
    commitComents = []
    for commitId in get_commit_hashes():
        if commitId:
            comment = Popen("git cat-file commit " + commitId + " | sed '1,/^$/d'", 
            shell=True, stdout=PIPE).stdout.read().decode('utf-8').strip()
            commitComents.append(comment)
    return commitComents

#Checks that every commit has jira issue id in description
def get_issueIds():
    issueIds = []
    for comment in get_commit_comments():
        issueId = pattern.findall(comment)
        if not issueId:
            print('\x1b[1;31m\nJira issue id was not found in commit comment : \x1b[0m' + comment + "\n")
            exit(1)
        issueIds.append(issueId[0])
    return list(set(issueIds))

#Checks if issue ids are present in JIRA
def check_issueIds():
    for each in get_issueIds():
        r = requests.get(jira_api_url + each, auth=(jira_login, jira_pass))
        try:
            data = json.loads(r.text)['errorMessages']
            if data:
                print('\x1b[1;31m\nTask id specified in commit does not exist or release hook doesn\'t have permission to see it.\x1b[0m\n')
                exit(1)
        except KeyError:
            print('\x1b[1;42mSuccessfully checked.\x1b[0m')
            exit(0)

check_issueIds()