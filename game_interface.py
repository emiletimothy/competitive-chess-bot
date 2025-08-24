"""
Chess Game Interface - Command Line Interface for playing against the bot
"""

import sys
from typing import Optional, Tuple
from chess_board import ChessBoard, Move, Color, PieceType
from move_generator import MoveGenerator
from chess_engine import ChessEngine

class ChessGame:
    def __init__(self, engine_depth: int = 4):
        self.board = ChessBoard()
        self.engine = ChessEngine(max_depth=engine_depth)
        self.move_generator = MoveGenerator(self.board)
        self.human_color = Color.WHITE
        self.engine_color = Color.BLACK
    
    def play(self):
        """Main game loop"""
        print("Welcome to Chess Bot!")
        print("You are playing as White. Enter moves in algebraic notation (e.g., e2e4)")
        print("Type 'quit' to exit, 'help' for commands")
        print()
        
        self.display_board()
        
        while not self.is_game_over():
            if self.board.current_player == self.human_color:
                self.handle_human_move()
            else:
                self.handle_engine_move()
            
            self.display_board()
        
        self.display_game_result()
    
    def display_board(self):
        """Display the current board state"""
        print("\n" + str(self.board))
        print(f"\nCurrent player: {'White' if self.board.current_player == Color.WHITE else 'Black'}")
        
        if self.board.is_in_check(self.board.current_player):
            print("CHECK!")
    
    def handle_human_move(self):
        """Handle human player input"""
        while True:
            try:
                user_input = input("\nEnter your move: ").strip().lower()
                
                if user_input == 'quit':
                    print("Thanks for playing!")
                    sys.exit(0)
                elif user_input == 'help':
                    self.display_help()
                    continue
                elif user_input == 'moves':
                    self.display_legal_moves()
                    continue
                
                move = self.parse_move(user_input)
                if move and self.is_legal_move(move):
                    self.make_move(move)
                    break
                else:
                    print("Invalid move! Try again.")
                    
            except KeyboardInterrupt:
                print("\nThanks for playing!")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}. Try again.")
    
    def handle_engine_move(self):
        """Handle engine move"""
        print("\nEngine is thinking...")
        move = self.engine.get_best_move(self.board)
        
        if move:
            print(f"Engine plays: {move}")
            self.make_move(move)
        else:
            print("Engine has no legal moves!")
    
    def parse_move(self, move_str: str) -> Optional[Move]:
        """Parse move string into Move object"""
        move_str = move_str.replace(" ", "")
        
        if len(move_str) < 4:
            return None
        
        try:
            # Parse from and to positions
            from_col = ord(move_str[0]) - ord('a')
            from_row = 8 - int(move_str[1])
            to_col = ord(move_str[2]) - ord('a')
            to_row = 8 - int(move_str[3])
            
            if not (0 <= from_row < 8 and 0 <= from_col < 8 and 
                   0 <= to_row < 8 and 0 <= to_col < 8):
                return None
            
            # Check for promotion
            promotion = None
            if len(move_str) == 5:
                promotion_char = move_str[4].lower()
                promotion_map = {
                    'q': PieceType.QUEEN,
                    'r': PieceType.ROOK,
                    'b': PieceType.BISHOP,
                    'n': PieceType.KNIGHT
                }
                promotion = promotion_map.get(promotion_char)
            
            # Detect special moves automatically
            piece = self.board.get_piece(from_row, from_col)
            if not piece:
                return None
            
            is_castling = False
            is_en_passant = False
            
            # Check for castling (king moving 2 squares)
            if piece.type == PieceType.KING and abs(to_col - from_col) == 2:
                is_castling = True
            
            # Check for en passant (pawn diagonal move to empty square)
            if (piece.type == PieceType.PAWN and 
                abs(to_col - from_col) == 1 and 
                not self.board.get_piece(to_row, to_col) and
                self.board.en_passant_target == (to_row, to_col)):
                is_en_passant = True
            
            return Move((from_row, from_col), (to_row, to_col), 
                       promotion=promotion, is_castling=is_castling, 
                       is_en_passant=is_en_passant)
            
        except (ValueError, IndexError):
            return None
    
    def is_legal_move(self, move: Move) -> bool:
        """Check if move is legal"""
        self.move_generator = MoveGenerator(self.board)
        legal_moves = self.move_generator.generate_all_moves(self.board.current_player)
        return move in legal_moves
    
    def make_move(self, move: Move):
        """Make a move on the board"""
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
        
        # Add move to history
        self.board.move_history.append(move)
        
        # Switch current player
        self.board.current_player = Color.BLACK if self.board.current_player == Color.WHITE else Color.WHITE
        
        # Update move counters
        captured_piece = self.board.get_piece(to_row, to_col)
        if piece.type == PieceType.PAWN or captured_piece:
            self.board.halfmove_clock = 0
        else:
            self.board.halfmove_clock += 1
        
        if self.board.current_player == Color.WHITE:
            self.board.fullmove_number += 1
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        self.move_generator = MoveGenerator(self.board)
        moves = self.move_generator.generate_all_moves(self.board.current_player)
        
        if not moves:
            return True  # Checkmate or stalemate
        
        # Check for 50-move rule
        if self.board.halfmove_clock >= 100:
            return True
        
        # Check for insufficient material
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.type != PieceType.KING:
                    pieces.append(piece.type)
        
        if len(pieces) == 0:
            return True  # King vs King
        
        if len(pieces) == 1 and pieces[0] in [PieceType.BISHOP, PieceType.KNIGHT]:
            return True  # King + minor piece vs King
        
        return False
    
    def display_game_result(self):
        """Display the final game result"""
        self.move_generator = MoveGenerator(self.board)
        moves = self.move_generator.generate_all_moves(self.board.current_player)
        
        if not moves:
            if self.board.is_in_check(self.board.current_player):
                winner = "Black" if self.board.current_player == Color.WHITE else "White"
                print(f"\nCheckmate! {winner} wins!")
            else:
                print("\nStalemate! It's a draw!")
        elif self.board.halfmove_clock >= 100:
            print("\nDraw by 50-move rule!")
        else:
            print("\nDraw by insufficient material!")
    
    def display_help(self):
        """Display help information"""
        print("\nCommands:")
        print("  - Enter moves in format: e2e4 (from e2 to e4)")
        print("  - For promotion, add piece: e7e8q (promote to queen)")
        print("  - 'moves' - show all legal moves")
        print("  - 'help' - show this help")
        print("  - 'quit' - exit game")
    
    def display_legal_moves(self):
        """Display all legal moves for current player"""
        self.move_generator = MoveGenerator(self.board)
        moves = self.move_generator.generate_all_moves(self.board.current_player)
        
        if not moves:
            print("No legal moves available!")
            return
        
        print(f"\nLegal moves for {'White' if self.board.current_player == Color.WHITE else 'Black'}:")
        move_strs = [str(move) for move in moves]
        move_strs.sort()
        
        for i, move_str in enumerate(move_strs):
            print(f"{move_str:6}", end="  ")
            if (i + 1) % 8 == 0:
                print()
        print()

def main():
    """Main function to start the game"""
    print("Chess Bot - Competitive Chess AI")
    print("=" * 40)
    
    try:
        difficulty = input("Choose difficulty (1-5, default 4): ").strip()
        if difficulty.isdigit() and 1 <= int(difficulty) <= 5:
            depth = int(difficulty) + 1
        else:
            depth = 4
        
        color_choice = input("Play as (w)hite or (b)lack? (default white): ").strip().lower()
        
        game = ChessGame(engine_depth=depth)
        
        if color_choice.startswith('b'):
            game.human_color = Color.BLACK
            game.engine_color = Color.WHITE
        
        game.play()
        
    except KeyboardInterrupt:
        print("\nThanks for playing!")

if __name__ == "__main__":
    main()
