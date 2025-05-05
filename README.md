# ♟️ Chess Analyzer

An advanced Python application for downloading and analyzing your own [Chess.com](https://www.chess.com/) games.

## 🚀 Features

- ✅ Download games by month via Chess.com Public API
- ✅ Save games as `.json` and `.pgn` in structured folders
- ✅ Deduplication and summary stats per month
- ✅ Analyze time-consuming decisions:
  - Detect where you hesitate most
  - Understand complexity of those positions
  - Get contextual insights like material balance, check status, legal move count
- 🔜 (coming soon): Blunder/inaccuracy detection using Stockfish

---

## 🛠 Requirements

- Python 3.9+
- Packages:
pip install -r requirements.txt

- Optional: [Stockfish](https://stockfishchess.org/download/) for deeper analysis

---

## 📂 Project Structure

chess_analyzer/
├── api/ # Chess.com API client
├── analyzer/ # GameAnalyzer: time use, position complexity
├── downloader/ # Saves PGNs and JSONs
├── utils/ # Reusable decorators
├── config.py # Username, base URL, storage path
├── main.py # Orchestrates download and analysis

---

## ⚙️ Configuration

Edit `config.py` to set your Chess.com username and storage path:

```python
USERNAME = "your_chess_username"
BASE_URL = "https://api.chess.com/pub/player"
STORAGE_PATH = "games"
```

You can also use command-line arguments:

python main.py           # Download latest month
python main.py --all     # Download all available months

##📁 Output Structure

Downloaded games will be saved in:

games/
├── 2025-03/
│   ├── 2025-03-01_18-10-44_1.pgn
│   ├── 2025-03-01_18-10-44_1.json
│   └── summary.json
🔐 You may want to add games/ to .gitignore if you don’t want to commit your own matches.

🧠 Time-Use Analysis
After download, the analyzer shows:

Top N positions where you spent the most time

Whether you were in check

Number of legal moves

Material imbalance

Endgame flag

Example:

swift
Kopiuj
Edytuj
1. ⏱ 16.0s on move 35 (Black played ...Kc7)
   📁 From game: 2025-03-31_22-11-45_157.pgn
   📍 FEN: 8/5b1p/1k1p1bp1/2p2P2/1PP5/3P4/2K4P/2B5 b - - 0 35
✅ Roadmap
 Time-use analysis

 Blunder/inaccuracy detection using Stockfish

 Opening mistake patterns

 Save top positions to JSON

 Add visual board diagrams (optional)

📜 License
MIT (feel free to fork, use, and improve)
