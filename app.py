"""
Flask Web API for Chess Bot with Drag-and-Drop Interface
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
from chess_board import ChessBoard, Move, Color, PieceType
from move_generator import MoveGenerator
from chess_engine import ChessEngine

app = Flask(__name__)
app.secret_key = 'chess_bot_secret_key_2024'
CORS(app)

# Store active games
games = {}

class ChessGameAPI:
    def __init__(self, engine_depth=4):
        self.board = ChessBoard()
        self.engine = ChessEngine(max_depth=engine_depth)
        self.human_color = Color.WHITE
        self.engine_color = Color.BLACK
        self.game_over = False
        self.winner = None
    
    def get_board_state(self):
        """Get current board state as JSON"""
        board_data = []
        for row in range(8):
            board_row = []
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    piece_data = {
                        'type': piece.type.name.lower(),
                        'color': 'white' if piece.color == Color.WHITE else 'black',
                        'symbol': str(piece)
                    }
                else:
                    piece_data = None
                board_row.append(piece_data)
            board_data.append(board_row)
        
        return {
            'board': board_data,
            'current_player': 'white' if self.board.current_player == Color.WHITE else 'black',
            'in_check': self.board.is_in_check(self.board.current_player),
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    def get_legal_moves(self, from_row, from_col):
        """Get legal moves for piece at position"""
        move_generator = MoveGenerator(self.board)
        piece = self.board.get_piece(from_row, from_col)
        
        if not piece or piece.color != self.board.current_player:
            return []
        
        all_moves = move_generator.generate_piece_moves(from_row, from_col)
        legal_positions = []
        
        for move in all_moves:
            legal_positions.append({
                'row': move.to_pos[0],
                'col': move.to_pos[1],
                'is_capture': bool(self.board.get_piece(move.to_pos[0], move.to_pos[1])),
                'is_castling': move.is_castling,
                'is_en_passant': move.is_en_passant
            })
        
        return legal_positions
    
    def make_move(self, from_row, from_col, to_row, to_col, promotion=None):
        """Make a move and return result"""
        # Create move object
        move = Move((from_row, from_col), (to_row, to_col))
        
        # Detect special moves
        piece = self.board.get_piece(from_row, from_col)
        if piece:
            if piece.type == PieceType.KING and abs(to_col - from_col) == 2:
                move.is_castling = True
            elif (piece.type == PieceType.PAWN and 
                  abs(to_col - from_col) == 1 and 
                  not self.board.get_piece(to_row, to_col) and
                  self.board.en_passant_target == (to_row, to_col)):
                move.is_en_passant = True
            elif promotion:
                promotion_map = {
                    'queen': PieceType.QUEEN,
                    'rook': PieceType.ROOK,
                    'bishop': PieceType.BISHOP,
                    'knight': PieceType.KNIGHT
                }
                move.promotion = promotion_map.get(promotion)
        
        # Validate move
        move_generator = MoveGenerator(self.board)
        legal_moves = move_generator.generate_all_moves(self.board.current_player)
        
        if move not in legal_moves:
            return {'success': False, 'error': 'Illegal move'}
        
        # Make the move
        self._execute_move(move)
        
        # Check for game over
        self._check_game_over()
        
        return {'success': True}
    
    def make_engine_move(self):
        """Make engine move"""
        if self.board.current_player != self.engine_color or self.game_over:
            return {'success': False, 'error': 'Not engine turn or game over'}
        
        move = self.engine.get_best_move(self.board)
        if not move:
            return {'success': False, 'error': 'No legal moves'}
        
        self._execute_move(move)
        self._check_game_over()
        
        return {
            'success': True,
            'move': {
                'from': {'row': move.from_pos[0], 'col': move.from_pos[1]},
                'to': {'row': move.to_pos[0], 'col': move.to_pos[1]}
            }
        }
    
    def _execute_move(self, move):
        """Execute a move on the board"""
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return
        
        # Handle special moves
        if move.is_castling:
            # Move king
            self.board.set_piece(to_row, to_col, piece)
            self.board.set_piece(from_row, from_col, None)
            piece.has_moved = True
            
            # Move rook
            if to_col > from_col:  # Kingside
                rook = self.board.get_piece(to_row, 7)
                if rook:
                    self.board.set_piece(to_row, 5, rook)
                    self.board.set_piece(to_row, 7, None)
                    rook.has_moved = True
            else:  # Queenside
                rook = self.board.get_piece(to_row, 0)
                if rook:
                    self.board.set_piece(to_row, 3, rook)
                    self.board.set_piece(to_row, 0, None)
                    rook.has_moved = True
        
        elif move.is_en_passant:
            # Move pawn
            self.board.set_piece(to_row, to_col, piece)
            self.board.set_piece(from_row, from_col, None)
            # Remove captured pawn
            self.board.set_piece(from_row, to_col, None)
        
        else:
            # Regular move
            if move.promotion:
                from chess_board import Piece
                promoted_piece = Piece(move.promotion, piece.color)
                promoted_piece.has_moved = True
                self.board.set_piece(to_row, to_col, promoted_piece)
            else:
                self.board.set_piece(to_row, to_col, piece)
            self.board.set_piece(from_row, from_col, None)
            piece.has_moved = True
        
        # Update en passant target
        self.board.en_passant_target = None
        if (piece.type == PieceType.PAWN and abs(to_row - from_row) == 2):
            self.board.en_passant_target = ((from_row + to_row) // 2, from_col)
        
        # Switch current player
        self.board.current_player = Color.BLACK if self.board.current_player == Color.WHITE else Color.WHITE
        
        # Update move counters
        if piece.type == PieceType.PAWN or self.board.get_piece(to_row, to_col):
            self.board.halfmove_clock = 0
        else:
            self.board.halfmove_clock += 1
        
        if self.board.current_player == Color.WHITE:
            self.board.fullmove_number += 1
    
    def _check_game_over(self):
        """Check if game is over"""
        move_generator = MoveGenerator(self.board)
        moves = move_generator.generate_all_moves(self.board.current_player)
        
        if not moves:
            self.game_over = True
            if self.board.is_in_check(self.board.current_player):
                self.winner = 'black' if self.board.current_player == Color.WHITE else 'white'
            else:
                self.winner = 'draw'

@app.route('/')
def index():
    """Serve the main chess interface"""
    return render_template('chess.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new chess game"""
    game_id = str(uuid.uuid4())
    data = request.get_json() or {}
    difficulty = data.get('difficulty', 4)
    human_color = data.get('color', 'white')
    
    game = ChessGameAPI(engine_depth=difficulty)
    if human_color == 'black':
        game.human_color = Color.BLACK
        game.engine_color = Color.WHITE
    
    games[game_id] = game
    session['game_id'] = game_id
    
    response = {
        'game_id': game_id,
        'board_state': game.get_board_state()
    }
    
    # If engine plays first (human is black), make engine move
    if game.engine_color == Color.WHITE:
        engine_result = game.make_engine_move()
        response['engine_move'] = engine_result
        response['board_state'] = game.get_board_state()
    
    return jsonify(response)

