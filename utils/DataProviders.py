import pandas as pd
from sbrscrape import Scoreboard


class SbrOddsProvider:
    def __init__(self):
        sb = Scoreboard(sport="NBA")
        self.games = sb.games if hasattr(sb, 'games') else []
        self.sportbooks = ["fanduel", "betmgm", "caesars", "draftkings", "bet365"]  # All sportsbooks

    def get_odds(self):
        """Retrieve odds from the games and return as a dictionary."""
        dict_res = {}
        for game in self.games:
            home_team_name = game['home_team'].replace("Los Angeles Clippers", "LA Clippers")
            away_team_name = game['away_team'].replace("Los Angeles Clippers", "LA Clippers")

            game_odds = {
                'under_over_odds': game['total'].get(self.sportbooks[0], None),  # Default to the first sportsbook
                home_team_name: {},
                away_team_name: {}
            }

            # Loop through all sportsbooks and get the odds for each
            for sportsbook in self.sportbooks:
                home_moneyline = game['home_ml'].get(sportsbook, None)
                away_moneyline = game['away_ml'].get(sportsbook, None)

                game_odds[home_team_name][sportsbook] = home_moneyline
                game_odds[away_team_name][sportsbook] = away_moneyline

            dict_res[home_team_name + ':' + away_team_name] = game_odds

        return dict_res

    def get_odds_table(self):
        """Convert the odds dictionary into a structured table using pandas."""
        odds = self.get_odds()
        table_data = []

        # Group data by teams
        teams_data = {}

        for game, details in odds.items():
            home_team, away_team = game.split(":")

            if home_team not in teams_data:
                teams_data[home_team] = {sportsbook: None for sportsbook in self.sportbooks}
            if away_team not in teams_data:
                teams_data[away_team] = {sportsbook: None for sportsbook in self.sportbooks}

            # Set the moneyline odds for each team for each sportsbook
            for sportsbook in self.sportbooks:
                teams_data[home_team][sportsbook] = details[home_team].get(sportsbook, None)
                teams_data[away_team][sportsbook] = details[away_team].get(sportsbook, None)

        # Prepare rows for the table
        for team, odds in teams_data.items():
            row = {"Team": team}
            row.update(odds)
            table_data.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(table_data)
        return df

