import requests, csv, os
from bs4 import BeautifulSoup
from datetime import date

'''
Scrape the cpu and gpu benchmark data from PassMark
'''

cwd = os.getcwd()

# Web page setup
# Header to be sent with request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
# URL to website
cpuURL = 'https://www.cpubenchmark.net/cpu_list.php'
gpuURL = 'https://www.videocardbenchmark.net/gpu_list.php'

# Scrape CPU data
cpuRequest = requests.get(cpuURL, headers=headers)
cpuSoup = BeautifulSoup(cpuRequest.text, features='html.parser')
cpuDataSoup = cpuSoup.find('tbody')

cpuFile = open(cwd + '/datasets/processor_data/cpu_data' + str(date.today()) + '.csv', 'w')
cpuWriter = csv.writer(cpuFile, quotechar="'")
cpuWriter.writerow(['CPU Name', 'CPU Mark'])
for cpuSoup in cpuDataSoup.contents:
    if cpuSoup == '\n':
        continue
    cpuName = cpuSoup.find('a').text
    cpuMark = cpuSoup.find_all('td')[1].text
    cpuWriter.writerow([cpuName, cpuMark])
cpuFile.close()

# Scrape GPU Data
gpuRequest = requests.get(gpuURL, headers=headers)
gpuSoup = BeautifulSoup(gpuRequest.text, features='html.parser')
gpuDataSoup = gpuSoup.find('tbody')

gpuFile = open(cwd + '/datasets/processor_data/gpu_data' + str(date.today()) + '.csv', 'w')
gpuWriter = csv.writer(gpuFile, quotechar="'")
gpuWriter.writerow(['GPU Name', 'GPU Mark'])
for gpuSoup in gpuDataSoup.contents:
    if gpuSoup == '\n':
        continue
    gpuName = gpuSoup.find('a').text
    gpuMark = gpuSoup.find_all('td')[1].text
    gpuWriter.writerow([gpuName, gpuMark])
gpuFile.close()