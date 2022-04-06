from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random, time
from minesweeperbutton import *

#Change these numbers to make game more difficult
#CELLS is the size of the board
CELLS = 10
#Number of bombs
BOMBS = 15

#Images for widgets, downloaded from freepngimg.com
IMG_BOMB = QImage("./images/flashybomb.png")
IMG_FLAG = QImage("./images/flag.png")
IMG_CLOCK = QImage("./images/stopwatch.png")
IMG_TURNS = QImage("./images/moves.png")

#State of the board, set up first so it would be more convinient to change images later
STATE_READY = 0
STATE_PLAYING = 1
STATE_LOSE = 2
STATE_WIN = 3

STATE_ICONS = {
    STATE_READY: "./images/shiba.png",
    STATE_PLAYING: "./images/shiba.png",
    STATE_LOSE: "./images/lost.png",
    STATE_WIN: "./images/win.png",
}

class MainWindow(QMainWindow):
    nturns = 0
    def __init__(self):
        super(MainWindow, self).__init__()

        # set title
        self.setWindowTitle("Minesweeper")


        w = QWidget()
        hb = QHBoxLayout()

        #Label to indicate number of mines in the game
        self.mines = QLabel()
        self.mines.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mines.setText("%03d" % BOMBS)

        #time taken for 1 game
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.clock.setText("000")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # 1 second timer

        #number of clicks made
        self.turns = QLabel()
        self.turns.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.turns.setText("%03d" % self.nturns)

        #new game button, also used to indicate the state of the game, win or lost 
        self.dogebutton = QPushButton()
        self.dogebutton.setFixedSize(QSize(35, 35))
        self.dogebutton.setIconSize(QSize(35, 35))
        self.dogebutton.setIcon(QIcon("./images/shiba.png"))      
        self.dogebutton.pressed.connect(self.dogebutton_pressed)

        hb.addWidget(self.dogebutton)

        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_BOMB))
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hb.addWidget(l)

        hb.addWidget(self.mines)

        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_TURNS))
        l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        hb.addWidget(l)
        hb.addWidget(self.turns)
        

        l = QLabel()
        l.setPixmap(QPixmap.fromImage(IMG_CLOCK))
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hb.addWidget(l)

        hb.addWidget(self.clock)

        vb = QVBoxLayout()
        vb.addLayout(hb)

        self.horizontal_grid = QHBoxLayout(self.setCentralWidget(QWidget()))

        vb.addLayout(self.horizontal_grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.init_game()
        self.update_state(STATE_READY)

        self.push = {}
        
        # Add an array of QPushbottons to the board
        for i in range(0, CELLS):
            self.vertical_grid = QVBoxLayout()
            for j in range(0, CELLS):
                self.push[i,j] = Button()
                #set property so more convinient to find out which buttons were pressed later
                self.push[i,j].setProperty("myRow",i)
                self.push[i,j].setProperty("myCol",j)
                #set objective name so it would be convinient to call the push button later if we need to reveal surrounding buttons
                self.push[i,j].setObjectName(str(i) + ',' + str(j))
                self.push[i,j].setStyleSheet('QPushButton {background-color: grey}')
                #connect left click and right click
                self.push[i,j].clicked.connect(self.left_clicked)
                self.push[i,j].r_clicked.connect(self.flag)
                self.vertical_grid.addWidget(self.push[i,j])
            self.horizontal_grid.addLayout(self.vertical_grid)
            self.horizontal_grid.setSpacing(0)

        self.show()
      
        
    def init_game(self):
        #set all label to 0
        self.nturns = 0
        self.turns.setText("%03d" % self.nturns)
        self.clock.setText("000")

        self.board = []
        # create empty array
        #0: nothing not revealed
        #1-8: bombs around not revealed
        #9: bomb not flag not revealed
        #0-8 +10: revealed
        #9 +10: exploded
        #29: bomb flaged
        #0-8 +20: not revealed but flaged  
        for row in range(CELLS):
            col = [0]*CELLS
            self.board.append(col)

        #add mines to the board
        self.bomb_added = [] #array to record which buttons we have added mines 
        while len(self.bomb_added) < BOMBS:
            row, col = random.randint(0, CELLS - 1), random.randint(0, CELLS - 1)
            if (row, col) not in self.bomb_added:
                self.board[row][col] = 9
                self.bomb_added.append((row, col))

        #update numbers around the bomb
        for row in range(CELLS):
            for col in range(CELLS):
                # if we have a bomb, we add 1 to the value of surrounding buttons
                if self.board[row][col] == 9:
                    if row - 1 >= 0 and self.board[row - 1][col] != 9:
                        self.board[row - 1][col] += 1
                    if row + 1 <= CELLS -1 and self.board[row + 1][col] != 9:
                        self.board[row + 1][col] += 1
                    if col - 1 >= 0 and self.board[row][col - 1] != 9:
                        self.board[row][col - 1] += 1
                    if col + 1 <= CELLS - 1 and self.board[row][col + 1] != 9:
                        self.board[row][col + 1] += 1
                    if row - 1 >= 0 and col - 1 >= 0 and self.board[row - 1][col - 1] != 9:
                        self.board[row - 1][col - 1] += 1
                    if row + 1 <= CELLS - 1 and col - 1 >= 0 and self.board[row + 1][col - 1] != 9:
                        self.board[row + 1][col - 1] += 1
                    if row - 1 >= 0 and col + 1 <= CELLS - 1 and self.board[row - 1][col + 1] != 9:
                        self.board[row - 1][col + 1] += 1
                    if row + 1 <= CELLS - 1 and col + 1 <= CELLS - 1 and self.board[row + 1][col + 1] != 9:
                        self.board[row + 1][col + 1] += 1

    #right-click
    def flag(self):
        self.r_clicked=self.sender()
        row=self.r_clicked.property("myRow")
        col=self.r_clicked.property("myCol")

        #indicate button will be flag
        if self.board[row][col] <= 9:
            self.board[row][col] += 20
        #unflag
        elif self.board[row][col] >= 20:
            self.board[row][col] -= 20
        

        self.update_board()

        #trigger start of game
        if self.state != STATE_PLAYING:
            # First click.
            self.update_state(STATE_PLAYING)
            # Start timer.
            self._timer_start_nsecs = int(time.time())

        #You won if you flag the last bomb
        if self.check_win():
            self.update_state(STATE_WIN)

        self.nturns += 1
        self.turns.setText("%03d" % self.nturns)


    def left_clicked(self):

        self.l_clicked=self.sender()
        row=self.l_clicked.property("myRow")
        col=self.l_clicked.property("myCol")

        #if empty button was clicked, expend to surrounding buttons
        if self.board[row][col] == 0:
            self.empty_buttons_pressed(row,col)
            self.update_board()

        #if not empty, just simply reveal it
        if self.board[row][col] in range(1,9):
            self.board[row][col] +=10
            self.update_board()
          

        #trigger start of game
        if self.state != STATE_PLAYING:
            # First click.
            self.update_state(STATE_PLAYING)
            # Start timer.
            self._timer_start_nsecs = int(time.time())

        #You won
        if self.check_win():
            self.update_state(STATE_WIN)
        
        #You lost
        if self.board[row][col] == 9:
            self.update_state(STATE_LOSE)
            self.reveal_board()

        self.nturns += 1
        self.turns.setText("%03d" % self.nturns)

    #this function used when empty button was clicked to reveal surrounding button
    def empty_buttons_pressed(self, row, col):
        if self.board[row][col] == 0:
            #recursive if we find another empty button
            self.board[row][col] += 10
            if row - 1 >= 0:
                self.empty_buttons_pressed(row - 1, col)
            if row + 1 <= CELLS -1:
                self.empty_buttons_pressed(row + 1, col)
            if col - 1 >= 0:
                self.empty_buttons_pressed(row, col - 1)
            if col + 1 <= CELLS-1:
                self.empty_buttons_pressed(row, col + 1)
            if row - 1 >= 0 and col - 1 >= 0:
                self.empty_buttons_pressed(row - 1, col - 1)
            if row + 1 <= CELLS -1 and col - 1 >= 0:
                self.empty_buttons_pressed(row + 1, col - 1)
            if row - 1 >= 0 and col + 1 <= CELLS - 1:
                self.empty_buttons_pressed(row - 1, col + 1)
            if row + 1 <= CELLS -1 and col + 1 <= CELLS-1:
                self.empty_buttons_pressed(row + 1, col + 1)
        #if the button is 1-8, simply +10 so it will be revealed when update_board
        else:
            if self.board[row][col] in range(1,9):
                self.board[row][col] += 10    

    #update how the button actually looks like according to board[] 
    def update_board(self):
        for row in range(CELLS):
            for col in range(CELLS):
                if self.board[row][col] <= 9:
                    self.push[row,col].setStyleSheet('QPushButton {background-color: grey}')
                    self.push[row,col].setIcon(QIcon())
                    self.push[row,col].setText("")
                elif self.board[row][col] == 10:
                    self.push[row,col].setStyleSheet('QPushButton {background-color: white}')
                elif self.board[row][col] == 11:
                    self.push[row,col].setStyleSheet('QPushButton {color: skyblue;}')
                    self.push[row,col].setText("1")
                elif self.board[row][col] == 12:
                    self.push[row,col].setStyleSheet('QPushButton {color: lime;}')
                    self.push[row,col].setText("2")
                elif self.board[row][col] == 13:
                    self.push[row,col].setStyleSheet('QPushButton {color: slateblue;}')
                    self.push[row,col].setText("3")
                elif self.board[row][col] == 14:
                    self.push[row,col].setStyleSheet('QPushButton {color: red;}')
                    self.push[row,col].setText("4")
                elif self.board[row][col] == 15:
                    self.push[row,col].setStyleSheet('QPushButton {color: hotpink;}')
                    self.push[row,col].setText("5")
                elif self.board[row][col] == 16:
                    self.push[row,col].setStyleSheet('QPushButton {color: darkviolet;}')
                    self.push[row,col].setText("6")
                elif self.board[row][col] == 17:
                    self.push[row,col].setStyleSheet('QPushButton {color: orange;}')
                    self.push[row,col].setText("7")
                elif self.board[row][col] == 18:
                    self.push[row,col].setStyleSheet('QPushButton {color: midnightblue;}')
                    self.push[row,col].setText("8")
                elif self.board[row][col] == 19:
                    self.push[row,col].setStyleSheet('QPushButton {background-color: red}')
                    self.push[row, col].setIcon(QIcon("./images/flashybomb.png"))
                elif self.board[row][col] >= 20:
                    self.push[row,col].setIcon(QIcon("./images/flag.png"))

    def dogebutton_pressed(self):
        #if dogebutton pressed while playing, game is considered lost and reveal the board
        if self.state == STATE_PLAYING:
            self.update_state(STATE_LOSE)
            self.reveal_board()

        #if dogebutton pressed when game is already won or lost, new game
        elif self.state == STATE_LOSE or self.state == STATE_WIN:
            self.update_state(STATE_READY)
            self.reset_game()
            self.init_game()

    #reveal all board
    def reveal_board(self):
        for row in range(CELLS):
            for col in range(CELLS):
                if self.board[row][col] <= 9:
                    self.board[row][col] += 10
                elif self.board[row][col] >=20:
                    self.board[row][col] -= 10

        self.update_board()

    #reset the board[] and update buttons
    def reset_game(self):
        for row in range(CELLS):
            for col in range(CELLS):
                self.board[row][col] = 0
        self.update_board()

    #check to see if the board still have any unrevealed button or any mine that have not been flaged
    def check_win(self):
        for row in range(CELLS):
            for col in range(CELLS):
                if self.board[row][col] <= 9 or self.board[row][col] in range(20,29):
                    return False
        return True

    #Start the clock
    def update_timer(self):
        if self.state == STATE_PLAYING:
            n_secs = int(time.time()) - self._timer_start_nsecs
            self.clock.setText("%03d" % n_secs)

    #update the dogebutton so it show the game is lost or won
    def update_state(self, state):
        self.state = state
        self.dogebutton.setIcon(QIcon(STATE_ICONS[self.state]))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()