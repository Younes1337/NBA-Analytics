import bs4
from bs4 import BeautifulSoup
import requests
import pandas as pd


def extract_money_lines(url, dateStr):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    payload = {
        'sport': 'basketball',
        'league': 'nba',
        'region': 'us',
        'lang': 'en',
        'contentorigin': 'espn',
        'buyWindow': '1m',
        'showAirings': 'buy,live,replay',
        'tz': 'America/New_York',
        'dates': dateStr}

    response = requests.get(url, headers=headers, params=payload).json()
    events = response['sports'][0]['leagues'][0]['events']

    df = pd.json_normalize(events,
                           record_path=['competitors'],
                           meta=['odds', ['odds', 'away', 'moneyLine'], ['odds', 'home', 'moneyLine']],
                           errors='ignore')

    reshaped_data = []

    for i in range(0, len(df), 2):
        row_away = df.iloc[i]
        row_home = df.iloc[i + 1]
        reshaped_row = {
            'away': f"{row_away['displayName']}",
            'home': f"{row_home['displayName']}",
            'odds.away.moneyLine': row_away['odds.away.moneyLine'],
            'odds.home.moneyLine': row_home['odds.home.moneyLine']
        }
        reshaped_data.append(reshaped_row)

    reshaped_df = pd.DataFrame(reshaped_data)

    return reshaped_df


def moneyline_to_probability(moneyline):
    """
    Converts a moneyline to its implied probability (in decimal form).
    """
    try:
        moneyline = int(moneyline)
        if moneyline > 0:
            probability = 100 / (moneyline + 100)
        else:
            probability = abs(moneyline) / (abs(moneyline) + 100)
        return round(probability, 4)  # Return a decimal probability (e.g., 0.9091)
    except ValueError:
        return None  # Handle cases where the moneyline is invalid


# Function to calculate the potential price from the moneyline
def calculate_price(probability):
    """
    Calculates the price based on the implied probability.
    """
    if probability is None:
        return "N/A"  # Handle invalid probabilities
    try:
        return round(1 / probability, 2)  # Return the calculated price
    except ZeroDivisionError:
        return "N/A"
