import requests
from dotenv import load_dotenv
import os
load_dotenv()

def get_first_experince_with_brapi():

    url = "https://brapi.dev/api/v2/crypto"
    url_btc = f"https://brapi.dev/api/v2/crypto/available?search=BT&token={os.getenv('BRAPI_API_KEY')}"

    print(url_btc)
    params = {
        'coin': 'BTC,ETC',
        'currency': 'BRL',
        'range': '5d',
        'interval': '1d',
        'token': os.getenv('BRAPI_API_KEY'), 
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return print(data)
    else:
        return print(f"Request failed with status code {response.status_code}")

def get_brapi_analysis():
    tickers = ["PETR4", "VALE3.SA", "ITUB4.SA", "AMER3.SA", "B3SA3.SA", "MGLU3.SA", "LREN3.SA", "ITSA4.SA", "BBAS3.SA", "RENT3.SA", "ABEV3.SA"]
    token = os.getenv('BRAPI_API_KEY')
    if not token:
        print("Error: BRAPI_API_KEY is not set in the environment variables.")
        return

    for ticker in tickers:
        url = f"https://brapi.dev/api/quote/{ticker}?token={token}"
        try:
            response = requests.get(url)
            print(f"Requesting URL: {url}")
            print(f"Response Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(f"Request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # get_first_experince_with_brapi()
    get_brapi_analysis()


