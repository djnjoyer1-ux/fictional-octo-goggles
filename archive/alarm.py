import time
import threading
from datetime import datetime, timedelta
from playsound import playsound

# Define the schedule as a list of tuples with time and task
schedule = [
    ("14:50", "Review Introductions to DEs"),
    ("15:30", "First-Order DEs (1.1 - 1.3)"),
    ("16:00", "First-Order DEs (Cont'd)"),
    ("16:40", "Integrating Factor Method (2.2)"),
    ("17:00", "Existence and Uniqueness, Variation of Parameters (2.2 - 2.3)"),
    ("17:40", "Existence and Uniqueness (Cont'd)"),
    ("18:20", "Separable DEs (2.4)"),
    ("18:50", "Exact DEs (2.5)"),
    ("19:20", "Higher-Order DEs, nth-Order Homogeneous DEs (3.1 - 3.3)"),
    ("19:50", "Quick Review")
]

def alarm_at_time(time_str, task):
    # Get today's date
    now = datetime.now()
    
    # Convert time_str to a datetime object using today's date
    alarm_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    
    # If the alarm time has already passed today, set it for tomorrow
    if alarm_time < now:
        alarm_time += timedelta(days=1)

    # Calculate the delay time in seconds
    delay = (alarm_time - now).total_seconds()

    # Debug print to check the delay value
    print(f"Current Time: {now}, Alarm Time: {alarm_time}, Delay: {delay} seconds")

    # If delay is negative (somehow), reset for the next day
    if delay < 0:
        delay += 24 * 60 * 60  # Add 24 hours in seconds

    # Wait until it's time for the alarm
    time.sleep(delay)

    # Play the sound
    playsound('alarm_sound.mp3')

    # Print the alarm message with the task
    print(f"ALARM: It's {time_str}, time to study: {task}")

def start_alarms():
    # Start alarms for each scheduled task
    for time_str, task in schedule:
        threading.Thread(target=alarm_at_time, args=(time_str, task)).start()

if __name__ == "__main__":
    start_alarms()
