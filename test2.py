import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

# Function to convert string in number if possible
def convert_to_number(value):
    try:
        if value.strip() == "":
            return ""
        if '.' in value:  
            return float(value)
        else:
            return int(value)  
    except ValueError:
        return value  

# Function to load crop names and checkbox IDs from the file
def load_crop_data(filename):
    crop_data = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()  
                if line:  
                    parts = line.split(", ")
                    crop_name = parts[0].split(": ")[1]
                    crop_id = parts[1].split(": ")[1]
                    crop_data[crop_name] = crop_id
        return crop_data
    except Exception as e:
        print(f"Error loading crop data: {e}")
        return {}

# Function to extract and save crop IDs to a new file (crop_ids.txt)
def extract_and_save_crop_ids(input_filename, output_filename):
    crop_ids = set()
    try:
        with open(output_filename, 'r') as file:
            for line in file:
                crop_ids.add(line.strip())  
    except FileNotFoundError:
        pass

    try:
        with open(input_filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(", ")
                    if len(parts) == 2:
                        crop_id = parts[1].split(": ")[1]
                        crop_ids.add(crop_id)
    except Exception as e:
        print(f"Error reading crop_dict.txt: {e}")

    try:
        with open(output_filename, 'w') as file:
            for crop_id in crop_ids:
                file.write(crop_id + "\n")
        print(f"Updated crop IDs saved to {output_filename}")
    except Exception as e:
        print(f"Error saving crop IDs to {output_filename}: {e}")

# Function to get the last 60 days
def get_previous_60_days():
    today = datetime.now()
    days = []
    for i in range(60):
        day = today - timedelta(days=i)
        days.append(day.day)  # Save only the day part (1 to 31)
    return days

# Path to ChromeDriver
driver_path = r"D:\chromedriver-win64\chromedriver-win64\chromedriver.exe" 

# Set Chrome options
options = Options()

# Set up the service object with ChromeDriver path
service = Service(driver_path)

# Initialize WebDriver with the Service object
driver = webdriver.Chrome(service=service, options=options)

# Load crop data from the file (crop_dict.txt)
crop_data = load_crop_data('crop_dict.txt')  # Ensure this file contains your crop data

# Get the previous 60 days
previous_60_days = get_previous_60_days()

# Iterate over the previous 60 days
for day in previous_60_days:
    try:
        # Open the government website
        url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityWiseDailyReport.aspx"
        driver.get(url)

        # Click the link with the specific day
        elem = driver.find_element(By.LINK_TEXT, str(day))
        elem.click()

        # Wait for the "Submit" link to be present
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cphBody_Submit_list"))
        )
        element.click()

        # Example: Iterate through each crop's checkbox ID and select the checkbox
        for crop_name, crop_id in crop_data.items():
            print(f"Attempting to select checkbox for crop: {crop_name}, ID: {crop_id}")
            try:
                crop_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, crop_id))
                )
                if not crop_checkbox.is_selected():  
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

        # Assuming the first row contains the column headers
        headers = [header.text for header in table_rows[0].find_elements(By.XPATH, ".//th")]

        # Loop through the rows and create a dictionary for each row
        for row in table_rows[1:]:  # Skip the header row
            row_data = [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
            if row_data:  
                row_dict = {}
                for i, header in enumerate(headers):
                    if i < len(row_data):
                        row_dict[header] = convert_to_number(row_data[i])
                    else:
                        row_dict[header] = ""  

                # Add the date to each record
                row_dict["Date"] = day
                data.append(row_dict)

        # Save the data to a JSON file
        with open(f"crop_data_{day}.json", "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)

        print(f"Data for {day} has been saved to 'crop_data_{day}.json'.")

    except Exception as e:
        print(f"Error during interaction with the page for day {day}: {e}")

    # Optional: Wait to avoid being detected as a bot
    time.sleep(5)

# Now fetch today's data
current_day = datetime.now().day

# Fetch today's data the same way as before
try:
    # Open the government website
    url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityWiseDailyReport.aspx"
    driver.get(url)

    # Click the link with the current day
    elem = driver.find_element(By.LINK_TEXT, str(current_day))
    elem.click()

    # Wait for the "Submit" link to be present
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cphBody_Submit_list"))
    )
    element.click()

    # Iterate through each crop's checkbox ID and select the checkbox
    for crop_name, crop_id in crop_data.items():
        print(f"Attempting to select checkbox for crop: {crop_name}, ID: {crop_id}")
        try:
            crop_checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, crop_id))
            )
            if not crop_checkbox.is_selected():  
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

    # Assuming the first row contains the column headers
    headers = [header.text for header in table_rows[0].find_elements(By.XPATH, ".//th")]

    # Loop through the rows and create a dictionary for each row
    for row in table_rows[1:]:
        row_data = [cell.text for cell in row.find_elements(By.XPATH, ".//td")]
        if row_data:
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row_data):
                    row_dict[header] = convert_to_number(row_data[i])
                else:
                    row_dict[header] = ""

            row_dict["Date"] = current_day
            data.append(row_dict)

    # Save today's data to a JSON file
    with open(f"crop_data_{current_day}.json", "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

    print(f"Today's data has been saved to 'crop_data_{current_day}.json'.")

except Exception as e:
    print(f"Error during interaction with the page for today's data: {e}")

finally:
    # Quit the driver
    driver.quit()

# Wait for user to close the browser manually
input("Press Enter to exit...")