# Competitive Chess Bot

A web-based chess AI with drag-and-drop interface, powered by advanced minimax algorithm and alpha-beta pruning, and any other RL policy you wish to benchmark!

![Chess Bot Interface](https://img.shields.io/badge/Interface-Web%20Based-blue)
![AI Engine](https://img.shields.io/badge/AI-Minimax%20%2B%20Alpha--Beta-green)
![Python](https://img.shields.io/badge/Python-3.7%2B-brightgreen)
![Flask](https://img.shields.io/badge/Flask-Web%20API-red)

## ✨ Features

### 🎮 Interactive Web Interface
- **Drag & Drop Gameplay**: Intuitive piece movement with visual feedback
- **Beautiful Glass Morphism Design**: Modern aesthetic with animated gradients
- **Real-time Move Validation**: Instant legal move highlighting
- **Responsive Design**: Works on desktop and mobile devices

### 🤖 Advanced AI Engine
- **Minimax with Alpha-Beta Pruning**: Optimal move selection algorithm
- **Position Evaluation**: Sophisticated scoring considering material, position, and king safety
- **Multiple Difficulty Levels**: 4 skill levels from Easy to Expert
- **Performance Optimized**: Evaluates thousands of positions per second

### ♟️ Complete Chess Implementation
- **Full Rule Set**: Castling, en passant, pawn promotion, check/checkmate
- **Move History Tracking**: Complete game notation and replay
- **Game State Management**: Proper handling of draws and endgames
- **Legal Move Generation**: Comprehensive move validation system

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/competitive-chess-bot.git
   cd competitive-chess-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8080
   ```

### Alternative: Command Line Interface

For a text-based experience:
```bash
python game_interface.py
```

## Architecture

### Core Components

- **`chess_board.py`**: Board representation and game state management
- **`move_generator.py`**: Legal move generation and validation
- **`chess_engine.py`**: AI engine with minimax and position evaluation
- **`game_interface.py`**: Command-line interface for gameplay

### AI Engine Details

- **Algorithm**: Minimax with alpha-beta pruning
- **Evaluation**: Material + positional bonuses + king safety + mobility
- **Move Ordering**: MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
- **Search Depth**: Configurable (default 4 ply)

## Game Commands

- `e2e4` - Move from e2 to e4
- `e7e8q` - Promote pawn to queen
- `moves` - Show all legal moves
- `help` - Display help
- `quit` - Exit game

## Difficulty Levels

1. **Level 1**: 2-ply search (Beginner)
2. **Level 2**: 3-ply search (Easy)
3. **Level 3**: 4-ply search (Medium)
4. **Level 4**: 5-ply search (Hard) - Default
5. **Level 5**: 6-ply search (Expert)

## Technical Details

### Position Evaluation

The engine evaluates positions based on:
- **Material**: Standard piece values (P=100, N=320, B=330, R=500, Q=900)
- **Position**: Piece-square tables for optimal placement
- **King Safety**: Penalties for exposed king, bonuses for castling
- **Mobility**: Bonus for having more legal moves

### Performance

- Evaluates thousands of positions per second
- Alpha-beta pruning reduces search space significantly
- Move ordering improves pruning efficiency
- Typical search depth of 4-6 ply provides strong play

## Future Enhancements

- Opening book integration
- Endgame tablebase support
- Graphical user interface
- Tournament mode
- Position analysis tools

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)

## License

Open source - feel free to modify and enhance!
