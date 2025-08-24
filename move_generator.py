"""
Chess Move Generation and Validation
"""

from typing import List, Tuple, Optional
from chess_board import ChessBoard, Move, Piece, PieceType, Color

class MoveGenerator:
    def __init__(self, board: ChessBoard):
        self.board = board
    
    def generate_all_moves(self, color: Color) -> List[Move]:
        """Generate all legal moves for given color"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == color:
                    moves.extend(self.generate_piece_moves(row, col))
        return moves
    
    def generate_piece_moves(self, row: int, col: int) -> List[Move]:
        """Generate all legal moves for piece at given position"""
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        
        pseudo_legal_moves = self._generate_pseudo_legal_moves(row, col)
        legal_moves = []
        
        for move in pseudo_legal_moves:
            if self.is_legal_move(move):
                legal_moves.append(move)
        
        return legal_moves
    
    def _generate_pseudo_legal_moves(self, row: int, col: int) -> List[Move]:
        """Generate pseudo-legal moves (may leave king in check)"""
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        
        if piece.type == PieceType.PAWN:
            return self._generate_pawn_moves(row, col)
        elif piece.type == PieceType.ROOK:
            return self._generate_rook_moves(row, col)
        elif piece.type == PieceType.KNIGHT:
            return self._generate_knight_moves(row, col)
        elif piece.type == PieceType.BISHOP:
            return self._generate_bishop_moves(row, col)
        elif piece.type == PieceType.QUEEN:
            return self._generate_queen_moves(row, col)
        elif piece.type == PieceType.KING:
            return self._generate_king_moves(row, col)
        
        return []
    
    def _generate_pawn_moves(self, row: int, col: int) -> List[Move]:
        """Generate pawn moves"""
        moves = []
        piece = self.board.get_piece(row, col)
        direction = -1 if piece.color == Color.WHITE else 1
        start_row = 6 if piece.color == Color.WHITE else 1
        promotion_row = 0 if piece.color == Color.WHITE else 7
        
        # Forward moves
        new_row = row + direction
        if self.board.is_valid_position(new_row, col) and not self.board.get_piece(new_row, col):
            if new_row == promotion_row:
                # Promotion
                for promotion_piece in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move((row, col), (new_row, col), promotion=promotion_piece))
            else:
                moves.append(Move((row, col), (new_row, col)))
                
                # Double move from starting position
                if row == start_row and not self.board.get_piece(new_row + direction, col):
                    moves.append(Move((row, col), (new_row + direction, col)))
        
        # Captures
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            if self.board.is_valid_position(new_row, new_col):
                target_piece = self.board.get_piece(new_row, new_col)
                if target_piece and target_piece.color != piece.color:
                    if new_row == promotion_row:
                        # Promotion capture
                        for promotion_piece in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move((row, col), (new_row, new_col), promotion=promotion_piece))
                    else:
                        moves.append(Move((row, col), (new_row, new_col)))
                
                # En passant
                elif (self.board.en_passant_target and 
                      self.board.en_passant_target == (new_row, new_col)):
                    moves.append(Move((row, col), (new_row, new_col), is_en_passant=True))
        
        return moves
    
    def _generate_rook_moves(self, row: int, col: int) -> List[Move]:
        """Generate rook moves"""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for row_dir, col_dir in directions:
            for distance in range(1, 8):
                new_row = row + row_dir * distance
                new_col = col + col_dir * distance
                
                if not self.board.is_valid_position(new_row, new_col):
                    break
                
                target_piece = self.board.get_piece(new_row, new_col)
                if target_piece:
                    if target_piece.color != self.board.get_piece(row, col).color:
                        moves.append(Move((row, col), (new_row, new_col)))
                    break
                else:
                    moves.append(Move((row, col), (new_row, new_col)))
        
        return moves
    
    def _generate_knight_moves(self, row: int, col: int) -> List[Move]:
        """Generate knight moves"""
        moves = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), 
                       (1, 2), (1, -2), (-1, 2), (-1, -2)]
        
        piece = self.board.get_piece(row, col)
        for row_offset, col_offset in knight_moves:
            new_row = row + row_offset
            new_col = col + col_offset
            
            if self.board.is_valid_position(new_row, new_col):
                target_piece = self.board.get_piece(new_row, new_col)
                if not target_piece or target_piece.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col)))
        
        return moves
    
    def _generate_bishop_moves(self, row: int, col: int) -> List[Move]:
        """Generate bishop moves"""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for row_dir, col_dir in directions:
            for distance in range(1, 8):
                new_row = row + row_dir * distance
                new_col = col + col_dir * distance
                
                if not self.board.is_valid_position(new_row, new_col):
                    break
                
                target_piece = self.board.get_piece(new_row, new_col)
                if target_piece:
                    if target_piece.color != self.board.get_piece(row, col).color:
                        moves.append(Move((row, col), (new_row, new_col)))
                    break
                else:
                    moves.append(Move((row, col), (new_row, new_col)))
        
        return moves
    
    def _generate_queen_moves(self, row: int, col: int) -> List[Move]:
        """Generate queen moves (combination of rook and bishop)"""
        return self._generate_rook_moves(row, col) + self._generate_bishop_moves(row, col)
    
    def _generate_king_moves(self, row: int, col: int) -> List[Move]:
        """Generate king moves"""
        moves = []
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), 
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        piece = self.board.get_piece(row, col)
        for row_offset, col_offset in king_moves:
            new_row = row + row_offset
            new_col = col + col_offset
            
            if self.board.is_valid_position(new_row, new_col):
                target_piece = self.board.get_piece(new_row, new_col)
                if not target_piece or target_piece.color != piece.color:
                    moves.append(Move((row, col), (new_row, new_col)))
        
        # Castling
        if not piece.has_moved and not self.board.is_in_check(piece.color):
            # Kingside castling
            if self._can_castle_kingside(piece.color):
                moves.append(Move((row, col), (row, col + 2), is_castling=True))
            
            # Queenside castling
            if self._can_castle_queenside(piece.color):
                moves.append(Move((row, col), (row, col - 2), is_castling=True))
        
        return moves
    
    def _can_castle_kingside(self, color: Color) -> bool:
        """Check if kingside castling is possible"""
        king_row = 7 if color == Color.WHITE else 0
        rook = self.board.get_piece(king_row, 7)
        
        if not rook or rook.type != PieceType.ROOK or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty and not attacked
        for col in range(5, 7):
            if (self.board.get_piece(king_row, col) or 
                self.board.is_square_attacked(king_row, col, Color.WHITE if color == Color.BLACK else Color.BLACK)):
                return False
        
        return True
    
    def _can_castle_queenside(self, color: Color) -> bool:
        """Check if queenside castling is possible"""
        king_row = 7 if color == Color.WHITE else 0
        rook = self.board.get_piece(king_row, 0)
        
        if not rook or rook.type != PieceType.ROOK or rook.has_moved:
            return False
        
        # Check if squares between king and rook are empty
        for col in range(1, 4):
            if self.board.get_piece(king_row, col):
                return False
        
        # Check if king's path is not attacked
        for col in range(2, 4):
            if self.board.is_square_attacked(king_row, col, Color.WHITE if color == Color.BLACK else Color.BLACK):
                return False
        
        return True
    
    def is_legal_move(self, move: Move) -> bool:
        """Check if a move is legal (doesn't leave king in check)"""
        # Make the move temporarily
        temp_board = self.board.copy()
        self._make_move_on_board(temp_board, move)
        
        # Check if king is in check after the move
        moving_piece = self.board.get_piece(move.from_pos[0], move.from_pos[1])
        return not temp_board.is_in_check(moving_piece.color)
    
    def _make_move_on_board(self, board: ChessBoard, move: Move):
        """Make a move on the given board (helper for legal move checking)"""
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        
        piece = board.get_piece(from_row, from_col)
        if not piece:
            return
        
        # Handle special moves
        if move.is_castling:
            # Move king
            board.set_piece(to_row, to_col, piece)
            board.set_piece(from_row, from_col, None)
            
            # Move rook
            if to_col > from_col:  # Kingside
                rook = board.get_piece(to_row, 7)
                board.set_piece(to_row, 5, rook)
                board.set_piece(to_row, 7, None)
            else:  # Queenside
                rook = board.get_piece(to_row, 0)
                board.set_piece(to_row, 3, rook)
                board.set_piece(to_row, 0, None)
        
        elif move.is_en_passant:
            # Move pawn
            board.set_piece(to_row, to_col, piece)
            board.set_piece(from_row, from_col, None)
            # Remove captured pawn
            board.set_piece(from_row, to_col, None)
        
        else:
            # Regular move
            if move.promotion:
                promoted_piece = Piece(move.promotion, piece.color)
                board.set_piece(to_row, to_col, promoted_piece)
            else:
                board.set_piece(to_row, to_col, piece)
            board.set_piece(from_row, from_col, None)
        
        # Update piece moved status
        if piece.type == PieceType.KING or piece.type == PieceType.ROOK:
            piece.has_moved = True