@app.route('/api/board_state/<game_id>')
def get_board_state(game_id):
    """Get current board state"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    return jsonify(game.get_board_state())

@app.route('/api/legal_moves/<game_id>/<int:row>/<int:col>')
def get_legal_moves(game_id, row, col):
    """Get legal moves for piece at position"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    legal_moves = game.get_legal_moves(row, col)
    return jsonify({'legal_moves': legal_moves})

@app.route('/api/make_move/<game_id>', methods=['POST'])
def make_move(game_id):
    """Make a move"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.get_json()
    
    from_row = data['from']['row']
    from_col = data['from']['col']
    to_row = data['to']['row']
    to_col = data['to']['col']
    promotion = data.get('promotion')
    
    # Make human move
    result = game.make_move(from_row, from_col, to_row, to_col, promotion)
    
    if not result['success']:
        return jsonify(result), 400
    
    response = {
        'success': True,
        'board_state': game.get_board_state()
    }
    
    # Make engine move if game continues
    if not game.game_over and game.board.current_player == game.engine_color:
        engine_result = game.make_engine_move()
        response['engine_move'] = engine_result
        response['board_state'] = game.get_board_state()
    
    return jsonify(response)

@app.route('/api/engine_move/<game_id>', methods=['POST'])
def engine_move(game_id):
    """Make engine move"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    result = game.make_engine_move()
    
    return jsonify({
        'engine_move': result,
        'board_state': game.get_board_state()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
