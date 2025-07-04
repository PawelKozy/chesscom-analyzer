# Entry point to run the app
import os
import logging
from api.client import ChessAPIClient
from downloader.game_downloader import GameDownloader
from analyzer.analyzer import GameAnalyzer
import config
import argparse

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Chess.com Game Downloader & Analyzer")
    parser.add_argument("--all", action="store_true", help="Fetch all available archives instead of just the latest")
    return parser.parse_args()


def main():
    from config import BASE_URL, USERNAME, STORAGE_PATH
    args = parse_args()

    api_client = ChessAPIClient(BASE_URL, USERNAME)
    downloader = GameDownloader(STORAGE_PATH)
    engine_path = "C:/Program Files/Stockfish/stockfish-windows-x86-64-avx2.exe"

    # Get archives
    archives = api_client.get_available_game_months()
    archives_to_fetch = archives if args.all else [archives[-1]] if archives else []

    logger.info(f"Found {len(archives)} archives.")

    for archive_url in archives_to_fetch:
        year, month = map(int, archive_url.rsplit('/', 2)[-2:])
        games = api_client.get_games_for_month(year, month)
        downloader.save_games(games, year, month)

    analysis_folder = os.path.join(STORAGE_PATH, "2025-05")
    engine_path = "C:/Program Files/Stockfish/stockfish-windows-x86-64-avx2.exe"

    analyzer = GameAnalyzer(analysis_folder, engine_path)

    analyzer.find_time_consuming_positions(top_n=5, max_games=157, verbose=True)
    analyzer.find_common_mistakes(limit_eval_drop=1.5, max_games=157, verbose=True)
    analyzer.analyze_opening_issues()
    analyzer.summarize_total_time_played()
    analyzer.analyze_progress_over_time(limit_eval_drop=1.5, max_games=157)

    analyzer.close()

if __name__ == "__main__":
    main()
