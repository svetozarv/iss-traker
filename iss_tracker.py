import requests 
import requests.exceptions
import time
import datetime
import smtplib
from zoneinfo import ZoneInfo

from _secrets import EMAIL_FROM, EMAIL_TO, PASSWORD

MY_LAT = 52.209942   # latitude and longitude of Warszawa, Mokotów
MY_LNG = 21.020531
iss_coords_relative = None


def write_email():
    message = f"Subject:International space station\n\n \
                        Hello, currently the IIS is passing near you in 5x5 sector, take a moment ot find it! \
                        The ISS coords relative to you is: {iss_coords_relative}"

    connection = smtplib.SMTP(host="smtp.gmail.com")
    connection.starttls()
    connection.login(user=EMAIL_FROM, password=PASSWORD)
    connection.sendmail(from_addr=EMAIL_FROM, to_addrs=EMAIL_TO, msg=message)
    print("Email sent.")
    connection.close()


# get coords of the ISS
def iss_nearby() -> bool:
    response = requests.get("http://api.open-notify.org/iss-now.json")
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("HTTPError. Skipping...")
        return False
    iss_pos = response.json()["iss_position"]
    iss_lat = float(iss_pos["latitude"])
    iss_lng = float(iss_pos["longitude"])
    print(f"ISS coords: {iss_lat}, {iss_lng}")
    global iss_coords_relative
    iss_coords_relative = (MY_LAT - iss_lat, MY_LNG - iss_lng)
    if (iss_lat - 5 <= MY_LAT <= iss_lat + 5) and (iss_lng - 5 <= MY_LNG <= iss_lng + 5):
        return True
    return False


# get sunrise & sunset time
def sun_is_down() -> bool:
    # get current hour 
    curr = datetime.datetime.now(tz=ZoneInfo("Europe/Warsaw"))
    print(f"\nCurrent time: {curr.hour}:{curr.minute}")

    parameters = {
        "lat": MY_LAT,
        "lng": MY_LNG,
        "formatted": 0,
        "tzid": "Europe/Warsaw",
    }
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("HTTPError. Skipping...")
        return False
    data = response.json()
    sunrise_hour = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset_hour = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    print(f"Sunrise hour: {sunrise_hour}")
    print(f"Sunset hour: {sunset_hour}")
    if curr.hour > sunset_hour or curr.hour < sunrise_hour:
        return True
    return False


while True:
    if sun_is_down() and iss_nearby():
        write_email()
    time.sleep(60*30)
