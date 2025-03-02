import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

# Function to conver string in number if possible
def convert_to_number(value):
    try:
        #if value is empty then return empty
        if value.strip() == "":
            return "" 
        # If decimal point present will convert it into float
        if '.' in value:  
            return float(value)
        else:
            return int(value)  #if not then convert to integer 
    except ValueError:
        return value  #If the string cannot be converted tto integer then return that string 

# Function to load crop names and checkbox IDs from the file
def load_crop_data(filename):
    crop_data = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if line:  # Skip empty lines
                    # Split the line into 'Name' and 'ID' parts
                    parts = line.split(", ")
                    crop_name = parts[0].split(": ")[1]  # Get the crop name
                    crop_id = parts[1].split(": ")[1]  # Get the checkbox ID
                    crop_data[crop_name] = crop_id
        return crop_data
    except Exception as e:
        print(f"Error loading crop data: {e}")
        return {}

# Function to extract and save crop IDs to a new file (crop_ids.txt)
def extract_and_save_crop_ids(input_filename, output_filename):
    crop_ids = set()  # Use a set to ensure uniqueness

    # Load existing crop IDs from output file (if any)
    try:
        with open(output_filename, 'r') as file:
            for line in file:
                crop_ids.add(line.strip())  # Add existing IDs to the set
    except FileNotFoundError:
        # If the output file doesn't exist, we will create it
        pass

    # Extract crop IDs from the input file (crop_dict.txt)
    try:
        with open(input_filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    # Split the line into 'Name' and 'ID' parts
                    parts = line.split(", ")
                    if len(parts) == 2:
                        crop_id = parts[1].split(": ")[1]  # Get the crop ID
                        crop_ids.add(crop_id)  # Add to the set of IDs
    except Exception as e:
        print(f"Error reading crop_dict.txt: {e}")

    # Save the unique crop IDs back to the output file
    try:
        with open(output_filename, 'w') as file:
            for crop_id in crop_ids:
                file.write(crop_id + "\n")  # Write each ID on a new line
        print(f"Updated crop IDs saved to {output_filename}")
    except Exception as e:
        print(f"Error saving crop IDs to {output_filename}: {e}")

# Get the current date
current_date = datetime.now()

# Save the day (only the day number) in a variable
current_day = current_date.day

# Path to ChromeDriver
driver_path = r"D:\chromedriver-win64\chromedriver-win64\chromedriver.exe" 

# Set Chrome options
options = Options()

# Set up the service object with ChromeDriver path
service = Service(driver_path)

# Initialize WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=options)

# Open the government website
url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityWiseDailyReport.aspx"
driver.get(url)

# Click the link with Current Day
elem = driver.find_element(By.LINK_TEXT, str(current_day))
elem.click()

# Wait for the "Submit" link to be present
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphBody_Submit_list"))
    )
    element.click()

    # Load crop names and IDs from the file (crop_dict.txt)
    crop_data = load_crop_data('crop_dict.txt')  # Ensure this file contains your crop data

    # Example: Iterate through each crop's checkbox ID and select the checkbox
    for crop_name, crop_id in crop_data.items():
        print(f"Attempting to select checkbox for crop: {crop_name}, ID: {crop_id}")
        try:
            # Wait for the checkbox element to be clickable
            crop_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, crop_id))
            )
            if not crop_checkbox.is_selected():  # Ensure the checkbox is not already selected
                crop_checkbox.click()
                print(f"Successfully selected checkbox for {crop_name}.")
            else:
                print(f"Checkbox for {crop_name} was already selected.")
        except Exception as e:
            print(f"Could not select checkbox for {crop_name}: {e}")

    # Wait for the "Submit" button and click it
    submit_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphBody_btnSubmit"))
    )
    submit_button.click()

    # Wait for the table with <tr> elements to be fully loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphBody_GridView1"))
    )

    # Find all the <tr> elements within the table
    table_rows = driver.find_elements(By.XPATH, "//table[@id='cphBody_GridView1']//tr")

    # List to store the data in dictionary format
    data = []

    # Assuming the first row contains the column headers (adjust if necessary)
    headers = [header.text for header in table_rows[0].find_elements(By.XPATH, ".//th")]

    # Loop through the rows and create a dictionary for each row
    for row in table_rows[1:]:  # Skip the header row
        row_data = [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
        if row_data:  # Skip empty rows
            row_dict = {}

            # Handle missing data and ensure all keys are added
            for i, header in enumerate(headers):
                if i < len(row_data):
                    # Try to convert the data to a number if possible
                    row_dict[header] = convert_to_number(row_data[i])
                else:
                    row_dict[header] = ""  # Add empty values for missing columns

            # Add the dictionary to the data list
            data.append(row_dict)

    # Save the data to a JSON file
    with open(f"crop_data_{current_day}.json", "w", encoding="utf-8") as jsonfile:
        # Use json.dump to write data as JSON
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

    print(f"Data for {current_day} has been saved to 'crop_data_{current_day}.json'.")

except Exception as e:
    print(f"Error during interaction with the page: {e}")

finally:
    time.sleep(20)
    # Make sure to quit the driver properly
    driver.quit()

# Wait for user to close the browser manually
input("Press Enter to exit...")
