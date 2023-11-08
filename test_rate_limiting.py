import requests

def callAPI():
    response = requests.get(url="http://127.0.0.1:8000/")
    return response.text

# Note that the "/" endPoint have 5 api calls/minutes rate limit
# Hence the 6th api call in a minute should give rate limit exceeded error.

for x in range(6):
    print("API Call Number: " + str(x+1))
    print(callAPI() + '\n')