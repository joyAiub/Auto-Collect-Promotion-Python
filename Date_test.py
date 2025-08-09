import datetime
import time
import pytz

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