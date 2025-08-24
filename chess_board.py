"""
Chess Board Representation and Game Logic
"""

import copy
from enum import Enum
from typing import List, Tuple, Optional, Dict

class PieceType(Enum):
    PAWN = 1
    ROOK = 2
    KNIGHT = 3
    BISHOP = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 1
    BLACK = -1

class Piece:
    def __init__(self, piece_type: PieceType, color: Color):
        self.type = piece_type
        self.color = color
        self.has_moved = False
    
    def __str__(self):
        symbols = {
            (PieceType.PAWN, Color.WHITE): '♟',
            (PieceType.ROOK, Color.WHITE): '♜',
            (PieceType.KNIGHT, Color.WHITE): '♞',
            (PieceType.BISHOP, Color.WHITE): '♝',
            (PieceType.QUEEN, Color.WHITE): '♛',
            (PieceType.KING, Color.WHITE): '♚',
            (PieceType.PAWN, Color.BLACK): '♟',
            (PieceType.ROOK, Color.BLACK): '♜',
            (PieceType.KNIGHT, Color.BLACK): '♞',
            (PieceType.BISHOP, Color.BLACK): '♝',
            (PieceType.QUEEN, Color.BLACK): '♛',
            (PieceType.KING, Color.BLACK): '♚',
        }
        return symbols.get((self.type, self.color), '?')
    
    def copy(self):
        new_piece = Piece(self.type, self.color)
        new_piece.has_moved = self.has_moved
        return new_piece

class Move:
    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                 promotion: Optional[PieceType] = None, is_castling: bool = False,
                 is_en_passant: bool = False):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.promotion = promotion
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
    
    def __str__(self):
        def pos_to_algebraic(pos):
            return chr(ord('a') + pos[1]) + str(8 - pos[0])
        
        result = pos_to_algebraic(self.from_pos) + pos_to_algebraic(self.to_pos)
        if self.promotion:
            result += self.promotion.name.lower()
        return result
    
    def __eq__(self, other):
        return (self.from_pos == other.from_pos and 
                self.to_pos == other.to_pos and
                self.promotion == other.promotion and
                self.is_castling == other.is_castling and
                self.is_en_passant == other.is_en_passant)

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = Color.WHITE
        self.move_history = []
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.king_positions = {Color.WHITE: (7, 4), Color.BLACK: (0, 4)}
        self._setup_initial_position()
    
    def _setup_initial_position(self):
        """Set up the standard chess starting position"""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE)
        
        # Place other pieces
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, 
                      PieceType.QUEEN, PieceType.KING, PieceType.BISHOP, 
                      PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            self.board[0][col] = Piece(piece_order[col], Color.BLACK)
            self.board[7][col] = Piece(piece_order[col], Color.WHITE)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at given position"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            if piece and piece.type == PieceType.KING:
                self.king_positions[piece.color] = (row, col)
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def is_square_attacked(self, row: int, col: int, by_color: Color) -> bool:
        """Check if a square is attacked by pieces of given color"""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == by_color:
                    if self._can_piece_attack_square(r, c, row, col):
                        return True
        return False
    
    def _can_piece_attack_square(self, piece_row: int, piece_col: int, 
                                target_row: int, target_col: int) -> bool:
        """Check if piece can attack target square (ignoring check rules)"""
        piece = self.board[piece_row][piece_col]
        if not piece:
            return False
        
        row_diff = target_row - piece_row
        col_diff = target_col - piece_col
        
        if piece.type == PieceType.PAWN:
            direction = 1 if piece.color == Color.BLACK else -1
            # Pawn attacks diagonally
            return (row_diff == direction and abs(col_diff) == 1)
        
        elif piece.type == PieceType.ROOK:
            return self._is_clear_path(piece_row, piece_col, target_row, target_col, 'straight')
        
        elif piece.type == PieceType.BISHOP:
            return self._is_clear_path(piece_row, piece_col, target_row, target_col, 'diagonal')
        
        elif piece.type == PieceType.QUEEN:
            return (self._is_clear_path(piece_row, piece_col, target_row, target_col, 'straight') or
                   self._is_clear_path(piece_row, piece_col, target_row, target_col, 'diagonal'))
        
        elif piece.type == PieceType.KNIGHT:
            return (abs(row_diff) == 2 and abs(col_diff) == 1) or (abs(row_diff) == 1 and abs(col_diff) == 2)
        
        elif piece.type == PieceType.KING:
            return abs(row_diff) <= 1 and abs(col_diff) <= 1 and (row_diff != 0 or col_diff != 0)
        
        return False
    
    def _is_clear_path(self, from_row: int, from_col: int, to_row: int, to_col: int, path_type: str) -> bool:
        """Check if path between two squares is clear"""
        row_diff = to_row - from_row
        col_diff = to_col - from_col

        if path_type == 'straight':
            if row_diff != 0 and col_diff != 0:
                return False
        elif path_type == 'diagonal':
            if abs(row_diff) != abs(col_diff):
                return False

        if row_diff == 0 and col_diff == 0:
            return False

        # Calculate step direction
        row_step = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
        
        # Check each square in the path
        current_row, current_col = from_row + row_step, from_col + col_step
        while (current_row, current_col) != (to_row, to_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += row_step
            current_col += col_step
        
        return True
    
    def is_in_check(self, color: Color) -> bool:
        """Check if king of given color is in check"""
        king_pos = self.king_positions[color]
        return self.is_square_attacked(king_pos[0], king_pos[1], Color.WHITE if color == Color.BLACK else Color.BLACK)
    
    def copy(self):
        """Create a deep copy of the board"""
        new_board = ChessBoard()
        new_board.board = [[piece.copy() if piece else None for piece in row] for row in self.board]
        new_board.current_player = self.current_player
        new_board.move_history = self.move_history.copy()
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.king_positions = self.king_positions.copy()
        return new_board
    
    def __str__(self):
        """String representation of the board"""
        result = "  a b c d e f g h\n"
        for row in range(8):
            result += f"{8-row} "
            for col in range(8):
                piece = self.board[row][col]
                result += (str(piece) if piece else '·') + " "
            result += f"{8-row}\n"
        result += "  a b c d e f g h"
        return result
