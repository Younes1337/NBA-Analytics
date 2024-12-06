import pandas as pd
from sbrscrape import Scoreboard


class SbrOddsProvider:
    def __init__(self, sportsbook="fanduel"):
        sb = Scoreboard(sport="NBA")
        self.games = sb.games if hasattr(sb, 'games') else []
        self.sportsbook = sportsbook

    def get_odds(self):
        """Retrieve odds from the games and return as a dictionary."""
        dict_res = {}
        for game in self.games:
            home_team_name = game['home_team'].replace("Los Angeles Clippers", "LA Clippers")
            away_team_name = game['away_team'].replace("Los Angeles Clippers", "LA Clippers")

            money_line_home_value = game['home_ml'].get(self.sportsbook, None)
            money_line_away_value = game['away_ml'].get(self.sportsbook, None)
            totals_value = game['total'].get(self.sportsbook, None)

            dict_res[home_team_name + ':' + away_team_name] = {
                'under_over_odds': totals_value,
                home_team_name: {'money_line_odds': money_line_home_value},
                away_team_name: {'money_line_odds': money_line_away_value},
            }
        return dict_res

    def get_odds_table(self):
        """Convert the odds dictionary into a structured table using pandas."""
        odds = self.get_odds()
        table_data = []
        for game, details in odds.items():
            home_team, away_team = game.split(":")
            row = {
                "Home Team": home_team,
                "Away Team": away_team,
                "Home Moneyline Odds": details[home_team]["money_line_odds"],
                "Away Moneyline Odds": details[away_team]["money_line_odds"],
                "Under/Over Odds": details["under_over_odds"],
            }
            table_data.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(table_data)
        return df
