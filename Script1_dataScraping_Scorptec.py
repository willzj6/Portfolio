import requests, csv, os, re, logging, time
from bs4 import BeautifulSoup
from datetime import date

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.disable(logging.DEBUG)

"""
Scrape all laptops and their specs availble for sale from Scorptec.

Data to be scraped:
Name [0]
ProductCode [1]
Price [2]
Processor [3]
RAM/Memory [4]
Graphics [5]
Storage [6]
Display [7]
"""
COLUMNS = ['NAME', 'PRODUCTCODE', 'PRICE', 'PROCESSOR', 'MEMORY', 'GRAPHICS', 'STORAGE', 'DISPLAY']

# Web page setup
# Header to be sent with request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
# URL to website
mainURL = 'https://www.scorptec.com.au/product/laptops-&-notebooks'
domainURL = 'https://www.scorptec.com.au'

# FUNCTIONS
def newSpecs():
    # Return a new empty specs dictionary with all values set to None
    specs = {}
    for column in COLUMNS:
        specs[column] = None
    return specs

def scrapeData(productURL):
    # Scrape the specs from the html and returns them in a specs dictionary

    # Sleep so connection doesn't get cut
    time.sleep(1)

    # Request the product html page
    productRequest = requests.get(productURL, headers= headers)
    productSoup = BeautifulSoup(productRequest.text, features='html.parser')

    # Write the html to a file for debugging
    # with open('debug.html', 'w') as f:
    #     f.write(productRequest.text)

    # Create new empty specs dictionary
    specs = newSpecs()
    # Scrape the name, product code and price
    name = productSoup.find("h1", class_ = "product-page-title")
    specs['NAME'] = name.text.strip().split('\xa0')[0]
    productCode = productSoup.find("div", class_ = "product-page-model mb-4")
    specs['PRODUCTCODE'] = productCode.text.strip()
    price = productSoup.find("div", class_ = "product-main-price")
    specs['PRICE'] = price.text.strip()
    
    productDesc = productSoup.find(class_="product-page-desc").text
    productSpecs = productDesc.split(',')
    # Using Memory to check if the columns are correctly formatted
    if extractMemory(productSpecs[2]) == '':
        if extractMemory(productSpecs[3])!= '':
            # The description has a colour column
            del productSpecs[1]
        elif extractMemory(productSpecs[1]) != '':
            processorIn0 = extractProcessor(productSpecs[0])
            processorIn1 = extractProcessor(productSpecs[1])
            if processorIn0 != '':
                # Processor mixed into column 1, split out the processor
                productSpecs.insert(1, processorIn0)
            elif processorIn1 != '':
                # Processor and RAM mixed together in column 1
                productMemory = extractMemory(productSpecs[1])
                productSpecs.insert(1, processorIn1)
                productSpecs[2] = productMemory
            else:
                raise Exception('PRODUCT DESCRIPTION COLUMNS INVALID: ' + str(productSpecs))
    
    specs['PROCESSOR'] = productSpecs[1].strip()
    specs['MEMORY'] = productSpecs[2].strip()
    specs['STORAGE'] = productSpecs[3].strip()
    specs['DISPLAY'] = productSpecs[4].strip()
    specs['GRAPHICS'] = productSpecs[5].strip()
    return specs

def extractProcessor(text):
    # Return the processor name from a string of text
    processorRegex = re.compile(r'((AMD|Intel|Ryzen|Core|i\d).*\d{4,}\w{1,2})(\s|,)?', re.IGNORECASE)
    processor = processorRegex.search(text)
    if processor != None:
        return processor.group(1)
    else:
        return ''

def extractMemory(text):
    memoryRegex = re.compile(r'(\d{1,2}\s?GB).*(DDR(4|5)|RAM)')
    memory = memoryRegex.search(text)
    if memory !=  None:
        return memory.group(1)
    else:
        return ''

def writeCsvLine(specs):
    # Writes the specs data to the csv file.
    writerSpecs = []
    for column in COLUMNS:
        writerSpecs.append(specs[column])
    dataWriter.writerow(writerSpecs)

def getProductURLs(pageURL, productURLs):
    # Find all product URLs on a page
    
    # Sleep to maintain connection
    time.sleep(1)
    logging.info(pageURL)
    pageRequest = requests.get(pageURL, headers=headers)
    pageSoup = BeautifulSoup(pageRequest.text, features='html.parser')
    # Product URLs are under class: inherit-class
    hrefPageSoup = pageSoup.find_all(class_='inherit-class')
    for tag in hrefPageSoup:
        productURL = tag.get('href')
        # If the tag is hidden, there href is empty and so the tag should be skipped
        if productURL != '':
            productURLs[productURL]= tag.text.strip()
    return

# Create .csv file
# TODO add time to the csv file name
cwd = os.getcwd()
dataFile = open(cwd + '/datasets/laptop_data/scorptec' + str(date.today()) +'.csv', 'w', newline='')
dataWriter = csv.writer(dataFile, quotechar="'")
dataWriter.writerow(COLUMNS)

# Create logger file
logger = open(cwd + '/logs/log' + str(date.today()) +'.txt', 'w')
# URLwriter = open('URLs.txt', 'w')

# Loop through each page of each category and store the product URLs in productURLs
# Using a dictionary to avoid doubling up on products repeating in different categories
productURLs = {}
mainRequest = requests.get(mainURL, headers=headers)
mainSoup = BeautifulSoup(mainRequest.text, features='html.parser')
hrefMainSoup = mainSoup.find_all('div', class_='grid-subcategory-title')
for link in hrefMainSoup:
    if re.match(r'.*Laptops.*',link.find('a')['title']):
        categoryURL = domainURL + link.find('a').get('href')
        # Request category page HTML
        categoryRequest = requests.get(categoryURL, headers=headers)
        categorySoup = BeautifulSoup(categoryRequest.text, features='html.parser')
        # Get how many pages is in the category
        categoryPageNum = categorySoup.find_all('a', class_='page-link')[-2].text
        # Loop through each page of the category
        for i in range(int(categoryPageNum)):
            pageURL = categoryURL + '?page=' + str(i+1)
            logging.debug(pageURL)
            getProductURLs(pageURL, productURLs)


# for product, URL in productURLs.items():
#     URLwriter.writelines(f'{product}\n{URL}\n\n')

print("\n\nExtracting Specs\n\n")

# Iterate through every page in productURLs and scrape the laptop date
for URL in productURLs.keys():
    # Try 4 times in case of server error
    for x in range(0, 4):
        sleepTimer = 1
        error = None
        try:
            specs = scrapeData(URL)
            writeCsvLine(specs)
            print(f"\n\nProduct: {specs['NAME']}\
                \nLink: {URL}\
                \nProduct Code: {specs['PRODUCTCODE']}\
                \nPrice: {specs['PRICE']}\
                \nProcessor: {specs['PROCESSOR']}\
                \nMemory: {specs['MEMORY']}\
                \nGraphics: {specs['GRAPHICS']}\
                \nStorage: {specs['STORAGE']}\
                \nDisplay: {specs['DISPLAY']}\
                ")
        except Exception as e:
            error = str(e)
            logging.warning('n' + error)
            logging.warning(URL)
            if x == 3:
                logger.writelines(URL + '\n')
                logger.writelines(error + '\n\n')
            pass
        
        if error:
            time.sleep(sleepTimer)
            sleepTimer *= 2
        else:
            break

# Close csv file
dataFile.close()
logger.close()