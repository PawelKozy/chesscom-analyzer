# Entry point to run the app
import os
from api.client import ChessAPIClient
from downloader.game_downloader import GameDownloader
from analyzer.analyzer import GameAnalyzer
import config

def main():
    from config import BASE_URL, USERNAME, STORAGE_PATH

    api_client = ChessAPIClient(BASE_URL, USERNAME)
    downloader = GameDownloader(STORAGE_PATH)
    engine_path = "C:\Program Files\stockfish\stockfish-windows-x86-64-avx2.exe"

    # Get archives
    archives = api_client.get_available_game_months()
    print(f"Found {len(archives)} archives.")

    # Example: fetch the latest month's games
    if archives:
        last_archive = archives[-1]
        year, month = map(int, last_archive.rsplit('/', 2)[-2:])
        games = api_client.get_games_for_month(year, month)
        downloader.save_games(games, year, month)
        print(f"Fetched {len(games)} games for {year}-{month:02d}.")

    analysis_folder = os.path.join(STORAGE_PATH, "2025-03")
    engine_path = "C:/Program Files/Stockfish/stockfish-windows-x86-64-avx2.exe"

    analyzer = GameAnalyzer(analysis_folder, engine_path)

    analyzer.find_time_consuming_positions(top_n=5, max_games=157, verbose=True)
    analyzer.find_common_mistakes()
    analyzer.analyze_opening_issues()

    analyzer.close()

if __name__ == "__main__":
    main()
