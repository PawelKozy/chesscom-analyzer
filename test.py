import chess.pgn

with open("games/2025-03/2025-03-01_16-57-19_1.pgn", encoding="utf-8") as f:
    game = chess.pgn.read_game(f)

node = game
found = False

while node.variations:
    move = node.variation(0)
    comment = move.comment
    if "%clk" in comment:
        print("✅ Found clock annotation:", comment)
        found = True
        break
    node = move

if not found:
    print("❌ No %clk annotations found in this PGN.")
