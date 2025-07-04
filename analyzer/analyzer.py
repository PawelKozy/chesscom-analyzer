import os
import chess
import re
import chess.pgn
import chess.engine
import logging
from typing import List
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class GameAnalyzer:
    """
    Analyzes downloaded chess games for insights using python-chess.
    """
    def __init__(self, game_folder: str, engine_path: str):
        self.game_folder = game_folder
        self.engine_path = engine_path
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def _load_pgn_files(self) -> List[str]:
        return [os.path.join(self.game_folder, f) for f in os.listdir(self.game_folder) if f.endswith(".pgn")]

    def find_time_consuming_positions(self, top_n: int = 5, max_games: int = None, verbose: bool = False):
        """
        Finds positions where the player spent the most time (based on %clk comments).
        Prints top N most time-consuming decisions with contextual info.
        """
        logger.info("\n🕒 Finding time-consuming positions...")

        time_spent = []
        files = self._load_pgn_files()
        if max_games:
            files = files[:max_games]

        for i, file in enumerate(files, start=1):
            if verbose:
                logger.info(f"🔄 Analyzing game {i}/{len(files)}: {os.path.basename(file)}")

            with open(file, encoding="utf-8") as f:
                game = chess.pgn.read_game(f)

            if not game:
                logger.warning(f"⚠️ Skipping invalid PGN file: {file}")
                continue

            node = game
            previous_time = None
            move_counter = 0

            while node.variations and move_counter < 200:
                move = node.variation(0)
                comment = move.comment

                import re

                # inside the loop
                if "%clk" in comment:
                    try:
                        # PREVIOUSLY: board_before = move.parent.board()
                        board_before = move.parent.board()

                        # New analysis
                        legal_moves = board_before.legal_moves.count()
                        in_check = board_before.is_check()
                        piece_map = board_before.piece_map()
                        white_material = sum(p.piece_type for s, p in piece_map.items() if p.color == chess.WHITE)
                        black_material = sum(p.piece_type for s, p in piece_map.items() if p.color == chess.BLACK)
                        material_balance = white_material - black_material
                        is_endgame = white_material + black_material <= 14  # heuristic threshold

                        # Get SAN before the move is applied
                        san = board_before.san(move.move)

                        # Extract clock value with regex
                        match = re.search(r"%clk\s+(\d+):(\d+)(?:\.\d+)?", comment)
                        if match:
                            minutes = int(match.group(1))
                            seconds = int(match.group(2))
                            current_time = minutes * 60 + seconds

                            if previous_time is not None:
                                spent = previous_time - current_time
                                if spent > 0:
                                    time_spent.append({
                                        "seconds_spent": spent,
                                        "fen": board_before.fen(),  # also before the move
                                        "move_number": board_before.fullmove_number,
                                        "player": "White" if board_before.turn else "Black",
                                        "move_san": san,
                                        "legal_moves": legal_moves,
                                        "in_check": in_check,
                                        "material_balance": material_balance,
                                        "is_endgame": is_endgame,
                                        "file": os.path.basename(file)
                                    })

                            previous_time = current_time
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing clock: {e}")

                node = move
                move_counter += 1

        if not time_spent:
            logger.warning("⚠️ No %clk comments found in the selected games.")
            return

        top_positions = sorted(time_spent, key=lambda x: x["seconds_spent"], reverse=True)[:top_n]
        logger.info("\n📊 Hesitation Pattern Insights:")
        total = len(time_spent)

        simple_positions = sum(1 for x in time_spent if x["legal_moves"] <= 10)
        in_check_count = sum(1 for x in time_spent if x["in_check"])
        endgame_count = sum(1 for x in time_spent if x["is_endgame"])

        logger.info(f"• Positions analyzed: {total}")
        logger.info(
            f"• Spent time in low-complexity positions (<=10 legal moves): {simple_positions} ({simple_positions / total:.1%})")
        logger.info(f"• Spent time while in check: {in_check_count} ({in_check_count / total:.1%})")
        logger.info(f"• Spent time in endgames: {endgame_count} ({endgame_count / total:.1%})")

        logger.info(f"\n🎯 Top {top_n} most time-consuming positions:")
        for i, pos in enumerate(top_positions, 1):
            logger.info(
                f"{i}. ⏱ {pos['seconds_spent']:.1f}s on move {pos['move_number']} ({pos['player']} played {pos['move_san']})")
            logger.info(f"   📁 From game: {pos['file']}")
            logger.info(f"   📍 FEN: {pos['fen']}")
            logger.info("-" * 60)

    def find_common_mistakes(self, limit_eval_drop: float = 1.5, max_games: int = None, verbose: bool = False):
        """
        Identifies blunders/inaccuracies with Stockfish and displays human-readable descriptions and eval interpretation.
        """
        logger.info("\n❌ Common blunders or inaccuracies:")

        all_mistakes = []
        mistake_moves = Counter()
        files = self._load_pgn_files()
        if max_games:
            files = files[:max_games]

        piece_names = {
            "P": "Pawn", "N": "Knight", "B": "Bishop", "R": "Rook", "Q": "Queen", "K": "King"
        }

        def describe_move(move_san):
            if move_san in ["O-O", "O-O-O"]:
                return "Castles kingside" if move_san == "O-O" else "Castles queenside"
            piece = "Pawn"
            dest = move_san[-2:]
            if move_san[0].isupper() and move_san[0] in piece_names:
                piece = piece_names[move_san[0]]
            return f"{piece} to {dest}"

        def format_eval(eval_score):
            if eval_score is None:
                return "?"
            if eval_score >= 9000:
                return "#Mate for White"
            if eval_score <= -9000:
                return "#Mate for Black"
            return f"{eval_score / 100:.2f}"

        for i, file in enumerate(files, 1):
            if verbose:
                logger.info(f"🔍 Evaluating game {i}/{len(files)}: {os.path.basename(file)}")

            with open(file, encoding="utf-8") as f:
                game = chess.pgn.read_game(f)

            if not game:
                continue

            board = game.board()
            node = game
            move_number = 0
            headers = game.headers
            white = headers.get("White", "Unknown")
            black = headers.get("Black", "Unknown")
            white_elo = headers.get("WhiteElo", "N/A")
            black_elo = headers.get("BlackElo", "N/A")

            while node.variations:
                move = node.variation(0)
                move_number += 1

                if board.turn == chess.WHITE:  # Change if you play Black
                    try:
                        info_before = self.engine.analyse(board, chess.engine.Limit(depth=12))
                        eval_before = info_before["score"].relative.score(mate_score=10000)
                    except Exception:
                        break
                else:
                    board.push(move.move)
                    node = move
                    continue

                try:
                    board_before = move.parent.board()
                    san = board_before.san(move.move)
                    description = describe_move(san)
                except Exception:
                    san = "?"
                    description = "Unrecognized move"

                board.push(move.move)

                try:
                    info_after = self.engine.analyse(board, chess.engine.Limit(depth=12))
                    eval_after = info_after["score"].relative.score(mate_score=10000)
                except Exception:
                    continue

                if eval_before is not None and eval_after is not None:
                    eval_drop = eval_before - eval_after
                    if eval_drop > limit_eval_drop:
                        all_mistakes.append({
                            "move_number": move_number,
                            "move_san": san,
                            "description": description,
                            "eval_drop": eval_drop,
                            "eval_before": eval_before,
                            "eval_after": eval_after,
                            "fen": board_before.fen(),
                            "file": os.path.basename(file),
                            "white": white,
                            "black": black,
                            "white_elo": white_elo,
                            "black_elo": black_elo
                        })
                        mistake_moves[san] += 1
                node = move

        if not all_mistakes:
            logger.info("✅ No major mistakes detected.")
            return

        top_blunders = sorted(all_mistakes, key=lambda x: x["eval_drop"], reverse=True)[:5]

        logger.info("\n🔻 Top evaluation drops:")
        for i, m in enumerate(top_blunders, 1):
            logger.info(f"{i}. {m['move_san']} → {m['description']}")
            logger.info(
                f"   Eval dropped from {format_eval(m['eval_before'])} to {format_eval(m['eval_after'])} (Δ -{m['eval_drop']:.1f})")
            logger.info(f"   📁 Game: {m['file']} | {m['white']} ({m['white_elo']}) vs {m['black']} ({m['black_elo']})")
            logger.info(f"   📍 FEN: {m['fen']}")
            logger.info("-" * 60)

        logger.info("\n♻️ Most frequently repeated mistakes (by move SAN):")
        for move, count in mistake_moves.most_common(5):
            logger.info(f"• {move} → {count} times")

    def analyze_opening_issues(self, move_limit: int = 10):
        """
        Extracts the most common problematic positions in the opening.
        """
        logger.info("\n♟️ Opening issues:")
        issues = Counter()

        for file in self._load_pgn_files():
            with open(file, encoding="utf-8") as f:
                game = chess.pgn.read_game(f)

            node = game
            board = game.board()
            prev_eval = None
            move_count = 0

            while node.variations and move_count < move_limit:
                move = node.variation(0)
                board.push(move.move)
                move_count += 1

                info = self.engine.analyse(board, chess.engine.Limit(depth=12))
                score = info["score"].relative.score(mate_score=10000)

                if prev_eval is not None and score is not None:
                    eval_drop = prev_eval - score
                    if eval_drop > 1:
                        issues[board.fen()] += 1

                prev_eval = score
                node = move

        for i, (fen, count) in enumerate(issues.most_common(5), 1):
            logger.info(f"{i}. Eval drop in opening ({count} times): {fen}")

    def summarize_total_time_played(self, max_games: int = None):
        """
        Sums total time (in minutes) spent playing games based on clock comments.
        """
        logger.info("\n⏳ Total Time Spent Playing:")
        import re

        files = self._load_pgn_files()
        if max_games:
            files = files[:max_games]

        total_seconds = 0
        for file in files:
            with open(file, encoding="utf-8") as f:
                game = chess.pgn.read_game(f)
            if not game:
                continue

            previous_time = None
            for node in game.mainline():
                comment = node.comment
                if "%clk" in comment:
                    match = re.search(r"%clk\s+(\d+):(\d+)(?:\.(\d+))?", comment)
                    if match:
                        minutes = int(match.group(1))
                        seconds = int(match.group(2))
                        current_time = minutes * 60 + seconds
                        if previous_time and current_time < previous_time:
                            total_seconds += previous_time - current_time
                        previous_time = current_time

        total_minutes = total_seconds // 60
        hours = total_minutes // 60
        minutes = total_minutes % 60
        logger.info(f"🕰 Estimated total clocked time: {hours}h {minutes}m")

    def analyze_progress_over_time(self, limit_eval_drop: float = 1.5, max_games: int = None):
        """
        Analyzes progress over time, grouping by game date.
        Skips illegal moves and filters mate evals. Normalizes evals to pawns.
        """
        logger.info("\n📊 Regression Analysis: Progress Over Time")
        from collections import defaultdict
        import datetime

        files = self._load_pgn_files()
        if max_games:
            files = files[:max_games]

        daily_stats = defaultdict(lambda: {"games": 0, "blunders": 0, "total_eval_drop": 0.0})

        for file in files:
            with open(file, encoding="utf-8") as f:
                game = chess.pgn.read_game(f)

            if not game:
                continue

            date_str = game.headers.get("Date", "????.??.??")
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y.%m.%d").date()
            except ValueError:
                continue

            board = game.board()
            node = game
            game_blunders = 0
            game_eval_drop = 0.0

            while node.variations:
                move = node.variation(0)

                if board.turn == chess.WHITE:
                    try:
                        info_before = self.engine.analyse(board, chess.engine.Limit(depth=12))
                        eval_before = info_before["score"].relative.score(mate_score=10000)
                    except Exception:
                        break
                else:
                    if move.move in board.legal_moves:
                        board.push(move.move)
                    node = move
                    continue

                try:
                    board_before = move.parent.board()
                except Exception:
                    board_before = board.copy()

                if move.move in board.legal_moves:
                    board.push(move.move)
                else:
                    logger.warning(f"⚠️ Skipping illegal move {move.move} in {file}")
                    break

                try:
                    info_after = self.engine.analyse(board, chess.engine.Limit(depth=12))
                    eval_after = info_after["score"].relative.score(mate_score=10000)
                except Exception:
                    continue

                if abs(eval_before) >= 9000 or abs(eval_after) >= 9000:
                    continue

                drop = eval_before - eval_after
                if drop > limit_eval_drop * 100:
                    drop = min(drop, 1000)
                    game_blunders += 1
                    game_eval_drop += drop

                node = move

            daily_stats[date_obj]["games"] += 1
            daily_stats[date_obj]["blunders"] += game_blunders
            daily_stats[date_obj]["total_eval_drop"] += game_eval_drop

        if not daily_stats:
            logger.warning("⚠️ No games with valid date headers or no mistakes found.")
            return

        logger.info("\n📅 Daily Summary:")
        for day in sorted(daily_stats.keys()):
            stats = daily_stats[day]
            games = stats["games"]
            blunders = stats["blunders"]
            avg_drop = (stats["total_eval_drop"] / max(blunders, 1)) / 100
            logger.info(f"{day}: {games} game(s), {blunders} blunder(s), avg eval drop: {avg_drop:.2f} pawns")

        logger.info("\n✅ Use this to see if you're improving day by day.")

    def close(self):
        self.engine.quit()
