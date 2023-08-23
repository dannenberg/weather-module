import requests
api_key = "ac15a5aa6c4d4516afb172640232308"
weather_api_url = "http://api.weatherapi.com/v1/current.json"
req = {"key": api_key, "q": 11106}
response = requests.get(''.join([weather_api_url, "?key=", api_key, "&q=", "11106"]))

print(response)
print(response.json())
