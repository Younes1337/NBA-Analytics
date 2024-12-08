import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from typing import Dict, Any

class NBADataProcessor:
    def __init__(self):
        self.raw_data = pd.DataFrame()
        self.processed_data = pd.DataFrame()

    def fetch_live_game_data(self) -> pd.DataFrame:
        """
        Fetches live NBA game data using the nba_api and formats it into a structured DataFrame
        with relevant game information for both home and away teams.
        """
        try:
            # Fetch live scoreboard data
            games = scoreboard.ScoreBoard()
            games_data = games.get_dict()

            # Check if the data is available and valid
            if 'scoreboard' not in games_data or 'games' not in games_data['scoreboard']:
                raise ValueError("Invalid or empty data received from the NBA API.")

            # Extract relevant information from the game data for both home and away teams
            game_info = [
                self._extract_team_info(game, team_type='home') for game in games_data['scoreboard']['games']
            ] + [
                self._extract_team_info(game, team_type='away') for game in games_data['scoreboard']['games']
            ]

            # Create a Pandas DataFrame from the extracted data
            self.raw_data = pd.DataFrame(game_info)
            return self.raw_data

        except Exception as e:
            print(f"Error fetching NBA game data: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of error

    def preprocess_data(self) -> pd.DataFrame:
      """
      Preprocesses the raw game data to prepare it for modeling, including feature engineering
      such as encoding, time conversion, and target creation.
      """
      if self.raw_data.empty:
          raise ValueError("No raw data available. Please fetch data first.")

      df_encoded = pd.get_dummies(self.raw_data, columns=['TEAM'], drop_first=False)

      # Convert only the team columns (that were generated) to 0 and 1
      team_columns = [col for col in df_encoded.columns if 'TEAM_' in col]
      df_encoded[team_columns] = df_encoded[team_columns].astype(int)

      # Add the target column 'WIN'
      df_encoded['WIN'] = (df_encoded['POINTS_DIFFERENTIAL'] > 0).astype(int)

      # Convert the 'TIME_REMAINING' column to seconds
      df_encoded['TIME_REMAINING'] = df_encoded['TIME_REMAINING'].apply(self._time_to_seconds)

      # Encode 'HOME_AWAY' as binary (0 for Away, 1 for Home)
      df_encoded['HOME_AWAY'] = (df_encoded['HOME_AWAY'] == 'Home').astype(int)

      self.processed_data = df_encoded
      return self.processed_data


    def _extract_team_info(self, game: Dict[str, Any], team_type: str) -> Dict[str, Any]:
        """
        Extracts relevant game information for either the home or away team.

        Args:
            game (dict): A dictionary containing information about a single NBA game.
            team_type (str): Specify 'home' or 'away' to extract data for the respective team.

        Returns:
            dict: A dictionary with relevant game details: 'TIME_REMAINING', 'POINTS_DIFFERENTIAL',
                  'HOME_AWAY', and 'TEAM'.
        """
        if team_type == 'home':
            team = game['homeTeam']['teamTricode']
            score = game['homeTeam']['score']
            opponent_score = game['awayTeam']['score']
            home_away = 'Home'
        elif team_type == 'away':
            team = game['awayTeam']['teamTricode']
            score = game['awayTeam']['score']
            opponent_score = game['homeTeam']['score']
            home_away = 'Away'
        else:
            raise ValueError("Invalid team_type. Must be 'home' or 'away'.")

        # Determine the time remaining (game clock) or set as 'N/A' if not available
        time_remaining = game.get('gameClock', 'N/A')

        # Calculate the points differential
        points_diff = score - opponent_score

        return {
            'TIME_REMAINING': time_remaining,
            'POINTS_DIFFERENTIAL': points_diff,
            'HOME_AWAY': home_away,
            'TEAM': team
        }

    @staticmethod
    def _time_to_seconds(time_str: str) -> int:
        """
        Converts a time string in the format MM:SS to total seconds.
        If the time string is empty or invalid, returns 0.

        Args:
            time_str (str): The time string to convert.

        Returns:
            int: The total time in seconds.
        """
        if not time_str or time_str == 'N/A':  # Check for empty or invalid strings
            return 0
        try:
            minutes, seconds = map(int, time_str.split(":"))
            return minutes * 60 + seconds
        except ValueError:
            # If the format is invalid, return 0
            return 0
