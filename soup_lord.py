import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
from IPython.display import HTML



test_scraping_results_dict = ["https://www.indeed.ca/rc/clk?jk=e1f406a12e97e209&fccid=c71c81e6ff3d20a6&vjs=3","https://www.indeed.ca/rc/clk?jk=f83ee262b276c200&fccid=9917de3c28f569f6&vjs=3","https://www.indeed.ca/rc/clk?jk=38ceed478d6c5c9e&fccid=82179ab8760b598c&vjs=3"]

python_counter = 0
for each_page in test_scraping_results_dict:
    # get the HTML of the search results page
    page = requests.get(each_page)
    content = page.text
    soup = BeautifulSoup(content, 'lxml')
    main = soup.find('div',{"class":"jobsearch-JobComponent-description icl-u-xs-mt--md"})
    if ("python" in str(main).lower()):
        python_counter += 1
print (python_counter)
