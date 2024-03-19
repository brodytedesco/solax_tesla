from twilio.rest import Client
import sys
import time
import json
from datetime import datetime
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
    
            
def get_grid():
    now = datetime.now()
    pretty_time = now.strftime("[%d-%m-%Y, %H:%M:%S]")
    grid = get_solar_stats.get_solar_grid()
    print(str(pretty_time)+": "+"Feed in (W): "+str(grid))
    return grid
    


def __main__():
    array_of_feed_in = []
    start_time = time.time()
    charging_startedby_script = False
    current_watts_consumed_from_charging=0
    amps_for_app=0
    watts_count = 0
    while True:
        
        # Variable setting
        current_time = time.time()
        elapsed_time = current_time - start_time
        watts_count += 1

        # Get grid + print values
        grid = get_grid()
        
        # The trigger to swap the charging can take 30 seconds so we accomidate by this, by not counting the readings until a set amount of cycles
        if watts_count > 4:
            array_of_feed_in.append(grid)
            
        # Wait 5 seconds before looping again, no need for lots of data
        time.sleep(5)


        # Enter the "Decision Tree Logic"
        if elapsed_time >= duration_seconds:
            print("--------------------------------------------------------------------------------------------------------------------------------------")
            watts_count = 0
            start_time = time.time()
            
            # Averaging the feed in
            average_feedin=calculate_average(array_of_feed_in)
            print("Average Feed-In: "+str(average_feedin))
            array_of_feed_in = []
            adjusted_feedin=round(average_feedin+current_watts_consumed_from_charging,2)
            print("Feed in adjusted for the amount of Watts Tesla charging is consuming: "+str(adjusted_feedin))
            
            # Getting + Printing Tesla charge/state, if this fails script will exit
            charge,charge_state = get_tesla_info.get_tesla_info()
            print("Tesla Charge and State: "+ str(charge),charge_state)
            
            
            # --------------------------------------------------------------------------------
            #                               DECISION TREE
            # --------------------------------------------------------------------------------
            # Logic for what to do depending on charge, charge state and average feed in
            
            
            # If Tesla is fully charged we move on
            if charge == 100:
                print("Fully Charged")
                current_watts_consumed_from_charging=0
                charging_startedby_script=False
            
            # If Tesla is disconnected we don't care 
            elif charge_state == "Disconnected":
                print("Tesla is Disconnected from a Charger")
                current_watts_consumed_from_charging=0
                charging_startedby_script=False
                
            # If the user started charging, we won't interrupt
            elif charging_startedby_script==False and charge_state=="Charging":
                print("Charging was started by user, therefore this script will not interrupt")
                current_watts_consumed_from_charging=0
                
            # If we started charging, but now the "adjusted feed in" is less then the minimum needed power to charge, we stop charging
            elif charging_startedby_script==True and charge_state=="Charging" and adjusted_feedin < watt_steps[0]+buffer_watts:
  
                print("stop charging")
                message = client.messages.create(
                body='stop',
                from_=twilio_phone_number,
                to=recipient_phone_number
                )
                print(message.sid)
                current_watts_consumed_from_charging=0
                charging_startedby_script=False

            # Logically if we don't meet any other condition we should be ready to calculate our charge
            else:
                
                # Do we have enough solar power to charge or not?
                if (adjusted_feedin > watt_steps[0]+buffer_watts):
                    print("Start charging calculations")
                    previous_amps=amps_for_app
                    amps_for_app,current_watts_consumed_from_charging = current_calculate(adjusted_feedin)
                    
                    # We have enough power and have calculated the Amps to charge at, sending a text to start this
                    if(previous_amps!=amps_for_app):
                        print("Charging set at: "+str(amps_for_app)+ "Amps, "+str(current_watts_consumed_from_charging)+"Watts")
                        message = client.messages.create(
                        body='start charging at: '+str(amps_for_app),
                        from_=twilio_phone_number,
                        to=recipient_phone_number
                        )
                        print(message.sid)
                    else:
                        print("Resuming Charging at: " + str(amps_for_app))
                    charging_startedby_script=True
                
                # We dont have enough power
                else:
                    print("will not charge due to average feed in being at:"+str(average_feedin))
                    current_watts_consumed_from_charging=0
                    charging_startedby_script=False
            
            #Debugging mostly
            print("Script States: charging_startedby_script: "+str(charging_startedby_script)+", amps_for_app: "+str(amps_for_app)+", current_watts_consumed_from_charging: "+str(current_watts_consumed_from_charging))
            print("--------------------------------------------------------------------------------------------------------------------------------------")
__main__()