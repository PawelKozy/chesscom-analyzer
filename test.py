import logging
import chess.pgn

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

with open("games/2025-03/2025-03-01_16-57-19_1.pgn", encoding="utf-8") as f:
    game = chess.pgn.read_game(f)

node = game
found = False

while node.variations:
    move = node.variation(0)
    comment = move.comment
    if "%clk" in comment:
        logger.info("✅ Found clock annotation: %s", comment)
        found = True
        break
    node = move

if not found:
    logger.warning("❌ No %clk annotations found in this PGN.")
