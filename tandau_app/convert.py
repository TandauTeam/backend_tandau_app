import xml.etree.ElementTree as ET
import json
import requests

# Send GET request to the URL
url = "https://edu-test-iam-service.azurewebsites.net/api/auth/location/"
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the XML response
    root = ET.fromstring(response.content)

    # Initialize list to store converted data
    converted_data = []

    # Iterate over each 'data' element in the XML
    for data_element in root.findall('.//data'):
        # Initialize dictionary for each 'data' element
        data_dict = {}
        # Extract required fields and add to dictionary
        data_dict['id'] = data_element.find('id').text
        data_dict['title_ru'] = data_element.find('title_ru').text
        data_dict['title_kz'] = data_element.find('title_kz').text
        data_dict['is_city'] = data_element.find('is_city').text
        # Append dictionary to list
        converted_data.append(data_dict)

    # Convert list of dictionaries to JSON
    json_data = json.dumps(converted_data, indent=2, ensure_ascii=False)
    
    # Print or return the JSON data
    print(json_data)

else:
    print("Failed to retrieve data from the URL")
