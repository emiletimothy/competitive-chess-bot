// Chess Bot Drag & Drop Interface JavaScript

class ChessGame {
    constructor() {
        this.gameId = null;
        this.boardState = null;
        this.selectedSquare = null;
        this.legalMoves = [];
        this.isPlayerTurn = true;
        this.moveHistory = [];
        this.capturedPieces = { white: [], black: [] };
        this.pendingPromotion = null;
        
        this.initializeBoard();
        this.bindEvents();
    }
    
    initializeBoard() {
        const board = document.getElementById('chess-board');
        board.innerHTML = '';
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = `square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
                square.dataset.row = row;
                square.dataset.col = col;
                
                board.appendChild(square);
            }
        }
    }
    
    bindEvents() {
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.startNewGame();
        });
        
        document.getElementById('new-game-modal-btn').addEventListener('click', () => {
            this.hideModal('game-over-modal');
            this.startNewGame();
        });
        
        // Board click events
        document.getElementById('chess-board').addEventListener('click', (e) => {
            if (e.target.classList.contains('square') || e.target.classList.contains('piece')) {
                const square = e.target.classList.contains('square') ? e.target : e.target.parentElement;
                this.handleSquareClick(square);
            }
        });
        
        // Drag and drop events
        document.getElementById('chess-board').addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('piece')) {
                this.handleDragStart(e);
            }
        });
        
        document.getElementById('chess-board').addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        document.getElementById('chess-board').addEventListener('dragenter', (e) => {
            if (e.target.classList.contains('square')) {
                e.target.classList.add('drag-over');
            }
        });
        
        document.getElementById('chess-board').addEventListener('dragleave', (e) => {
            if (e.target.classList.contains('square')) {
                e.target.classList.remove('drag-over');
            }
        });
        
        document.getElementById('chess-board').addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.target.classList.contains('square')) {
                e.target.classList.remove('drag-over');
                this.handleDrop(e);
            }
        });
        
        // Promotion modal events
        document.querySelectorAll('.promotion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handlePromotion(e.target.dataset.piece);
            });
        });
    }
    
    async startNewGame() {
        const difficulty = document.getElementById('difficulty-select').value;
        const color = document.getElementById('color-select').value;
        
        try {
            const response = await fetch('/api/new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    difficulty: parseInt(difficulty),
                    color: color
                })
            });
            
            const data = await response.json();
            this.gameId = data.game_id;
            this.boardState = data.board_state;
            this.moveHistory = [];
            this.capturedPieces = { white: [], black: [] };
            
            this.updateBoard();
            this.updateGameStatus();
            this.clearMoveHistory();
            this.clearCapturedPieces();
            
            // Handle engine first move if playing as black
            if (data.engine_move && data.engine_move.success) {
                this.addMoveToHistory(data.engine_move.move, 'black');
            }
            
        } catch (error) {
            console.error('Error starting new game:', error);
            this.showStatus('Error starting new game', 'error');
        }
    }
    
    updateBoard() {
        if (!this.boardState) return;
        
        const squares = document.querySelectorAll('.square');
        squares.forEach(square => {
            const row = parseInt(square.dataset.row);
            const col = parseInt(square.dataset.col);
            const piece = this.boardState.board[row][col];
            
            // Clear existing piece
            const existingPiece = square.querySelector('.piece');
            if (existingPiece) {
                existingPiece.remove();
            }
            
            // Add piece if exists
            if (piece) {
                const pieceElement = document.createElement('div');
                pieceElement.className = 'piece';
                pieceElement.textContent = piece.symbol;
                pieceElement.draggable = this.isPlayerTurn && this.canMovePiece(piece);
                pieceElement.dataset.type = piece.type;
                pieceElement.dataset.color = piece.color;
                square.appendChild(pieceElement);
            }
        });
    }
    
    canMovePiece(piece) {
        if (!this.boardState) return false;
        const currentPlayerColor = this.boardState.current_player;
        return piece.color === currentPlayerColor && this.isPlayerTurn;
    }
    
    async handleSquareClick(square) {
        if (!this.isPlayerTurn || !this.gameId) return;
        
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        
        // If clicking on selected square, deselect
        if (this.selectedSquare && 
            this.selectedSquare.row === row && 
            this.selectedSquare.col === col) {
            this.clearSelection();
            return;
        }
        
        // If clicking on a legal move, make the move
        if (this.selectedSquare && this.isLegalMove(row, col)) {
            await this.makeMove(this.selectedSquare.row, this.selectedSquare.col, row, col);
            return;
        }
        
        // Select piece if it belongs to current player
        const piece = this.boardState.board[row][col];
        if (piece && this.canMovePiece(piece)) {
            await this.selectSquare(row, col);
        } else {
            this.clearSelection();
        }
    }
    
    async selectSquare(row, col) {
        this.clearSelection();
        
        this.selectedSquare = { row, col };
        
        // Highlight selected square
        const square = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        square.classList.add('selected');
        
        // Get and show legal moves
        try {
            const response = await fetch(`/api/legal_moves/${this.gameId}/${row}/${col}`);
            const data = await response.json();
            this.legalMoves = data.legal_moves || [];
            this.showLegalMoves();
        } catch (error) {
            console.error('Error getting legal moves:', error);
        }
    }
    
    clearSelection() {
        // Clear selected square
        document.querySelectorAll('.square.selected').forEach(sq => {
            sq.classList.remove('selected');
        });
        
        // Clear legal move indicators
        document.querySelectorAll('.square.legal-move, .square.legal-capture').forEach(sq => {
            sq.classList.remove('legal-move', 'legal-capture');
        });
        
        this.selectedSquare = null;
        this.legalMoves = [];
    }
    
    showLegalMoves() {
        this.legalMoves.forEach(move => {
            const square = document.querySelector(`[data-row="${move.row}"][data-col="${move.col}"]`);
            if (square) {
                if (move.is_capture) {
                    square.classList.add('legal-capture');
                } else {
                    square.classList.add('legal-move');
                }
            }
        });
    }
    
    isLegalMove(row, col) {
        return this.legalMoves.some(move => move.row === row && move.col === col);
    }
    
    handleDragStart(e) {
        const square = e.target.parentElement;
        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);
        
        e.dataTransfer.setData('text/plain', JSON.stringify({ row, col }));
        e.target.classList.add('dragging');
        
        // Select the piece being dragged
        this.selectSquare(row, col);
    }
    
    async handleDrop(e) {
        const dropSquare = e.target;
        const dropRow = parseInt(dropSquare.dataset.row);
        const dropCol = parseInt(dropSquare.dataset.col);
        
        try {
            const dragData = JSON.parse(e.dataTransfer.getData('text/plain'));
            const { row: fromRow, col: fromCol } = dragData;
            
            // Clear dragging state
            document.querySelectorAll('.piece.dragging').forEach(piece => {
                piece.classList.remove('dragging');
            });
            
            // Make move if legal
            if (this.isLegalMove(dropRow, dropCol)) {
                await this.makeMove(fromRow, fromCol, dropRow, dropCol);
            } else {
                this.clearSelection();
            }
        } catch (error) {
            console.error('Error handling drop:', error);
        }
    }
    
    async makeMove(fromRow, fromCol, toRow, toCol, promotion = null) {
        if (!this.gameId) return;
        
        // Check if pawn promotion is needed
        const piece = this.boardState.board[fromRow][fromCol];
        if (piece && piece.type === 'pawn' && 
            ((piece.color === 'white' && toRow === 0) || 
             (piece.color === 'black' && toRow === 7))) {
            if (!promotion) {
                this.pendingPromotion = { fromRow, fromCol, toRow, toCol };
                this.showModal('promotion-modal');
                return;
            }
        }
        
        // Optimistic UI update - immediately move the piece visually
        const movingPiece = this.boardState.board[fromRow][fromCol];
        this.boardState.board[toRow][toCol] = movingPiece;
        this.boardState.board[fromRow][fromCol] = null;
        this.updateBoard();
        this.clearSelection();
        
        // Add move to history immediately
        this.addMoveToHistory({ from: { row: fromRow, col: fromCol }, to: { row: toRow, col: toCol } }, 
            this.boardState.current_player);
        
        try {
            this.isPlayerTurn = false;
            
            const response = await fetch(`/api/make_move/${this.gameId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from: { row: fromRow, col: fromCol },
                    to: { row: toRow, col: toCol },
                    promotion: promotion
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update to server board state (after human move, before engine move)
                this.boardState = data.board_state;
                this.updateGameStatus();
                
                // Show engine thinking and handle engine move
                if (data.engine_move && data.engine_move.success) {
                    this.showEngineThinking();
                    
                    setTimeout(() => {
                        this.addMoveToHistory(data.engine_move.move, 
                            this.boardState.current_player === 'white' ? 'black' : 'white');
                        this.boardState = data.board_state;
                        this.updateBoard();
                        this.updateGameStatus();
                        this.hideEngineThinking();
                        this.isPlayerTurn = true;
                    }, 800);
                } else {
                    this.isPlayerTurn = true;
                }
                
                // Check for game over
                if (this.boardState.game_over) {
                    this.handleGameOver();
                }
            } else {
                // Revert optimistic update on error
                this.boardState.board[fromRow][fromCol] = movingPiece;
                this.boardState.board[toRow][toCol] = null;
                this.updateBoard();
                this.showStatus('Invalid move', 'error');
                this.isPlayerTurn = true;
                // Remove the move from history
                this.moveHistory.pop();
                this.updateMoveHistory();
            }
            
        } catch (error) {
            console.error('Error making move:', error);
            // Revert optimistic update on error
            this.boardState.board[fromRow][fromCol] = movingPiece;
            this.boardState.board[toRow][toCol] = null;
            this.updateBoard();
            this.showStatus('Error making move', 'error');
            this.isPlayerTurn = true;
            // Remove the move from history
            this.moveHistory.pop();
            this.updateMoveHistory();
        }
    }
    
    handlePromotion(pieceType) {
        this.hideModal('promotion-modal');
        
        if (this.pendingPromotion) {
            const { fromRow, fromCol, toRow, toCol } = this.pendingPromotion;
            this.pendingPromotion = null;
            this.makeMove(fromRow, fromCol, toRow, toCol, pieceType);
        }
    }
    
    updateGameStatus() {
        if (!this.boardState) return;
        
        const playerIndicator = document.getElementById('player-indicator');
        const statusText = document.getElementById('status-text');
        
        playerIndicator.textContent = this.boardState.current_player === 'white' ? 'White' : 'Black';
        playerIndicator.className = `player ${this.boardState.current_player}`;
        
        if (this.boardState.game_over) {
            if (this.boardState.winner === 'draw') {
                statusText.textContent = 'Draw';
            } else {
                statusText.textContent = `${this.boardState.winner} wins!`;
            }
        } else if (this.boardState.in_check) {
            statusText.textContent = 'Check!';
        } else {
            statusText.textContent = 'Playing';
        }
    }
    
    handleGameOver() {
        const modal = document.getElementById('game-over-modal');
        const resultTitle = document.getElementById('game-result');
        const resultText = document.getElementById('game-result-text');
        
        if (this.boardState.winner === 'draw') {
            resultTitle.textContent = 'Draw!';
            resultText.textContent = 'The game ended in a draw.';
        } else {
            const winner = this.boardState.winner;
            resultTitle.textContent = `${winner.charAt(0).toUpperCase() + winner.slice(1)} Wins!`;
            resultText.textContent = `Congratulations to ${winner}!`;
        }
        
        this.showModal('game-over-modal');
    }
    
    addMoveToHistory(move, color) {
        this.moveHistory.push({ move, color });
        this.updateMoveHistory();
    }
    
    updateMoveHistory() {
        const container = document.getElementById('moves-list');
        container.innerHTML = '';
        
        for (let i = 0; i < this.moveHistory.length; i += 2) {
            const moveNumber = Math.floor(i / 2) + 1;
            const whiteMove = this.moveHistory[i];
            const blackMove = this.moveHistory[i + 1];
            
            const movePair = document.createElement('div');
            movePair.className = 'move-pair';
            
            const numberDiv = document.createElement('div');
            numberDiv.className = 'move-number';
            numberDiv.textContent = `${moveNumber}.`;
            
            const whiteMoveDiv = document.createElement('div');
            whiteMoveDiv.className = 'move white-move';
            whiteMoveDiv.textContent = whiteMove ? this.formatMove(whiteMove.move) : '';
            
            const blackMoveDiv = document.createElement('div');
            blackMoveDiv.className = 'move black-move';
            blackMoveDiv.textContent = blackMove ? this.formatMove(blackMove.move) : '';
            
            movePair.appendChild(numberDiv);
            movePair.appendChild(whiteMoveDiv);
            movePair.appendChild(blackMoveDiv);
            container.appendChild(movePair);
        }
        
        container.scrollTop = container.scrollHeight;
    }
    
    formatMove(move) {
        const fromFile = String.fromCharCode(97 + move.from.col);
        const fromRank = 8 - move.from.row;
        const toFile = String.fromCharCode(97 + move.to.col);
        const toRank = 8 - move.to.row;
        return `${fromFile}${fromRank}${toFile}${toRank}`;
    }
    
    clearMoveHistory() {
        document.getElementById('moves-list').innerHTML = '';
    }
    
    clearCapturedPieces() {
        document.getElementById('captured-white-pieces').innerHTML = '';
        document.getElementById('captured-black-pieces').innerHTML = '';
    }
    
    showEngineThinking() {
        document.getElementById('engine-thinking').classList.remove('hidden');
    }
    
    hideEngineThinking() {
        document.getElementById('engine-thinking').classList.add('hidden');
    }
    
    showModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
    }
    
    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
    }
    
    showStatus(message, type = 'info') {
        const statusText = document.getElementById('status-text');
        statusText.textContent = message;
        statusText.className = `status-${type}`;
        
        setTimeout(() => {
            statusText.className = '';
        }, 3000);
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const game = new ChessGame();
    
    // Auto-start a new game
    setTimeout(() => {
        game.startNewGame();
    }, 500);
});
