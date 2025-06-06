
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
- ✅ Blunder/inaccuracy detection using Stockfish
- ✅ Total time spent playing (based on clock comments)
- ✅ Regression analysis:
  - Blunders and eval drops grouped by date or week
  - Useful for tracking your improvement

---

## 🛠 Requirements

- Python 3.9+
- Install dependencies listed in `requirements.txt` (e.g. `requests`, `python-chess`):

   ```bash
   pip install -r requirements.txt
   ```

- Optional: [Stockfish](https://stockfishchess.org/download/) for deeper analysis

---

## 📂 Project Structure

```
chess_analyzer/
├── api/                # Chess.com API client
├── analyzer/           # GameAnalyzer: time use, eval drops, regression
├── downloader/         # Saves PGNs and JSONs
├── utils/              # Reusable decorators
├── config.py           # Username, base URL, storage path
├── main.py             # Orchestrates download and analysis
```

---

## ⚙️ Configuration

Edit `config.py` to set your Chess.com username and storage path:

```python
USERNAME = "your_chess_username"
BASE_URL = "https://api.chess.com/pub/player"
STORAGE_PATH = "games"
```

You can also use command-line arguments:

```bash
python main.py           # Download latest month
python main.py --all     # Download all available months
```

---

## 📁 Output Structure

Downloaded games will be saved in:

```
games/
├── 2025-03/
│   ├── 2025-03-01_18-10-44_1.pgn
│   ├── 2025-03-01_18-10-44_1.json
│   └── summary.json
```

> 🔐 You may want to add `games/` to `.gitignore` if you don’t want to commit your own matches.

---

## 🧠 Analysis Modules

### ⏱ Time-Use Analysis
- Shows positions where you spent the most time
- Context: material imbalance, check status, legal moves

### ❌ Blunder Detection
- Uses Stockfish to find moves with large eval drops
- Shows SAN + human-readable move description
- Ignores forced mates and caps extreme evals

### 📊 Regression Analysis
- Tracks improvement over time
- Daily/weekly summaries of:
  - Games played
  - Blunders
  - Average eval drop per mistake

### ⏳ Total Time Played
- Parses clock annotations to estimate total time spent

---

## ✅ Roadmap

- [x] Time-use analysis  
- [x] Blunder/inaccuracy detection using Stockfish  
- [x] Regression analysis (daily/weekly)  
- [x] Total time estimation  
- [ ] Opening mistake patterns  
- [ ] Save top positions to JSON  
- [ ] Add visual board diagrams (optional)  

---

## 📜 License

MIT (feel free to fork, use, and improve!)
