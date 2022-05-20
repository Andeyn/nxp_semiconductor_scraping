# NXP Semiconductor Web Scraping


### Overview ### 
The purpose of this repository is to scrape the [NXP Website](https://www.nxp.com/search?category=products&start=0&keyword=datasheets&filter=deviceTax%3E%3Ec731&selectedCategory=Products) of only the Processors and Microcontrollers to identify design commonalities of overlapping categories that contain datasheets. 

This is intended to serve as a proof of concept that it is possible to identify design commonalities among datasheets. 

NXP's website is dynamic, so this codebase uses Python and [Selenium's webdriver](https://www.selenium.dev/documentation/webdriver/) that refreshes NXP's website every second to scrape all the urls to the datasheets.

### Things to note: ###
1. There are 33 different categories and subcategories. 
  - _ProcessorsAndMicrocontrollers.csv_ contains a filter,name,url with 1) filter as the category, 2) the name as the subcategory, and 3), url with the respective link to it.

2. Each datasheet is set as a unique identifier based on its unique url to determine the overlap
  - **NOTE** some datasheet urls link to another page that contains more URLs. Hence, they are described in this dataset as datasheet/datasheet families.

### Python Scripts ### 
1. **_nxp_pmc_scraper.py_** uses the webdriver to retrieve all links to the datasheets. These are all placed into csv's based on their categories in the _nxp_pmc_ directory.
2. **_cleaning_data.py_** performs data analysis on the csv's found in the _nxp_pmc_ directory. This performs the following:
    1. Uses each unique url as a key to in a dictionary. 
    2. Uses the path name of that csv (i.e. Automotive_ADASAndHighlyAutomatedDriving.csv) as a value
    3. Determines the overlap count between the existing keys and places it into a matrix seen in _matrix_count.csv_

### CSV Files ###
1. _ProcessorsAndMicrocontrollers.csv_ contains all the urls that does the intial scraping.
2. _matrix_count.csv_ is the inital count of all the overlapping categories.
3. _pair_count.csv_ is a histogram of the rankings of the highest pair counts

### Output Figures in CSV ###
1. FIGURE 1: major_category.csv
3. FIGURE 2: largest_subcategories_diff_group.csv
4. FIGURE 3: automotive_commonality.csv
5. FIGURE 4: Industrial_commonality.csv

### Future Work: ###
1. To perform this on more of the categories. One would need to automate scraping the URLs for each new category and subcategories (i.e. Arm Microcontrollers, General Purpose MCUs)
2. Download all PDFs including the datasheet families (urls that link to more urls). 
