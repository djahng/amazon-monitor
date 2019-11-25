# Imports
import os

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client


def get_price(url):
    # Set User-Agent header so Amazon returns the actual page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    # Get the page
    response = requests.get(url, headers=headers)

    # Load into BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    # A trick since Amazon's page is javascript heavy
    soup = BeautifulSoup(soup.prettify(), 'html.parser')

    # Get the price
    price = soup.find(id='priceblock_ourprice').get_text()

    # Strip off the '$' and parse as a float
    price = float(price[1:])

    return price

def send_sms(price, title):
    # Get the account_sid and auth_token from environment variables
    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')

    # Get the to and from phone numbers
    to_phone = os.getenv('TO_PHONE')
    from_phone = os.getenv('FROM_PHONE')

    # Send the text
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=to_phone,
        from_=from_phone,
        body=f'{title} is currently ${price}.'
    )

    return message.sid


if __name__ == '__main__':
    url = 'https://www.amazon.com/gp/product/B00KC0LLFQ/'
    threshold = 8

    # Get the current price from Amazon
    price = get_price(url)

    # Send a text message if the price is below the threshold
    if price < threshold:
        sid = send_sms(price, 'Coffee')

        if sid:
            print(f'Message sent, sid: {sid}')
