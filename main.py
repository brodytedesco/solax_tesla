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

# Charging Variables
buffer_watts=200
voltage=230
current_steps=[8,16,24,32]
watt_steps=[]
for current in current_steps:
    watt_steps.append(voltage*current)


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

#calculating what amount of amps to turn the charging on, therefore dictating rate of charge
def current_calculate(feed_in):
    target_watts = 0
    target_amps = 0
    for watts in watt_steps:
        if watts<feed_in-buffer_watts:
            target_watts=watts
    target_amps = round(target_watts/voltage,0)
    return [target_amps, target_watts]
    
            
    


def __main__():
    array_of_feed_in = []
    start_time = time.time()
    charging_startedby_script = False
    current_watts_consumed_from_charging=0
    
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
            adjusted_feedin=average_feedin+current_watts_consumed_from_charging
            print("Feed in adjusted for the amount of Watts Tesla charging is consuming: "+str(adjusted_feedin))
            
            # Getting + Printing Tesla charge/state, if this fails script will exit
            charge,charge_state = get_tesla_info.get_tesla_info()
            print("Tesla Charge and State: "+ str(charge),charge_state)
            
            
            # Logic for what to do depending on charge, charge state and average feed in
            if charge == 100:
                print("Fully Charged")
                current_watts_consumed_from_charging=0
            elif charge_state == "Disconnected":
                print("Tesla is Disconnected from a Charger")
                current_watts_consumed_from_charging=0
            elif charging_startedby_script==False and charge_state=="Charging":
                print("Charging was started by user, therefore this script will not interrupt")
                current_watts_consumed_from_charging=0
            elif charging_startedby_script==True and charge_state=="Charging":
                if adjusted_feedin < watt_steps[0]+buffer_watts:
                    if average_feedin < -1000:
                        print("stop charging")
                        message = client.messages.create(
                        body='stop',
                        from_=twilio_phone_number,
                        to=recipient_phone_number
                        )
                        print(message.sid)
                        current_watts_consumed_from_charging=0
            else:
                #if we meet minimum charge constraints
                if (adjusted_feedin > watt_steps[0]+buffer_watts):
                    print("Start charging calculations")
                    amps_for_app,current_watts_consumed_from_charging = current_calculate(adjusted_feedin)
                    print("Charging set at: "+str(amps_for_app)+ "Amps, "+str(current_watts_consumed_from_charging)+"Watts")
                    
                    message = client.messages.create(
                    body='start charging at: '+str(amps_for_app),
                    from_=twilio_phone_number,
                    to=recipient_phone_number
                    )
                    print(message.sid)
                    charging_startedby_script=True
                else:
                    print("will not charge due to average feed in being at:"+str(average_feedin))
                    current_watts_consumed_from_charging=0
                    

__main__()