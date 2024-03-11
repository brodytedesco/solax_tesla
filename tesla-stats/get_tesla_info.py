import requests
import time
import json

def get_tesla_info():
    with open('creds.json', 'r') as file:
        data = json.load(file)
    
    # Access the variables
    refresh_token = data['tesla_refresh']
    vehicle_id = data['tesla_vehicleid']

    status_url = f"https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/vehicle_data"
    wake_url = f"https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/wake_up"
    # start_charge_url = f"https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/command/charge_start"
    # stop_charge_url = f"https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/command/charge_stop"



    #Refreshing our Auth Token

    # Define headers
    headers = {
        "Content-Type": "application/json"
    }

    url = "https://auth.tesla.com/oauth2/v3/token"
    # Define request body
    data = {
        "grant_type": "refresh_token",
        "client_id": "ownerapi",
        "refresh_token": refresh_token,
        "scope": "openid email offline_access"
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=data)

    # Check if request was successful
    if response.status_code == 200:
        # Extract new access token from response
        access_token = response.json()["access_token"]
        # print("New Access Token:", access_token)
        # print(response.text)
    else:
        print("Failed to refresh access token. Status code:", response.status_code)
   
        
    time.sleep(1)

    # Define headers with the access token obtained previously
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Send GET request
    response = requests.get(status_url, headers=headers)

    # print(response.status_code)
    # print(response.text)

    # Check if request was successful
    if response.status_code == 200:
        vehicle_data = response.json()


    elif (response.status_code == 408):
        response = requests.post(wake_url, headers=headers)
        if response.status_code == 200:
            print("Waking up")
            #Give Tesla time to "Wake up"
            time.sleep(30)
            print(response.text)
            
            response = requests.get(status_url, headers=headers)
            
            #Encountered the Tesla not waking up after hitting the url
            if response.status_code == 200:
                pass
            else:
                print("Tesla not responive" + response.status_code)
                print(response.text)
                exit()

        else:
            print("Tesla not responive:", response.status_code)
            print(response.text)
            exit()
           
    else:
        print("Failed to retrieve vehicle data. Status code:", response.status_code)
        print(response.text)
        exit()
        
    response_json = response.json()
    # Obtaining Battery Level and State
    data_reponse=response_json["response"]
    charge_states=data_reponse["charge_state"]
    battery=charge_states["battery_level"]
    state=charge_states["charging_state"]
    
    return [battery, state]