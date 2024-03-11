import requests
import x3_mic_pro_g2
import json

url = 'http://192.168.0.154'
data = {'optType': 'ReadRealTimeData', 'pwd': 'SR9CLDMPYP'}

def get_solar_grid():
    with open('creds.json', 'r') as file:
        data = json.load(file)
        
    url = data['solax_url']
    data = {'optType': 'ReadRealTimeData', 'pwd': data['solax_pwd']}
    
    response = requests.post(url, data=data)

    if response.status_code == 200:
        response_json = response.json()
        version = response_json.get('ver')
        # print("Version:", version)
        # print("Data",response_json.get('Data'))
    else:
        print("Error:", response.status_code)

    Data = (x3_mic_pro_g2.X3MicProG2.response_decoder(response_json.get('Data')))
    # print(Data)
    feedin = (Data["Feed-in Power (W)"])
    # print(len(response_json.get('Data')))
    return feedin
