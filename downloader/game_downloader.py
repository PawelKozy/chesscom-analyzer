import os
import json
import logging
from typing import List, Dict
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class GameDownloader:
    """
    Downloads game data and saves it locally in structured folders.
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def create_folder_structure(self, year: int, month: int) -> str:
        """
        Create a folder like games/2025-03 and return the full path.
        """
        folder_name = f"{year}-{month:02d}"
        folder_path = os.path.join(self.storage_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def _generate_timestamp(self, game: Dict, index: int) -> str:
        end_time = game.get("end_time")
        if end_time:
            return datetime.fromtimestamp(end_time).strftime("%Y-%m-%d_%H-%M-%S")
        return f"game_{index}"

    def _file_exists(self, folder: str, filename: str) -> bool:
        return os.path.exists(os.path.join(folder, filename))

    def save_games(self, games: List[Dict], year: int, month: int):
        """
        Save games as .json and .pgn, and generate a summary.json
        """
        folder_path = self.create_folder_structure(year, month)
        stats = {
            "total_games": 0,
            "opponents": [],
            "results": Counter(),
            "time_controls": Counter()
        }

        for index, game in enumerate(games, start=1):
            timestamp = self._generate_timestamp(game, index)
            base_filename = f"{timestamp}_{index}"
            json_filename = base_filename + ".json"
            pgn_filename = base_filename + ".pgn"

            # Deduplication check
            if self._file_exists(folder_path, json_filename):
                logger.warning(f"⚠️ Skipping duplicate: {json_filename}")
                continue

            # Save JSON
            json_path = os.path.join(folder_path, json_filename)
            with open(json_path, "w", encoding="utf-8") as f_json:
                json.dump(game, f_json, indent=2)

            # Save PGN
            pgn_text = game.get("pgn")
            if pgn_text:
                pgn_path = os.path.join(folder_path, pgn_filename)
                with open(pgn_path, "w", encoding="utf-8") as f_pgn:
                    f_pgn.write(pgn_text)

            # Update stats
            stats["total_games"] += 1
            opponent = game.get("white", {}).get("username") if game["black"]["username"].lower() == self.storage_path.lower() else game.get("black", {}).get("username")
            result = game.get("white", {}).get("result") if game["black"]["username"].lower() == self.storage_path.lower() else game.get("black", {}).get("result")
            stats["opponents"].append(opponent)
            stats["results"][result] += 1
            stats["time_controls"][game.get("time_control", "unknown")] += 1

        # Save summary.json
        summary_path = os.path.join(folder_path, "summary.json")
        stats["opponents"] = dict(Counter(stats["opponents"]))
        stats["results"] = dict(stats["results"])
        stats["time_controls"] = dict(stats["time_controls"])

        with open(summary_path, "w", encoding="utf-8") as f_summary:
            json.dump(stats, f_summary, indent=2)

        logger.info(f"✅ Saved {stats['total_games']} new games to {folder_path}")
        logger.info("📄 Summary written to summary.json")
