import requests
from bs4 import BeautifulSoup
import time
from IPython.display import HTML

#build the url link with searching data scientist job in Toronto
URL_1 = 'https://ca.indeed.com/jobs?q=data+scientist&l=Toronto&start'
HTML(URL_1)
job_counter = 0


def get_all_search_pages(URL_1):

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
    next_pages_links = "https://www.indeed.ca" + soup_1.find('div', {'class': 'pagination'}).find('a').get('href')[:-2]

    print(next_pages_links)

    # create empty list to store URLs of all search results pages
    List_of_all_URLs = []

    # add the first page to the 'List_of_all_URLs'
    List_of_all_URLs.append(next_pages_links)

    # add different starting positions for subsequent search results pages to 'List_of_all_URLs'
    for start_position in range(20, total_results, 20):
        List_of_all_URLs.append(next_pages_links + str(start_position))

    return List_of_all_URLs, total_results


List_of_all_URLs, total_results = get_all_search_pages(URL_1)
print("\n{0} links with search results pages generated and saved to 'List_of_all_URLs'.".format(len(List_of_all_URLs)) +
      " Search returned a total of {0} results\n".format(total_results))
print(List_of_all_URLs)

scraping_results_dict = {}  # this is a global dict used by 'scrape_job_info' to store scraping results to be parsed later


def scrape_job_info(job_search_results):

    global scraping_results_dict  # dict used to store results of scraping

    # loop over all <div> tags supplied by the function 'scrape_job_links_and_info'
    for x in job_search_results:
        # extract the individual job posting link from a <div> tag
        # res = x.find('a')['href']
        global job_counter
        title = x.find('div',{"class":"title"})
        job_href = title.find('a')['href']
        job_title = title.find('a')['title']
        job_link = "https://www.indeed.ca" + job_href
        job_counter+=1
        print("---------------------------------------------------------------------------------")
        print("==>Job #",job_counter,": ",job_title)
        print("==>Link:",job_link)

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


# run function 'scrape_job_links_and_info' to scrape every job posting from search results pages in 'List_of_all_URLs'
print("==========================================")
print("Soup Master on duty!===>")
print("==========================================\n")
scrape_job_links_and_info(List_of_all_URLs)
print(len(scraping_results_dict),"job postings have been scraped and saved to 'scraping_results_dict'.")

