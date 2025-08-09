import datetime
import time
import pytz
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from API_Request_Acess_Token import get_access_token  # This imports from API_Request_Acess_Token.py

#current_date = datetime.datetime.now().strftime("%d-%b-%Y")
# Set the time zone to Vancouver (PST)
vancouver_tz = pytz.timezone('America/Vancouver')
# Get the current time in Vancouver
current_time = datetime.datetime.now(tz=vancouver_tz)
# Format the date as "yyyy/MM/dd"
current_date = current_time.strftime('%Y/%m/%d')
# Format the time as "3:17 AM"
time_str = current_time.strftime('%#I:%M %p')

# Convert the current date to milliseconds
current_date_millisecond = int(current_time.timestamp() * 1000)

# Print the Vancouver date and time along with the current date in milliseconds
print("Vancouver Date (PST):", current_date)
print("Vancouver Time (PST):", time_str)
print("Current Date (PST) in Milliseconds:", current_date_millisecond)

#-------------------UberEats Search-------------------------
chrome_driver_path = 'E:/chromedriver/Chrome 113/chromedriver_win32/chromedriver.exe'

print("Starting Category extraction...")

def fetch_data():
    # Make the API call to get the access token
    response = get_access_token()
    access_token = response['tenant_access_token']
    print(access_token)

    url = 'https://open.larksuite.com/open-apis/bitable/v1/apps/basuspDo7viuUtnUvnrylTaC2hf/tables/tbljuYpPRrZd7SGO/records'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'view_id': 'vewj3fVbWL', 'field_names': '["Task name(VR name)","Ubereats Live Link","Doordash Live Link","Client restaurant name"]'}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()['data']
        items = data['items']

        # Initialize the browser outside the loop
        options = Options()
        # options.add_argument('--headless')
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        # Maximize the browser window
        driver.maximize_window()
        counter = 1
        for item in items:
            fields = item['fields']
            client_Restaurent_Name = fields['Client restaurant name'][0]['text']
            if client_Restaurent_Name == "" or client_Restaurent_Name.isspace() or client_Restaurent_Name is None or "\n" in client_Restaurent_Name:
                client_Restaurent_Name = fields['Client restaurant name'][1]['text']
            #VR_name = fields['Task name(VR name)'][0]['text']
            VR_name = fields['Task name(VR name)'][0]['text']
            if VR_name == "" or VR_name.isspace() or VR_name is None or "\n" in VR_name:
                VR_name = fields['Task name(VR name)'][1]['text']
            doordash_link = fields.get('Doordash Live Link')
            ubereats_link = fields.get('Ubereats Live Link')
            print(counter)
            counter = counter + 1
            print('VR Name:', VR_name)
            print('Client Resaurent Name:', client_Restaurent_Name)
            if doordash_link:
                print('Doordash Link:', doordash_link.strip())
            else:
                print('Doordash Link: No data found')
            if ubereats_link:
                print('Ubereats Link:', ubereats_link.strip())

                try:
                    # Navigate to the new UberEats URL within the existing browser
                    time.sleep(1.5)
                    driver.get(ubereats_link)
                    #Check Exception Dialog BOX
                    '''if len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, f'/html/body/div/div/div/div/div/div/div[2]')))) > 0:
                        print("Enter Delivery Address Pop Up, ")
                        Dialog1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div/div/div/div/div/div/div/div/button')))
                        Dialog1.click()
                    time.sleep(1)
                    if len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, f'/html/body/div[1]/div[2]/div/div/div[2]/div/div/div[@aria-label="dialog"]')))) > 0:
                        print("Select Schedule pop up ")
                        Dialog2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div/div/div/div/div/div/div/div/div/div/div/div/div/button')))
                        Dialog2.click()'''

                    # Send an Escape key press
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.ESCAPE)
                    # Execute JavaScript to click on a blank space
                    driver.execute_script("document.body.click();")
                    Element_Xpath = f'/html/body/div/div/div/main/div/div/div/div/div/div/div/nav/div[1]/button/div' #Check Promo / Picked for You
                    # Wait for the page to load completely
                    time.sleep(2)
                    if len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, Element_Xpath)))) > 0:
                        Promotion_Element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, Element_Xpath)))
                        Promotion_Data = Promotion_Element.text
                        print(Promotion_Data)
                        if Promotion_Data == 'Picked for you' or Promotion_Data == 'Popular Picks':
                            Promotion_Data = 'No promotion available'

                            time.sleep(1.5)
                            # Create Record in Lark
                            url1 = "https://open.larksuite.com/open-apis/bitable/v1/apps/LFgnb5CgMa45i6sYecguIw43sWf/tables/tblULfltBykVRAYY/records/batch_create"
                            headers = {'Authorization': f'Bearer {access_token}','Content-Type': 'application/json'}
                            body = {"records": [{"fields": {"Promotion Date": f"{current_date}", "Platform": "Uber","VR Name": f"{VR_name}","Restaurant": f"{client_Restaurent_Name}","Current Promo Type": f"{Promotion_Data}","Uber Eats Restaurant URL":f"{ubereats_link.strip()}"}}]}
                            response = requests.post(url1, headers=headers, json=body)
                            time.sleep(1)
                            if response.status_code == 200:
                                print("API request successful!")
                            else:
                                print(f"API request failed with status code {response.status_code}.")
                            print(Promotion_Data)
                        else:
                            Promo_XPath = f'/html/body/div/div/div/main/div/div/div/ul/li[1]/h3'
                            if len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, Promo_XPath)))) > 0:
                                Image_Element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, Element_Xpath)))
                                Image_Data = Image_Element.text
                                print(Image_Data)
                                if Promotion_Data == Image_Data:
                                    '''print('Matched')
                                    Dish_Name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f'/html/body/div/div/div/main/div/div/div/ul/li[1]/ul/li/div/div/div[2]/div[1]')))
                                    Dish_Name_Store = Dish_Name.text
                                    print(Dish_Name_Store)
                                    Dish_Price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,f'/html/body/div/div/div/main/div/div/div/ul/li[1]/ul/li/div/div/div[2]/div[2]')))
                                    Dish_Price_Store = Dish_Price.text
                                    print(Dish_Price_Store)
                                    time.sleep(1.5)'''
                                    print('Matched')
                                    Dish_Name_Elements = WebDriverWait(driver, 10).until(
                                        EC.presence_of_all_elements_located((By.XPATH,'/html/body/div/div/div/main/div/div/div/ul/li[1]/ul/li/div/div/div[2]')))
                                    dish_names = []
                                    dish_prices = []
                                    for Dish_Name_Element in Dish_Name_Elements:
                                        dish_text = Dish_Name_Element.text
                                        dish_data = dish_text.split('\n')
                                        dish_name = dish_data[0]
                                        #dish_price = dish_data[1]
                                        dish_price = dish_data[1].replace('CA', '')
                                        dish_names.append(f'[{dish_name}]')
                                        dish_prices.append(f'[{dish_price}]')
                                    dish_names_str = ', '.join(dish_names)
                                    dish_prices_str = ', '.join(dish_prices)
                                    print("Dish Name: " + dish_names_str)
                                    print("Dish Price: " + dish_prices_str)
                                    # Create Record in Lark
                                    url1 = "https://open.larksuite.com/open-apis/bitable/v1/apps/LFgnb5CgMa45i6sYecguIw43sWf/tables/tblULfltBykVRAYY/records/batch_create"
                                    headers = {'Authorization': f'Bearer {access_token}','Content-Type': 'application/json'}
                                    body = {"records": [{"fields": {"Promotion Date": current_date_millisecond,"Platform": "Uber", "VR Name": f"{VR_name}","Restaurant": f"{client_Restaurent_Name}","Current Promo Type": f"{Promotion_Data}","Discounted Item": f"{dish_names_str}","Price": f"{dish_prices_str}","Uber Eats Restaurant URL":f"{ubereats_link.strip()}"}}]}

                                    response = requests.post(url1, headers=headers, json=body)
                                    time.sleep(1)

                                    if response.status_code == 200:
                                        print("API request successful!")
                                    else:
                                        print(f"API request failed with status code {response.status_code}.")


                except:
                    if len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, f'/html/body/div/div/div/main/div/div[1]')))) > 0:
                        Eroor_dt = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div/div/div/main/div/div[1]')))
                        print(Eroor_dt.text)
            else:
                print('Ubereats Link: No data found')
            print('---')

        # Quit the browser after iterating over all items
        driver.quit()

    else:
        print('Error:', response.status_code)

fetch_data()
