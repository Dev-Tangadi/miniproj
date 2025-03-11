# miniproj

Project Overview

This project is a web scraping tool that automates data extraction from the AgMarknet website, which provides daily crop price and arrival reports. The main objective is to gather data for specified crops over a period of time and save the information in CSV format.

Key Features

Automated Data Extraction:
The tool uses Selenium to navigate the AgMarknet website, interact with elements (like date links and checkboxes), and retrieve crop data automatically.

Multi-Day Scraping:
The script is designed to scrape data for the previous 60 days as well as the current day's data, ensuring comprehensive historical records.

CSV Output:
Instead of saving the data in JSON format, the script directly converts the scraped data into CSV files. Each file is named after the day of data extraction, making it easy to organize and reference.

Dynamic Data Handling:
The script includes functionality to convert string representations of numbers into actual numeric types (integer or float) where appropriate. This ensures the data is stored in a more usable format.

Crop Configuration File:
A separate configuration file (for example, crop_dict.txt) is used to specify the crops to be scraped along with their associated checkbox IDs on the website. This allows for easy updates and customization without modifying the main code.

Prerequisites

Python Environment:
Ensure Python 3.x is installed.

Selenium Library:
The script uses Selenium for browser automation. You'll need to install Selenium via pip.

Web Browser and Driver:
The tool is built for use with the Chrome browser. You must download the appropriate ChromeDriver that matches your version of Chrome and update the driver path in the script.

How It Works

Setup and Initialization:
The script begins by reading crop configuration details from a file. It then sets up Selenium with the required ChromeDriver.

Navigating the Website:
The script accesses the AgMarknet website and clicks on links corresponding to specific days. For each day (including the last 60 days and today), it navigates to the daily report page.

Data Selection:
Using the crop configuration, the script selects the relevant checkboxes for each crop, ensuring that only the desired data is fetched.

Data Extraction and Conversion:
After clicking the “Submit” button, the script waits for the data table to load. It then iterates over the table rows, converts string values to numbers when possible, and appends a date field to each record.

CSV File Creation:
Instead of storing the results in JSON, the script writes the collected data to a CSV file for each day. This approach makes the data easily accessible and ready for further analysis.

Usage Instructions

Configuration:
Update the crop configuration file with crop names and corresponding checkbox IDs as found on the AgMarknet website.

Driver Path:
Modify the ChromeDriver path in the script to point to the correct location on your system.

Running the Script:
Once everything is configured, execute the script. The tool will iterate over the previous 60 days and the current day, scrape the data, and save each day’s data into separate CSV files.

Troubleshooting and Contributions

Common Issues:
If elements are not found or the page takes longer to load, consider increasing the timeout duration in the script’s wait statements. Also, verify that the crop IDs in your configuration file match the actual IDs on the website.

Feedback and Improvements:
Contributions are welcome! Feel free to open issues or submit pull requests if you have suggestions or improvements.

License

This project is open-source and available under the MIT License. Please refer to the LICENSE file for more details.
