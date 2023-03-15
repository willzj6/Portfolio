import requests, csv, os, re, logging, time
from bs4 import BeautifulSoup
from PIL import Image
from pytesseract import pytesseract

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')

"""
Scrape relevant laptop data from Scorptec.
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
ALTERNATE_SPEC_NAMES = {'PROCESSOR': ['Processor', 'CPU'],
                        'MEMORY': ['Memory', 'RAM'],
                        'GRAPHICS': ['Graphics', 'GPU'],
                        'STORAGE': ['Storage', 'SSD', 'HDD', 'CAPACITY'],
                        'DISPLAY': ['Display']}

# Web page setup
# Header to be sent with request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
# url to scrape from
mainURL = 'https://www.scorptec.com.au/product/laptops-&-notebooks'
domainURL = 'https://www.scorptec.com.au'

# Tesseract setup
tesseractPath = '/opt/homebrew/Cellar/tesseract/5.3.0_1/bin/tesseract'
pytesseract.tesseract_cmd = tesseractPath


# FUNCTIONS
def newSpecs():
    # create a new empty specs dictionary with all values set to None
    specs = {}
    for column in COLUMNS:
        specs[column] = None
    return specs

def scrapeTable(specSoup, specs):
    # Scrapes the laptop specs from pages with a table
    # Input beautifulsoup object, and specs dictionary
    specs['PROCESSOR'] = specSoup.find(data = "Processor").find(class_ = "rightValue").text
    specs['MEMORY'] = specSoup.find(data = "Memory").find(class_ = "rightValue").text
    specs['GRAPHICS'] = specSoup.find(data = "Graphics").find(class_ = "rightValue").text
    specs['STORAGE'] = specSoup.find(data = "Storage").find(class_ = "rightValue").text
    specs['DISPLAY'] = specSoup.find(data = "Display").find(class_ = "rightValue").text
    return

def scrapeImage(specSoup, specs):
    # scrape the laptop data from pages with the specs saved as an image
    # remember to clear data in specs

    # get image source URL
    imageSRC = specSoup.find('img')
    imageURL = imageSRC.get('src')
    imgResponse = requests.get(imageURL)
    # download specs sheet image
    imgFile = cwd + '/img_data/' +specs['PRODUCTCODE'] + '.jpg'
    with open(imgFile, 'wb') as f:
        f.write(imgResponse.content)
    image = Image.open(imgFile)
    # extract text from the image
    laptopSpecsString = pytesseract.image_to_string(image)
    logging.debug('\nSTART IMAGE TEXT:\n' + laptopSpecsString + '\nEND IMAGE TEXT')
    # check the first word of each row, if it matches any of the specs wanted
    columnPattern = r'^(\w+)\s+(.*)$'
    for line in laptopSpecsString.splitlines():
        match = re.match(columnPattern, line)
        # check if theres data on the line
        if match:
            # check if the data is one of the ones we want
            for specName, altSpecNames in ALTERNATE_SPEC_NAMES.items():
                if match.group(1) in altSpecNames:
                    # incase there is a second line, the critical info is always in the first line
                    if specs[specName] == None:
                        specs[specName] = match.group(2)            
    return

def scrapeData(productURL):
    # Scrape the specs from the html and returns them in a specs dictionary
    time.sleep(1)

    # Request the product html page
    productRequest = requests.get(productURL, headers= headers)
    productSoup = BeautifulSoup(productRequest.text, features='html.parser')

    # Create new empty specs dictionary
    specs = newSpecs()
    # Scrape the name, product code and price
    # TODO refactor this and remove the unnecessary variables
    name = productSoup.find("h1", class_ = "product-page-title")
    specs['NAME'] = name.text.strip()
    logging.debug(specs['NAME'])
    productCode = productSoup.find("div", class_ = "product-page-model mb-4")
    specs['PRODUCTCODE'] = productCode.text.strip()
    logging.debug(specs['PRODUCTCODE'])
    price = productSoup.find("div", class_ = "product-main-price")
    specs['PRICE'] = price.text.strip()
    logging.debug(specs['PRICE'])

    # Scrape the laptop specs
    specSoup = productSoup.find(id = "product-specs-value")
    if specSoup.find('table'):
        scrapeTable(specSoup, specs)
    elif specSoup.find('img'):
        scrapeImage(specSoup, specs)
    
    return specs

def writeCsvLine(specs):
    writerSpecs = []
    for column in COLUMNS:
        writerSpecs.append(specs[column])
    dataWriter.writerow(writerSpecs)

def getProductURLs(pageURL, productURLs):
    time.sleep(1)
    pageRequest = requests.get(pageURL, headers=headers)
    pageSoup = BeautifulSoup(pageRequest.text, features='html.parser')
    hrefPageSoup = pageSoup.find_all(class_='inherit-class')
    for link in hrefPageSoup:
        productURLs[link.text]= link.get('href')
    return productURLs

# Create .csv file
# TODO add time to the csv file name
cwd = os.getcwd()
dataFile = open(cwd + '/datasets/laptop_data/scorptec.csv', 'w', newline='')
dataWriter = csv.writer(dataFile, quotechar="'")
dataWriter.writerow(COLUMNS)


# htmlFile = open('htmlFile.txt', 'w')
# htmlFile.write(res.text)
# htmlFile.close

# Get the link to all product pages
productURLs = {}

# Loop through each page of each category and get the product URLs in productURLs
mainRequest = requests.get(mainURL, headers=headers)
mainSoup = BeautifulSoup(mainRequest.text, features='html.parser')
hrefMainSoup = mainSoup.find_all('div', class_='grid-subcategory-title')
for link in hrefMainSoup:
    if re.match(r'.*Laptops.*',link.find('a')['title']):
        categoryURL = domainURL + link.find('a').get('href')
        # Request category page HTML
        categoryRequest = requests.get(categoryURL, headers=headers)
        categorySoup = BeautifulSoup(categoryRequest.text, features='html.parser')

        htmlFile = open('htmlFile2.txt', 'w')
        htmlFile.write(categoryRequest.text)
        htmlFile.close

        # Get how many pages is in the category
        logging.debug(categorySoup.find_all('a', class_='page-link'))
        categoryPageNum = categorySoup.find_all('a', class_='page-link')[-2].text
        # Loop through each page of the category
        for i in range(int(categoryPageNum)):
            pageURL = categoryURL + '?page=' + str(i+1)
            logging.debug(pageURL)
            productURLs = getProductURLs(pageURL, productURLs)

# iterate through every page and scrape the data
# specs = scrapeData(pageURL)
# writeCsvLine(specs)

# Close csv file
dataFile.close()