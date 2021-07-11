import requests
import json
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import os
import pickle
import sys


class case_extractor:
    '''input the year'''
    def __init__(self, year):
        self.year = str(year)
        self.next_year = str(int(self.year)+1)

        try:
            with open(os.path.join('html_years',self.year+'-'+self.next_year+' Term _ Oyez.html'), 'r') as f:
                self.year_soup = BeautifulSoup(f.read(), 'html.parser')
        except:
            self.year_soup = None
            print('case list for %s has not been downloaded' %self.year)

        try:
            self.df = pd.read_csv(os.path.join('data', 'case_list', self.year+'_list.csv'))
        except:
            self.df = None
        
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('data/case_list'):
            os.mkdir('data/case_list')
        if not os.path.exists('data/cases_metadata'):
            os.mkdir('data/cases_metadata')
        if not os.path.exists('data/transcripts'):
            os.mkdir('data/transcripts')
    
    def get_case_list(self):
        '''If for the year html_years folder doesn't contain the corresponding file then run get_case_list'''
        case_list = []
        case_list_soup = self.year_soup.find('ul', attrs={'class':"index ng-scope"})
        case_items = case_list_soup.find_all('li')
        for item in case_items:
            link = item.find('a')
            case_list.append((link.text, link['href']))
        try:
            self.df = pd.DataFrame(case_list, columns = ['case_title', 'link'])
            self.df.to_csv(os.path.join('data', 'case_list', self.year+'_list.csv'), index=False)
            print('saved %s case list' %self.year)
        except:
            print('Error in saving %s case list' %self.year)

    def download_cases(self):
        ''' Adjust the sleep time and check data/transcripts folder for the json files corresponding to the case proceedings'''
        all_case_metadata = []

        for row in self.df.values:
            y, case_num = row[-1].split('/')[-2:]
            if not os.path.exists(os.path.join('data', 'transcripts', y)):
                os.mkdir(os.path.join('data','transcripts', y))
            case_link = '/'.join(['https://api.oyez.org/cases', y, case_num])+'?labels=true'
            resp_json = requests.get(case_link).json()
            all_case_metadata.append((y, case_num, resp_json))
            case_id = str(resp_json['ID'])
            transcript_url = 'https://api.oyez.org/case_media/oral_argument_audio/'+case_id
            sleep(3)

            # if resp_json['oral_argument_audio'] is not None:

            #     output = requests.get(transcript_url).json()
            #     print(output)
            #     return None

            #     with open(os.path.join('data', 'transcripts', y, case_id+'.json'), 'w') as f:
            #         json.dump(transcript_json, f, indent=4)
            # else:
            #     print("No transcript because no oral argument is available.")
                
        with open(os.path.join('data', 'cases_metadata', y+'.pkl'), 'wb') as f:
            pickle.dump(all_case_metadata, f)





if __name__ == '__main__':
    year = input("Please input a year for which to extract cases:\n")
    cases = case_extractor(year)
    func = input("Which function would you like to run? (1 for get_case_list, 2 for download_cases)\n")
    if func == str(1):
        cases.get_case_list()
    elif func == str(2):
        cases.download_cases()
    else:
        print("Input invalid. Exiting.")
        sys.exit()



#https://api.oyez.org/case_media/oral_argument_audio/25115