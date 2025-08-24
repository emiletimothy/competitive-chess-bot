"""
Chess AI Engine with Minimax and Alpha-Beta Pruning
"""

import time
from typing import List, Tuple, Optional, Dict
from chess_board import ChessBoard, Move, Piece, PieceType, Color
from move_generator import MoveGenerator

class ChessEngine:
    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
        self.transposition_table = {}
        self.nodes_evaluated = 0
        
        # Piece values for evaluation
        self.piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }
        
        # Positional bonus tables
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        self.king_middle_game_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]
    
    def get_best_move(self, board: ChessBoard) -> Optional[Move]:
        """Get the best move for current position"""
        self.nodes_evaluated = 0
        start_time = time.time()
        
        best_move, best_score = self.minimax(board, self.max_depth, float('-inf'), float('inf'), True)
        
        end_time = time.time()
        print(f"Evaluated {self.nodes_evaluated} positions in {end_time - start_time:.2f} seconds")
        print(f"Best move: {best_move}, Score: {best_score}")
        
        return best_move
    
    def minimax(self, board: ChessBoard, depth: int, alpha: float, beta: float, 
                maximizing_player: bool) -> Tuple[Optional[Move], float]:
        """Minimax algorithm with alpha-beta pruning"""
        self.nodes_evaluated += 1
        
        if depth == 0 or self.is_game_over(board):
            return None, self.evaluate_position(board)
        
        move_generator = MoveGenerator(board)
        moves = move_generator.generate_all_moves(board.current_player)
        
        if not moves:
            # No legal moves - checkmate or stalemate
            if board.is_in_check(board.current_player):
                # Checkmate - return very negative score for current player
                return None, -10000 + (self.max_depth - depth)
            else:
                # Stalemate
                return None, 0
        
        # Sort moves for better alpha-beta pruning
        moves = self.order_moves(board, moves)
        
        best_move = None
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in moves:
                new_board = self.make_move(board, move)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = self.make_move(board, move)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return best_move, min_eval
    
    def evaluate_position(self, board: ChessBoard) -> float:
        """Evaluate the current position"""
        if board.is_in_check(Color.WHITE):
            white_moves = MoveGenerator(board).generate_all_moves(Color.WHITE)
            if not white_moves:
                return -10000  # White is checkmated
        
        if board.is_in_check(Color.BLACK):
            black_moves = MoveGenerator(board).generate_all_moves(Color.BLACK)
            if not black_moves:
                return 10000  # Black is checkmated
        
        score = 0
        
        # Material and positional evaluation
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_score = self.evaluate_piece(piece, row, col)
                    if piece.color == Color.WHITE:
                        score += piece_score
                    else:
                        score -= piece_score
        
        # Mobility bonus
        white_moves = len(MoveGenerator(board).generate_all_moves(Color.WHITE))
        black_moves = len(MoveGenerator(board).generate_all_moves(Color.BLACK))
        score += (white_moves - black_moves) * 0.1
        
        # King safety
        score += self.evaluate_king_safety(board, Color.WHITE)
        score -= self.evaluate_king_safety(board, Color.BLACK)
        
        return score if board.current_player == Color.WHITE else -score
    
    def evaluate_piece(self, piece: Piece, row: int, col: int) -> float:
        """Evaluate a single piece"""
        base_value = self.piece_values[piece.type]
        
        # Adjust for piece color (flip table for black pieces)
        eval_row = row if piece.color == Color.WHITE else 7 - row
        
        positional_bonus = 0
        if piece.type == PieceType.PAWN:
            positional_bonus = self.pawn_table[eval_row][col]
        elif piece.type == PieceType.KNIGHT:
            positional_bonus = self.knight_table[eval_row][col]
        elif piece.type == PieceType.BISHOP:
            positional_bonus = self.bishop_table[eval_row][col]
        elif piece.type == PieceType.ROOK:
            positional_bonus = self.rook_table[eval_row][col]
        elif piece.type == PieceType.QUEEN:
            positional_bonus = self.queen_table[eval_row][col]
        elif piece.type == PieceType.KING:
            positional_bonus = self.king_middle_game_table[eval_row][col]
        
        return base_value + positional_bonus
    
    def evaluate_king_safety(self, board: ChessBoard, color: Color) -> float:
        """Evaluate king safety"""
        king_pos = board.king_positions[color]
        safety_score = 0
        
        # Penalty for king in center during middle game
        if 2 <= king_pos[0] <= 5 and 2 <= king_pos[1] <= 5:
            safety_score -= 50
        
        # Bonus for castling
        king = board.get_piece(king_pos[0], king_pos[1])
        if king and king.has_moved:
            safety_score -= 30
        
        return safety_score
    
    def order_moves(self, board: ChessBoard, moves: List[Move]) -> List[Move]:
        """Order moves for better alpha-beta pruning"""
        def move_priority(move):
            score = 0
            
            # Prioritize captures
            target_piece = board.get_piece(move.to_pos[0], move.to_pos[1])
            if target_piece:
                moving_piece = board.get_piece(move.from_pos[0], move.from_pos[1])
                # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
                score += self.piece_values[target_piece.type] - self.piece_values[moving_piece.type] // 10
            
            # Prioritize promotions
            if move.promotion:
                score += self.piece_values[move.promotion]
            
            # Prioritize center moves
            center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
            if move.to_pos in center_squares:
                score += 10
            
            return score
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def make_move(self, board: ChessBoard, move: Move) -> ChessBoard:
        """Make a move and return new board state"""
        new_board = board.copy()
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        piece = new_board.get_piece(from_row, from_col)
        if not piece:
            return new_board
        
        # Handle special moves
        if move.is_castling:
            # Move king
            new_board.set_piece(to_row, to_col, piece)
            new_board.set_piece(from_row, from_col, None)
            piece.has_moved = True
            
            # Move rook
            if to_col > from_col:  # Kingside
                rook = new_board.get_piece(to_row, 7)
                if rook:
                    new_board.set_piece(to_row, 5, rook)
                    new_board.set_piece(to_row, 7, None)
                    rook.has_moved = True
            else:  # Queenside
                rook = new_board.get_piece(to_row, 0)
                if rook:
                    new_board.set_piece(to_row, 3, rook)
                    new_board.set_piece(to_row, 0, None)
                    rook.has_moved = True
        
        elif move.is_en_passant:
            # Move pawn
            new_board.set_piece(to_row, to_col, piece)
            new_board.set_piece(from_row, from_col, None)
            # Remove captured pawn
            new_board.set_piece(from_row, to_col, None)
        
        else:
            # Regular move
            if move.promotion:
                promoted_piece = Piece(move.promotion, piece.color)
                promoted_piece.has_moved = True
                new_board.set_piece(to_row, to_col, promoted_piece)
            else:
                new_board.set_piece(to_row, to_col, piece)
            new_board.set_piece(from_row, from_col, None)
            piece.has_moved = True
        
        # Update en passant target
        new_board.en_passant_target = None
        if (piece.type == PieceType.PAWN and abs(to_row - from_row) == 2):
            new_board.en_passant_target = ((from_row + to_row) // 2, from_col)
        
        # Switch current player
        new_board.current_player = Color.BLACK if new_board.current_player == Color.WHITE else Color.WHITE
        
        # Update move counters
        if piece.type == PieceType.PAWN or new_board.get_piece(to_row, to_col):
            new_board.halfmove_clock = 0
        else:
            new_board.halfmove_clock += 1
        
        if new_board.current_player == Color.WHITE:
            new_board.fullmove_number += 1
        
        return new_board
    
    def is_game_over(self, board: ChessBoard) -> bool:
        """Check if game is over"""
        move_generator = MoveGenerator(board)
        moves = move_generator.generate_all_moves(board.current_player)
        
        if not moves:
            return True  # Checkmate or stalemate
        
        # Check for insufficient material
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.type != PieceType.KING:
                    pieces.append(piece.type)
        
        if len(pieces) == 0:
            return True  # King vs King
        
        if len(pieces) == 1 and pieces[0] in [PieceType.BISHOP, PieceType.KNIGHT]:
            return True  # King + minor piece vs King
        
        return False
