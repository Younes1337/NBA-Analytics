from nba_api.live.nba.endpoints import scoreboard
import streamlit as st
from datetime import datetime
from utils.utils import extract_money_lines, moneyline_to_probability, calculate_price
from utils.DataProviders import SbrOddsProvider
import pytz
import time

# Set Streamlit page config for better visuals
st.set_page_config(page_title="NBA Live Scores / Predictions", page_icon="🏀", layout="wide")

# Center the title of the app
st.markdown(
    """
    <style>
        .centered-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
        }
    </style>
    <div class="centered-title">
        🏀 NBA Live Scores
    </div>
    """,
    unsafe_allow_html=True,
)

# Subtitle
st.markdown(
    """
    <div style="text-align: center; color: #999; font-size: 16px; margin-bottom: 20px;">
        Stay updated with <strong>real-time NBA game updates</strong>! Data refreshes every minute.
    </div>
    """,
    unsafe_allow_html=True,
)

# Function to fetch live NBA data
def nba_live_data():
    games = scoreboard.ScoreBoard()
    data = games.get_dict()
    return data

# Function to fetch moneyline data
def moneyline_data():
    usa_timezone = pytz.timezone('America/New_York')
    current_time_usa = datetime.now(usa_timezone)
    dateStr = current_time_usa.strftime('%Y%m%d')
    url = "https://site.web.api.espn.com/apis/v2/scoreboard/header"
    df = extract_money_lines(url, dateStr)
    return df

# Display live NBA data
def display_nba_live_data():
    placeholder = st.empty()  # Placeholder for dynamic table updates

    # Get the odds
    sbr_provider = SbrOddsProvider()
    odds_df = sbr_provider.get_odds_table()
    money_line_data = odds_df[['Team', 'bet365']]

    while True:  # Continuous refresh
        # Fetch live data
        games_data = nba_live_data()
        moneyline_df = moneyline_data()
        games = games_data.get("scoreboard", {}).get("games", [])

        # Update the placeholder content
        with placeholder.container():
            if games:
                for game in games:
                    home_team = game["homeTeam"]["teamName"]
                    away_team = game["awayTeam"]["teamName"]
                    home_score = game["homeTeam"]["score"]
                    away_score = game["awayTeam"]["score"]
                    status = game["gameStatusText"]
                    home_full_name = f"{game['homeTeam']['teamCity']} {home_team}"
                    away_full_name = f"{game['awayTeam']['teamCity']} {away_team}"

                    home_moneyline = money_line_data[money_line_data["Team"] == home_full_name]["bet365"].values
                    away_moneyline = money_line_data[money_line_data["Team"] == away_full_name]["bet365"].values

                    home_moneyline = home_moneyline[0] if home_moneyline else "N/A"
                    away_moneyline = away_moneyline[0] if away_moneyline else "N/A"
                    home_price = moneyline_to_probability(home_moneyline)
                    away_price = moneyline_to_probability(away_moneyline)

                    def moneyline_color(moneyline):
                        if moneyline == "N/A":
                            return "white"
                        elif int(moneyline) > 0:
                            return "green"
                        else:
                            return "red"

                    st.markdown(
                        f"""
                        <div style="border: 2px solid #444; border-radius: 15px; padding: 20px; margin-bottom: 20px; background: linear-gradient(145deg, #0f0f0f, #202020); color: #ffffff; max-width: 700px; margin-left: auto; margin-right: auto; box-shadow: 3px 3px 8px #000000, -3px -3px 8px #2a2a2a;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="text-align: left; width: 45%;">
                                    <h3 style="margin: 10px 0; color: #4CAF50;">{home_full_name}</h3>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Score: <strong>{home_score}</strong></p>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Moneyline: <span style="color: {moneyline_color(home_moneyline)};">{home_moneyline}</span></p>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Price: <strong>{home_price}</strong></p>
                                </div>
                                <div style="text-align: center; font-size: 16px; color: #bbbbbb; width: 10%;">
                                    <p style="margin: 0; font-weight: bold; color: #FFD700;">{status}</p>
                                </div>
                                <div style="text-align: right; width: 45%;">
                                    <h3 style="margin: 10px 0; color: #FF5722;">{away_full_name}</h3>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Score: <strong>{away_score}</strong></p>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Moneyline: <span style="color: {moneyline_color(away_moneyline)};">{away_moneyline}</span></p>
                                    <p style="margin: 5px 0; font-size: 16px; color: #dddddd;"> Price: <strong>{away_price}</strong></p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Sportsbook tables
                st.markdown(
                    """
                    <div style="text-align: center; font-size: 20px; margin-top: 20px; color: #FFD700;">
                         <strong>Sportsbook Odds</strong> 
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.table(odds_df)

            else:
                st.markdown(
                    """
                    <div style="text-align: center; margin-top: 50px; color: #ffffff; font-size: 22px;">
                        <h4>🚫 No live NBA games available right now. 🚫</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        time.sleep(60)


if __name__ == "__main__":
    display_nba_live_data()
