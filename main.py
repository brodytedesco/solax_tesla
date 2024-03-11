from twilio.rest import Client
import sys
import time
import json
sys.path.append("tesla-stats")
import get_tesla_info
sys.path.append("../")
sys.path.append("solar-stats")
import get_solar_stats

# Amount of minutes before we do the validation against Tesla status
duration_minutes = 5
duration_seconds = duration_minutes * 60

# Your Twilio credentials
with open('creds.json', 'r') as file:
    data = json.load(file)
        
twilio_account_sid = data["twilio_account_sid"]
twilio_auth_token = data["twilio_auth_token"]
twilio_phone_number = data["twilio_phone_number"]
recipient_phone_number = data["recipient_phone_number"]  # Recipient's phone number


# Initialize Twilio client
client = Client(twilio_account_sid, twilio_auth_token)



#calculating average value of array 
def calculate_average(arr):
    # Check if the array is empty
    if not arr:
        return 0  # Return 0 if the array is empty to avoid division by zero
    
    # Calculate the sum of all elements in the array
    array_sum = sum(arr)
    
    # Calculate the average
    average = array_sum / len(arr)
    
    return average




def __main__():
    array_of_feed_in = []
    start_time = time.time()
    charging_startedby_script = False
    
    while True:
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        grid = get_solar_stats.get_solar_grid()
        print("Feed in (W): "+str(grid))
        array_of_feed_in.append(grid)
        time.sleep(5)


        
        if elapsed_time >= duration_seconds:
            
            start_time = time.time()
            
            # Averaging the feed in
            average_feedin=calculate_average(array_of_feed_in)
            print("Average Feed-In: "+str(average_feedin))
            array_of_feed_in = []
            
            # Getting + Printing Tesla charge/state, if this fails script will exit
            charge,charge_state = get_tesla_info.get_tesla_info()
            print("Tesla Charge and State: "+ str(charge),charge_state)
            
            
            # Logic for what to do depending on charge, charge state and average feed in
            if charge == 100:
                print("Fully Charged")
            elif charge_state == "Disconnected":
                print("Tesla is Disconnected from a Charger")
            elif charging_startedby_script==False and charge_state=="Charging":
                print("Charging was started by user, therefore this script will not interrupt")
            elif charging_startedby_script==True and charge_state=="Charging":
                if average_feedin < -1000:
                    print("stop charging")
                    message = client.messages.create(
                    body='stop',
                    from_=twilio_phone_number,
                    to=recipient_phone_number
                    )
                    print(message.sid)
            elif charging_startedby_script==False and charge_state=="Stopped":
                if average_feedin > 4000:
                    print("start charging")
                    message = client.messages.create(
                    body='start',
                    from_=twilio_phone_number,
                    to=recipient_phone_number
                    )
                    print(message.sid)
                    charging_startedby_script==True
                else:
                    print("will not charge due to average feed in being at:"+str(average_feedin))
                    

__main__()