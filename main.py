from queue import PriorityQueue
import curses
import time

class Board(object):
    """
    - Esta classe define um tabuleiro para o 8-Puzzle.
    - As telhas são denotadas usando 1-8, 0 denota uma peça em branco.
    """
    def __init__(self, board=None, moves=0, previous=None):
        """
            placa: array representando a placa atual,
            move: número de movimentos para chegar a esta prancha,
            anterior: estado anterior do conselho
        """
        if board is None:
            self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        else:
            self.board = board
        self.previous = previous
        self.moves = moves

    def is_goal(self):
        """
            retorna True se a placa atual for o estado da meta
        """
        for i in range(0, 9):
            if i != 8:
                if self.board[i] != i + 1:
                    return False

        return True

    def move_blank(self, where):
        """
            onde: Mover em branco "esquerda", "direita"
                     'Para cima ou para baixo',
                    Não faz nada se o lance estiver fora de campo.
        """
        blank = self.find_blank()

        if where == 'left':
            if blank % 3 != 0:
                t_col = (blank % 3) - 1
                t_row = int(blank / 3)
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'right':
            if blank % 3 != 2:
                t_col = (blank % 3) + 1
                t_row = int(blank / 3)
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'up':
            if int(blank / 3) != 0:
                t_col = (blank % 3)
                t_row = int(blank / 3) - 1
                self.exchange(blank, t_row * 3 + t_col)

        if where == 'down':
            if int(blank / 3) != 2:
                t_col = (blank % 3)
                t_row = int(blank / 3) + 1
                self.exchange(blank, t_row * 3 + t_col)

    def find_blank(self):
        """
            retorna o índice do bloco em branco
        """
        blank = None
        for i in range(0, 9):
            if self.board[i] == 0:
                blank = i
                break
        return blank

    def clone(self):
        """
            retorna cópia da placa atual com
                movimentos = movimentos atuais + 1 e
                anterior = placa atual
        """
        return Board(self.board.copy(), self.moves + 1, self)


    def exchange(self, source, target):
        """
            troca o bloco 'source' com 'target'
        """
        # print('Exchanging: {} <-> {}'.format(source, target))
        self.board[source], self.board[target] = self.board[target], self.board[source]


    def neighbours(self):
        """
            retorna uma lista de todos os vizinhos válidos gerados pela movimentação
                o bloco em branco uma vez em todas as direções possíveis
        """
        blank_index = self.find_blank()

        neighbours = []

        # print('Blank found: {}, := {}, {}'.format(blank_index, int(blank_index / 3), blank_index % 3))
        # Podemos mover a placa em branco para a esquerda?
        if blank_index % 3 != 0:
            new_board = self.clone()
            new_board.move_blank('left')
            neighbours.append(new_board)

        # direita?
        if blank_index % 3 != 2:
            new_board = self.clone()
            new_board.move_blank('right')
            neighbours.append(new_board)

        # acima?
        if int(blank_index / 3) != 0:
            new_board = self.clone()
            new_board.move_blank('up')
            neighbours.append(new_board)

        # baixo?
        if int(blank_index / 3) != 2:
            new_board = self.clone()
            new_board.move_blank('down')
            neighbours.append(new_board)

        return neighbours


    def manhattan(self):
        """
            retorna a distância de manhattan para a placa
        """
        manhattan = 0
        for i in range(0, 9):
            if self.board[i] != i + 1 and self.board[i] != 0:
                correct_pos = 8 if self.board[i] == 0 else self.board[i] - 1
                s_row = int(i / 3)
                s_col = i % 3
                t_row = int(correct_pos / 3)
                t_col = correct_pos % 3
                manhattan += abs(s_row - t_row) + abs(s_col - t_col)

        return manhattan

    def to_pq_entry(self, count):
        """
            retorna a tupla (prioridade, contagem, placa)
        """
        return (self.moves + self.manhattan(), count, self)

    def __str__(self):
        """
            O mesmo que print (self), exceto que isso retorna uma string
        """
        string = ''
        string = string + '+---+---+---+\n'
        for i in range(3):
            for j in range(3):
                tile = self.board[i * 3 + j]
                string = string + '| {} '.format(' ' if tile == 0 else tile)
            string = string + '|\n'
            string = string + '+---+---+---+\n'
        return string

    def __eq__(self, other):
        """
            verifique se auto == outro
        """
        if other is None:
            return False
        else:
            return self.board == other.board

    def get_previous_states(self):
        """
            retornar uma lista de estados anteriores subindo a árvore do espaço de estados
        """
        states = [self]
        prev = self.previous
        while prev is not None:
            states.append(prev)
            prev = prev.previous

        states.reverse()
        return states

def diff_boards_str(board1, board2):
    """
        retorna uma string descrevendo o movimento feito de board1 para board2
    """
    if board1 is None:
        return '\nEstado inicial'

    if board2 is None:
        return ''

    blank1 = board1.find_blank()
    blank2 = board2.find_blank()

    s_row = int(blank1 / 3)
    s_col = blank1 % 3
    t_row = int(blank2 / 3)
    t_col = blank2 % 3

    dx = s_col - t_col
    dy = s_row - t_row

    if dx == 1:
        return 'Mova para a esquerda'
    if dx == -1:
        return 'Mover para a direita'
    if dy == 1:
        return 'Mova para cima'
    if dy == -1:
        return 'Mova para baixo'

def solve(initial_board):
    """
        retorna uma lista de movimentos de 'initial_board' para o estado do objetivo
            calculado usando o algoritmo A *
    """
    queue = PriorityQueue()
    queue.put(initial_board.to_pq_entry(0))

    i = 1
    while not queue.empty():
        board = queue.get()[2]
        if not board.is_goal():
            for neighbour in board.neighbours():
                if neighbour != board.previous:
                    queue.put(neighbour.to_pq_entry(i))
                    i += 1
        else:
            return board.get_previous_states()

    return None


def main2(window):
    """
        Função de driver para manipular a interface do usuário usando curses.
    """
    initial = Board()
    window.insstr(0, 0, 'Digite o estado inicial do quadro: ')
    window.insstr(1, 0, str(initial))
    window.insstr(8, 0, 'Controles: cima, baixo, esquerda, direita para mover, enter para resolver')
    ch = window.getch()
    while str(ch) != '10':
        if ch == curses.KEY_UP:
            # Move blank up
            initial.move_blank('up')
        if ch == curses.KEY_DOWN:
            # Move blank down
            initial.move_blank('down')
        if ch == curses.KEY_LEFT:
            # Move blank left
            initial.move_blank('left')
        if ch == curses.KEY_RIGHT:
            # Move blank right
            initial.move_blank('right')
        window.insstr(1, 0, str(initial))
        ch = window.getch()
        window.refresh()

    moves = solve(initial)
    prev = None
    window.clear()
    for move in moves:
        window.clear()
        window.insstr(0, 0, 'Resolvendo 8-Puzzle: ')
        window.insstr(1, 0, str(move))
        window.insstr(8, 0, diff_boards_str(prev, move))
        window.refresh()
        time.sleep(1)
        prev = move

    window.insstr(9, 0, '8-Puzzle resolvido =)')
    window.getch()

if __name__ == '__main__':
    curses.wrapper(main2)
