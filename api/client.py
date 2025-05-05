import requests
from utils.decorators import retry, log_execution


class ChessAPIClient:
    """
    Client to interact with the Chess.com public API.
    """
    def __init__(self, base_url: str, username: str):
        self.base_url = base_url.rstrip('/')
        self.username = username.lower()
        self.headers = {
            "User-Agent": "ChessAnalyzerBot/1.0 (https://github.com/pawelkozy)"
        }

    @log_execution
    @retry(times=3, delay=1.5)
    def get_available_game_months(self) -> list:
        """
        Fetch the list of archive URLs for the user's monthly games.
        """
        url = f"{self.base_url}/{self.username}/games/archives"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("archives", [])

    @log_execution
    @retry(times=3, delay=1.5)
    def get_games_for_month(self, year: int, month: int) -> list:
        """
        Fetch games for a specific month.
        """
        month_str = f"{month:02d}"
        url = f"{self.base_url}/{self.username}/games/{year}/{month_str}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("games", [])
