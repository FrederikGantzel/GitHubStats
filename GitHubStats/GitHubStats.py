from typing import Dict, Iterable
from urllib.request import urlopen
from datetime import datetime
import urllib.error
import json

#cd /mnt/c/Users/frede/OneDrive/Skrivebord/GitHubStats
#python3 GitHubStats.py


#The goal of this program is to fetch info about an input GitHub account,
#and then display some of that info, namely:
#the account's oldest repository, the accounts most used language,
#and the licenses the account uses.

class GitHubRepo:
    def __init__(self, name):
        self.name = name

        #The API can give a maximum of 100 repositories
        #If a user has more than 100 repositories, the repositories will
        #be split up into multiple pages, and i'm not sure how one would
        #go about getting the rest of the repositories
        self.url = f"https://api.github.com/users/{name}/repos?per_page=100"

        #Some error handling
        try:
            self.API_response = urlopen(self.url)
        #Page not found
        except urllib.error.HTTPError as e:
            self.API_response_code = 404
        #Could not connect
        except urllib.error.URLError as e:
            self.API_response_code = 500
        else:
            self.API_response_code = self.API_response.getcode()
            self.API_json = json.loads(self.API_response.read())

#Simple class containing the name of a language,
#and how many instances of that language has been counted.
#Also contains a function to increase the count by 1
class LanguageCount:
    def __init__(self, name):
        self.name = name
        self.count = 1
    def increase_count(self):
        self.count += 1

#Function that returns a LanguageCount instances index in a list,
#by searching for it's name. Returns -1 if no such instance could be found
def LanguageInList(name, list):
    for i in range(len(list)):
        if(list[i].name == name):
            return i
    return -1

#Function that finds the LanguageCount object with the highest count in a list,
#and returns it's name
def MostNumerousLanguage(list):
    result_lang = list[0].name
    highest_count = list[0].count
    for i in range(len(list)):
        if(list[i].count > highest_count):
            result_lang = list[i].name
            highest_count = list[i].count
    return(result_lang)

#Main
keep_loop = 1
while(keep_loop):
    username = input("Enter a GitHub username, or type \"end session\" to stop:\n")
    if(username == "end session"):
        keep_loop = 0
        break

    repo = GitHubRepo(username)

    if(repo.API_response_code == 404):
        print("")
        print(repo.API_response_code)
        print("Could not find user\n")
    elif(repo.API_response_code == 500):
        print("")
        print(repo.API_response_code)
        print("Connection could not be established\n")
    elif(len(repo.API_json) == 0):
        print(f"\nStats for {username}:")
        print(f"{username} has no public repositories\n")
    else:
        #The items we will keep track of are:
        #oldest repository, how many instances of each language, and licenses
        oldest_repo = repo.API_json[0]["name"]
        oldest_repo_date = datetime.strptime(repo.API_json[0]["created_at"],
            "%Y-%m-%dT%H:%M:%SZ")
        language_list = []
        license_list = []

        #Loop through all repositories
        for i in range(len(repo.API_json)):
            #We get the date and time of the currect repository.
            #If it is found to be older than the current oldest repository,
            #its name and date is saved as the new oldest repository.
            current_repo_date = datetime.strptime(repo.API_json[i]["created_at"],
                "%Y-%m-%dT%H:%M:%SZ")
            if(current_repo_date < oldest_repo_date):
                oldest_repo = repo.API_json[i]["name"]
                oldest_repo_date = current_repo_date

            #Using the LanguageInList function, we find the index of The
            #language of the current repository, and increase its count by 1.
            #If the language has not yet been added to the list
            #(signified by its position being -1) it is added to the list.
            current_repo_lang = repo.API_json[i]["language"]
            lang_position = LanguageInList(current_repo_lang, language_list)
            if(lang_position < 0):
                language_list.append(LanguageCount(current_repo_lang))
            else:
                language_list[lang_position].increase_count()

            #For licenses, we only need to keep track of what licenses are used,
            #not how many of each license are used.
            #Thus, we use the built-in "index" method to see if the license
            #of the current repository is already on the list of licenses.
            #If the index method throws an error (because the license is not
            #on the list), we simply add it to the list.
            if(repo.API_json[i]["license"] != None):
                try:
                    license_list.index(repo.API_json[i]["license"]["name"])
                except:
                    license_list.append(repo.API_json[i]["license"]["name"])

        #Print out the stats
        print(f"\nStats for {username}:")
        print(f"  - Oldest repo: {oldest_repo}")
        print(f"  - Favorite Language: {MostNumerousLanguage(language_list)}")
        if(len(license_list) > 0):
            print(f"  - Licenses used:")
            for license in license_list:
                print(f"   - {license}")
        else:
            print(f"  - Licenses used: None")
        print("")

        #Some tests
        #since the GitHub API will give a maximum of 100 repositories,
        #there should not be more than 100 repositories in the GitHubRepo object
        assert len(repo.API_json) <= 100
        #all the counts in the language_list should add up to be equal to
        #the total number of repositories
        total_language_instances = 0
        for i in range(len(language_list)):
            total_language_instances += language_list[i].count
        assert len(repo.API_json) == total_language_instances
        #The API_response_code for the GitHubRepo object should be 200
        #if the HTTP request was successful
        assert repo.API_response_code == 200
