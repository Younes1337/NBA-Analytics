from nba_api.live.nba.endpoints import scoreboard
import streamlit as st
from datetime import datetime
from utils.utils import extract_money_lines, moneyline_to_probability, calculate_price
from utils.DataProviders import SbrOddsProvider
import pytz

# Set Streamlit page config for better visuals
st.set_page_config(page_title="NBA Live Scores", page_icon="🏀", layout="wide")

# Add a sidebar with a selectbox
st.sidebar.title("Select your Data")
page_option = st.sidebar.selectbox(
    "Select an option:",
    ("Live Data", "Historical Data")
)

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
    games_data = nba_live_data()
    moneyline_df = moneyline_data()
    games = games_data.get("scoreboard", {}).get("games", [])

    if games:
        st.markdown(
            """
            <div style="text-align: center; font-size: 24px; margin-bottom: 20px; color: #ffffff;">
                <strong>Home Team  Vs  Away Team</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for game in games:
            home_team = game["homeTeam"]["teamName"]
            away_team = game["awayTeam"]["teamName"]
            home_score = game["homeTeam"]["score"]
            away_score = game["awayTeam"]["score"]
            status = game["gameStatusText"]
            home_full_name = f"{game['homeTeam']['teamCity']} {home_team}"
            away_full_name = f"{game['awayTeam']['teamCity']} {away_team}"
            home_moneyline = moneyline_df[moneyline_df["home"] == home_full_name]["odds.home.moneyLine"].values
            away_moneyline = moneyline_df[moneyline_df["away"] == away_full_name]["odds.away.moneyLine"].values
            home_moneyline = home_moneyline[0] if home_moneyline else "N/A"
            away_moneyline = away_moneyline[0] if away_moneyline else "N/A"
            home_probability = moneyline_to_probability(home_moneyline)
            away_probability = moneyline_to_probability(away_moneyline)
            home_price = calculate_price(home_probability)
            away_price = calculate_price(away_probability)

            def moneyline_color(moneyline):
                if moneyline == "N/A":
                    return "white"
                elif int(moneyline) > 0:
                    return "green"
                else:
                    return "red"

            st.markdown(
                f"""
                <div style="border: 1px solid #555; border-radius: 10px; padding: 10px; margin-bottom: 15px; background-color: #000000; color: #ffffff; max-width: 600px; margin-left: auto; margin-right: auto;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="text-align: left;">
                            <h4 style="margin: 5px 0; color: #4CAF50;">{home_full_name}</h4>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Score: {home_score}</p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Moneyline: <span style="color: {moneyline_color(home_moneyline)};">{home_moneyline}</span></p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Implied Probability: {home_probability if home_probability else "N/A"}</p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Price: {home_price}</p>
                        </div>
                        <div style="text-align: center; font-size: 14px; color: #bbbbbb;">
                            <p style="margin: 5px 0; font-weight: bold;">{status}</p>
                        </div>
                        <div style="text-align: right;">
                            <h4 style="margin: 5px 0; color: #FF5722;">{away_full_name}</h4>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Score: {away_score}</p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Moneyline: <span style="color: {moneyline_color(away_moneyline)};">{away_moneyline}</span></p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Implied Probability: {away_probability if away_probability else "N/A"}</p>
                            <p style="margin: 5px 0; font-size: 14px; color: #dddddd;">Price: {away_price}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        sportbooks = ["fanduel", "betmgm", "caesars",
                      "draftkings", "bet365", "betrivers",
                      ""]
        for sportbook in sportbooks:
            st.write(f"Live data for {sportbook}")
            provider = SbrOddsProvider(sportbook)
            df = provider.get_odds_table()
            st.table(df)

    else:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 30px; color: #ffffff;">
                <h4>No live NBA games available right now.</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Display historical data
def display_historical_data():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px; color: #ffffff;">
            <h4>Historical Data is Coming Soon!</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Main logic
if __name__ == "__main__":
    if page_option == "Live Data":
        display_nba_live_data()
    elif page_option == "Historical Data":
        display_historical_data()
