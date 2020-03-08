import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np
from IPython.display import HTML

#######################################################
##########         Functions             ##############
#######################################################
def get_all_search_pages(URL_1):
    '''
    This function gets all job search results
    :param URL_1:
    :return:
    '''

    # get the HTML of the first search results page
    r = requests.get(URL_1)
    content = r.text

    # make a soup out of the first page of search results
    soup_1 = BeautifulSoup(content, 'lxml')

    # extract the number of search results
    num_results_str = soup_1.find('div', {'id': 'searchCount'}).text
    # parse the string and extract the total number (4th element), replace comma with an empty space, convert to int
    total_results = int(num_results_str.split()[3].replace(',', ''))

    # add the common part between all search pages
    if soup_1.find('div', {'class': 'pagination'}) is not None:
        next_pages_links = "https://www.indeed.ca" + soup_1.find('div', {'class': 'pagination'}).find('a').get('href')[:-2]
    else:
        next_pages_links = URL_1

    print(next_pages_links)

    # create empty list to store URLs of all search results pages
    List_of_all_URLs = []

    # add the first page to the 'List_of_all_URLs'
    List_of_all_URLs.append(next_pages_links)

    # add different starting positions for subsequent search results pages to 'List_of_all_URLs'
    if soup_1.find('div', {'class': 'pagination'}) is not None:
        for start_position in range(20, total_results, 20):
            List_of_all_URLs.append(next_pages_links + str(start_position))

    return List_of_all_URLs, total_results

def scrape_job_info(job_search_results):
    '''
    This function
    :param job_search_results:
    :return:
    '''

    global scraping_results_dict  # dict used to store results of scraping

    # loop over all <div> tags supplied by the function 'scrape_job_links_and_info'
    for x in job_search_results:
        # extract the individual job posting link from a <div> tag
        # res = x.find('a')['href']

        global job_counter
        global df
        global skills_keywords_dict
        global df_column_names
        global current_search_location
        global total_results
        title = x.find('div',{'class':"title"})
        job_href = title.find('a')['href']
        job_title = title.find('a')['title']
        job_link = "https://www.indeed.ca" + job_href

        #Get into individual page
        page = requests.get(job_link)
        content = page.text
        soup = BeautifulSoup(content, 'lxml')
        JobContent = soup.find('div', attrs={"class": "jobsearch-ViewJobLayout-jobDisplay"})
        str_job = str(JobContent).lower()



        ##############insert df
        temp_dict = dict(zip(df_column_names, [None]*len(df_column_names)))
        temp_dict['Job_Name'] = job_title
        temp_dict['Link'] = job_link
        temp_dict['Job_Location'] = current_search_location
        #search the content to collect data
        for key in skills_keywords_dict:
            # 'Technical Skills'
            for sub_key in skills_keywords_dict[key]:
                #'Machine Learning'
                key_words_list =skills_keywords_dict[key][sub_key]
                # ['Machine Learning', 'ML','Predictive Modeling']
                for key_word in key_words_list:
                    key_word_lower = key_word.lower()
                    if (key_word_lower in str_job):  # Key word has to be lower letter!!!
                        temp_dict[sub_key] = 1
                        break

        ##insert
        df = df.append(temp_dict,ignore_index=True)
        job_counter+=1
        print("---------------------------------------------------------------------------------")
        print("==>Job #",job_counter,": ",job_title)
        # print("==>Link:",job_link)
        print("==>progress", job_counter, "/", total_results)

        # get the HTML code from the job posting page and save it as text to 'scraping_results_dict'
        # link to the job posting is used as a key and HTML code of the job posting as a value
        job_html = requests.get(job_link)
        scraping_results_dict[job_link] = job_html.text

        # sleep for 0.5 second, to avoid too many requests to the indeed.ca server
        time.sleep(0.5)

def scrape_job_links_and_info(List_of_all_URLs):

    # loop over all pages in 'List_of_all_URLs' to extract links to each job posting
    for page_url in List_of_all_URLs:
        # get the HTML of the search results page
        page = requests.get(page_url)
        content = page.text
        # make a soup out of the HTML
        soup = BeautifulSoup(content, 'lxml')

        # find all <div> tags containing each job posting links and feed them to the function 'scrape_job_info'
        results = soup.find_all('div', {'class': 'jobsearch-SerpJobCard unifiedRow row result'})
        scrape_job_info(results)

    print("Done!")


#######################################################
##########           Main                ##############
#######################################################

skills_keywords_dict = {
    'Technical Skills': {
        # 0. Basic Mathmatics
        'Mathematics': ['Math'],
        'Statistics': ['probability', 'Statistics', 'Stochastic'],
        'Linear Algebra': ['Linear Algebra', 'Algebra', 'matrix'],

        # 1. Programming Language
        'Python': ['Python'],
        'R': [' R ', ' R/', ' R,', ' R.'],
        'Java': [' Java ', 'JVM'],
        'Scala': ['Scala'],
        'C/C++': ['C/C++', 'C++', ' C ', 'C#'],
        'MATLAB': ['MATLAB'],
        'Excel': ['Excel', 'VBA', 'Pivot Table'],
        'SAS': [' SAS '],
        'Object-oriented programming': ['Object-oriented', ' OOP ', ' OOP/', ' OOP,', ' OOP.'],

        # 2. Data Management
        'SQL/databases': ['SQL', 'databases'],
        'NoSQL': ['NoSQL', 'Cassandra', 'MongoDB'],
        'SPSS': ['SPSS'],
        'Stata': ['Stata'],
        'Access': ['Access'],
        'Data Mining/Analytics': ['Data Mining', ' DM ', 'Analytics', 'Data Collection'],

        # 3. Data Visulization
        'Visualisation': ['Visualisation', 'Visualization', 'render'],
        'Tableau': ['Tableau'],
        'Power BI': ['Power BI'],
        'Matplot': ['Matplot'],

        # 4. Machine Learning
        'Machine Learning': ['Machine Learning', 'ML', 'Predictive Modeling'],
        'KNN': ['KNN', 'nearest neighbour', 'nearest neighbor'],
        'SVM': ['SVM', 'Support Vector'],
        'K-means': ['K-means', 'K means'],
        'Multivariate Analysis': ['pca', 'principal component', 'pls'],
        'Regression': ['Regression', 'Regressive'],
        'Classification': ['Classification', 'Clustering'],
        'NLP': ['Natural Language Processing', ' NLP ', ' NLP/', ' NLP,', ' NLP.'],
        'Deep Learning': ['Deep Learning', 'Neural Networks', 'ANN', 'MLP', 'CNN', 'Tensorflow', 'Keras', 'Theano'],
        'Time-series': ['Time-series', 'time series'],
        'Simulation': ['simulation'],

        # 5. Cloud Computing
        'Big Data': ['Big Data', 'Spark', 'kafka', 'Hive',
                     'beam', 'Hadoop', 'MapReduce', 'Hbase',
                     'Coudera', 'Hortonworks', 'Apache'],
        'AWS Cloud': ['AWS'],
        'Google Cloud': ['Google Cloud', 'GCP'],
        'Databricks': ['Databricks'],
        'Azure': ['Azure'],
        'IBM Cloud': ['IBM Cloud', 'Watson'],

        # 6. DevOps
        'API': [' API ', 'application program interface', ' API/', ' API,', ' APL.'],
        'Operations research': ['Operations research'],
        'DevOps': ['DevOps', 'TDD', 'test-driven'],
        'Git': ['GitHub', 'Git', 'version control']},

    'softs skills': {'Critical Thinking': ['Critical', 'insight', 'perpective'],
                     'Effective Communication': ['communication', 'presentation', 'interpersonal', 'negotiation'],
                     'Problem Solving': ['problem solving', 'problem-solving'],
                     'Team building': ['Team leadership', 'team building', 'team player'],
                     'Work Ethic': ['ethic'],
                     'Project Management': ['project management', 'project_management'],
                     'Time Management': ['Time Management', 'Prioritization'],
                     'Management': ['management', 'Data management'],
                     'Innovation': ['innovation', 'innovative', 'curiosity'],
                     'Leadership': ['Leadership'],
                     'SDLC': ['SDLC', 'sdlc', 'software development', 'lifecycle'],
                     'Decision Making': ['decision-making', 'decision analysis'],
                     'Consulting': ['consulting', 'consultant']}
}

# build the url link with searching data scientist job in Toronto
#This url below has many pages of job postings
search_urls = {
    'Data+Toronto' : 'https://ca.indeed.com/jobs?q=data+scientist&l=Toronto&start',
    'Data+Vancouver' : 'https://ca.indeed.com/jobs?q=data+scientist&l=Vancouver&start',
    'Data+Montreal' : 'https://ca.indeed.com/jobs?q=data+scientist&l=Montreal&start',
}

search_key = 'Data+Toronto'

job_counter = 0
List_of_all_URLs, total_results = get_all_search_pages(search_urls[search_key])
print("\n{0} links with search results pages generated and saved to 'List_of_all_URLs'.".format(len(List_of_all_URLs)) + " Search returned a total of {0} results\n".format(total_results))

scraping_results_dict = {}  # this is a global dict used by 'scrape_job_info' to store scraping results to be parsed later
current_search_location = search_key.split("+")[1]
df_column_names = ['Job_Name','Link','Job_Location']

for key in skills_keywords_dict:
    for sub_key in skills_keywords_dict[key]:
        df_column_names.append(sub_key)

#Append df
df = pd.DataFrame(columns=df_column_names)

# run function 'scrape_job_links_and_info' to scrape every job posting from search results pages in 'List_of_all_URLs'
print("==========================================")
print("Soup Master on duty!===>")
print("==========================================\n")
scrape_job_links_and_info(List_of_all_URLs)
print(len(scraping_results_dict),"job postings have been scraped and saved to 'scraping_results_dict'.")
print(df)
file_name = search_key
save_file_name = file_name+".csv"
df.to_csv(save_file_name)

