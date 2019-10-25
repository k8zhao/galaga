from tkinter import *
import random
import pygame as pg

#music from youtube: https://www.youtube.com/watch?v=NslPD7pbfq0
## audio 
#loops through audio infinitely
def play():
    pg.mixer.music.play(-1)
def pause():
    pg.mixer.music.pause()
    
pg.mixer.init()
pg.mixer.music.load("themeSong.mp3")
play()

#parent class Player
class Player(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 20
        self.r = 25
        self.lives = 4
        self.color = "Black"
    
    def moveRight(self):
        self.x += self.speed

    def moveLeft(self):
        self.x -= self.speed
    
    def isOnLeftScreen(self, width):
        return self.x - self.r > 0 
        
    def isOnRightScreen(self, width):
        return self.x + self.r < width

    def draw(self, canvas, data):
        canvas.create_image(self.x, self.y-self.r, image = data.playerImage)

    def makeBullet(self):
        return playerBullet(self.x, self.y - self.r)

#parent class Enemy
class Enemy(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 25
        self.lives = 2
        self.speed = 10
        self.timer = 0

    def draw(self, canvas, data, image = "individualImage.gif"):
        canvas.create_image(self.x, self.y, image = image)

    def moveRight(self):
        self.x += self.speed
    
    def moveLeft(self):
        self.x -= self.speed 

    def makeEnemyBullet(self):
        return enemyBullet(self.x, self.y)

class individualEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.isReadyToDie = False
        self.m = None 
    
    def draw(self, canvas, data):
        super().draw(canvas, data, image = data.individualImage)
    
    #tracks player position, moves toward set position 
    def kamikaze(self, other, height):
        speed = 30
        if not self.isReadyToDie:
            if isinstance(other, Player):
                if (other.x - self.x) != 0:
                    self.m = (other.y - self.y)/(other.x - self.x)
                else:
                    self.m = 0
                self.isReadyToDie = True
        else:
            if self.m < 0:
                self.y -= self.m*speed
                self.x -= 1*speed
            elif self.m > 0:
                self.y += self.m*speed
                self.x += 1*speed
            else:
                self.y += 1*speed
    
    def hitPlayer(self, other):
        if(not isinstance(other, Player)):
            return False
        else:
            dist = ((other.x - self.x)**2 + (other.y - self.y)**2)**0.5
            return dist < self.r + other.r
    
    def isOffScreen(self, height):
        return self.y + self.r > height

class groupEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, canvas, data):
        canvas.create_image(self.x, self.y, image = data.groupImage)
    
class trackingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, canvas, data):
        super().draw(canvas, data, image = data.trackerImage)
    
    #overwrites makeEnemyBullet method 
    def makeEnemyBullet(self):
        return trackingEnemyBullet(self.x, self.y)

#parent class Bullet
class Bullet(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 25
        self.r = 5
        self.timer = 0

    def draw(self, canvas, color = "Red"):
        canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, \
        self.y+self.r, fill = color)
    
    def isOffScreen(self, height):
        return self.y + self.r > height
    
    def hitPlayer(self, other):
        if(not isinstance(other, Player)):
            return False
        else:
            dist = ((other.x - self.x)**2 + (other.y - self.y)**2)**0.5
            return dist < self.r + other.r

class playerBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, canvas):
        super().draw(canvas, color = "White")

    def move(self):
        self.y -= self.speed 
    
    #overwrites parent function because playBullet moves in opposite dir
    def isOffScreen(self):
        return self.y-self.r < 0

    def hitEnemy(self, other):
        if(not isinstance(other, Enemy)): 
            return False
        else:
            dist = ((other.x - self.x)**2 + (other.y - self.y)**2)**0.5
            return dist < self.r + other.r
    
    def hitPlayer(self, other):
        pass 

class enemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def draw(self, canvas):
        super().draw(canvas)
    
    def move(self):
        self.y += self.speed 

class trackingEnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.isTracking = False
        self.m = None
    
    def draw(self, canvas):
        super().draw(canvas)
        
    #enemy bullets from tracking enemy is able to shoot at current pos of player
    def shoot(self, other, height): 
        speed = 5
        if not self.isTracking:
            if isinstance(other, Player):
                if (other.x - self.x) != 0:
                    self.m = (other.y - self.y)/(other.x - self.x)
                else:
                    self.m = 0
                self.isTracking = True
        else:
            if self.m < 0:
                self.y -= self.m*speed
                self.x -= 1*speed
            elif self.m > 0:
                self.y += self.m*speed
                self.x += 1*speed
            else:
                self.y += 1*speed

#core animation code 
def init(data):
    data.highestScore = getHighestScore(data, "leaderboard.txt")
    data.mode = "startScreen"
    data.player = Player(data.width//2, data.height)
    data.playerBullets = []
    data.score = 0
    data.indEnemies = []
    data.enemyBullets = []
    data.grpBullets = []
    data.trackingEnemies = []
    data.trackingBullets = []
    data.timer = 0
    data.rows = 5
    data.cols = 3
    data.grpEnemyBoard = [([None]*data.cols) for row in range(data.rows)]
    data.grpEnemySize = 50
    data.grpEnemyBoardSize = len(data.grpEnemyBoard) * data.grpEnemySize
    data.gameOverTimerFired = 0
    data.username = ""
    data.textboxLeft = data.width//2 - 100
    data.textboxTop = data.height//2 - 10
    data.textboxRight = data.width//2 + 100
    data.textboxBottom = data.height//2 + 10
    data.isTypingUsername = False
    data.enemySize = 25
    data.playerImage = PhotoImage(file = "player.gif")
    data.individualImage = PhotoImage(file = "individualEnemy.gif")
    data.trackerImage = PhotoImage(file = "trackerEnemy.gif")
    data.groupImage = PhotoImage(file = "groupEnemy.gif")
    data.backgroundImage = PhotoImage(file = "background.gif")
    data.startImage = PhotoImage(file = "startScreen.gif")
    data.scrollY = 0
    data.scrollYSpeed = 10
    data.startScreenTimer = 0
    data.grpSpeed = 10
    data.grpScrollX = 0
    data.buttonSize = 100
    data.buttonHeight = 10
    data.isMovingRight = True
    
## keeps track of current mode 
#calls another mousePressed function based on current mode
def mousePressed(event, data):
    if (data.mode == "startScreen"): 
        startScreenMousePressed(event, data)
    elif (data.mode == "playGame"):   
        playGameMousePressed(event, data)
    elif (data.mode == "gameOver"):
        gameOverMousePressed(event, data)
    elif (data.mode == "leaderboard"):
        leaderboardMousePressed(event, data)
        
#calls another keyPressed function based on current mode
def keyPressed(event, data):
    if (data.mode == "startScreen"): 
        startScreenKeyPressed(event, data)
    elif (data.mode == "playGame"):   
        playGameKeyPressed(event, data)
    elif (data.mode == "gameOver"):       
        gameOverKeyPressed(event, data)
    elif (data.mode == "leaderboard"):
        leaderboardKeyPressed(event, data)

#calls another timeFired function based on current mode
def timerFired(data):
    if (data.mode == "startScreen"): 
        startScreenTimerFired(data)
    elif (data.mode == "playGame"):   
        playGameTimerFired(data)
    elif (data.mode == "gameOver"):       
        gameOverTimerFired(data)
    elif (data.mode == "leaderboard"):
        leaderboardTimerFired(data)

#calls another redrawAll function based on current mode
def redrawAll(canvas, data):
    if (data.mode == "startScreen"): 
        startScreenRedrawAll(canvas, data)
    elif (data.mode == "playGame"):
        playGameRedrawAll(canvas, data)
    elif (data.mode == "gameOver"):      
        gameOverRedrawAll(canvas, data)
    elif (data.mode == "leaderboard"):
        leaderboardRedrawAll(canvas, data)

## startScreen mode 
def startScreenMousePressed(event, data):
    threeQuarterPage = 3/4
    #if user clicks inside textbox, can type their username
    if event.x > data.textboxLeft and event.x < data.textboxRight and \
    event.y < data.textboxBottom and event.y > data.textboxTop:
        data.isTypingUsername = True
    #if user clicks inside leaderboard button, they can see leaderboard
    if event.x > data.width//2-data.buttonSize and event.x < data.width//2+\
    data.buttonSize and event.y < data.height*(threeQuarterPage)+\
    data.buttonHeight and event.y > data.height*(3/4)-data.buttonHeight:
        data.mode = "leaderboard"

#username appears on screen as user types it
def startScreenKeyPressed(event, data):
    if data.isTypingUsername:
        upperA = 65
        upperZ = 90
        lowerA = 97
        lowerZ = 122
        if (event.char >= chr(upperA) and event.char <= chr(upperZ)) or \
        (event.char >= chr(lowerA) and event.char <= chr(lowerZ)):
            data.username += event.char
    if event.keysym == "Return":
        data.mode = "playGame"
    if event.keysym == "BackSpace":
        data.username = data.username[:-1]

#resets variables for the new game 
def startScreenTimerFired(data):
    data.startScreenTimer += 1
    if data.startScreenTimer == 0:
        data.username = ""
        print("username: ", data.username)
    data.score = 0
    data.playerBullets.clear()
    data.indEnemies.clear()
    data.enemyBullets.clear()
    data.trackingEnemies.clear()
    data.trackingBullets.clear()
    data.player = Player(data.width//2, data.height)
    data.gameOverTimerFired = 0
    data.grpEnemyBoard = [([None]*data.cols) for row in range(data.rows)]
    
#draws start screen
def drawStartScreen(canvas, data):
    positioning = 10
    threeQuarterPage = 3/4
    canvas.create_image(data.width//2, data.height//2, image = data.startImage)
    canvas.create_rectangle(data.textboxLeft, data.textboxTop, \
    data.textboxRight, data.textboxBottom, fill = "White")
    canvas.create_text(data.width//2, data.textboxTop - positioning, text = \
    "Enter username: ", font = "Courier 10", fill = "White")
    canvas.create_text(data.width//2, data.height//2, text = data.username, \
    font = "Courier 10")
    canvas.create_rectangle(data.width//2-data.buttonSize, data.height*\
    (threeQuarterPage) - data.buttonHeight, data.width//2 + data.buttonSize,\
    data.height*(threeQuarterPage) + data.buttonHeight, fill = "Red")
    canvas.create_text(data.width//2, data.height*(threeQuarterPage), text = 
    "press to see the leaderboard", font = "Courier 10", fill = "White")
    
def startScreenRedrawAll(canvas, data):
    drawStartScreen(canvas, data)
    
## playGame mode
def playGameMousePressed(event, data):
    pass

def playGameKeyPressed(event, data):
    #left and right arrows move player 
    if event.keysym == "Right":
        if data.player.isOnRightScreen(data.width):
            data.player.moveRight()
    if event.keysym == "Left":
        if data.player.isOnLeftScreen(data.width):
            data.player.moveLeft()
    #spacebar shoots bullets 
    if event.keysym == "space":
        data.playerBullets.append(data.player.makeBullet())

def isOverlapping(x, y, r, other):
    dist = ((other.x - x)**2 + (other.y - y)**2)**0.5
    if isinstance(other, Enemy) and  dist < r + other.r:
        return True 

# #checks if the enemy added overlaps with any existing enemies
# #removes enemy if overlapping with any existing enemies
def checkOverlaps(data, x, y, r, individual, tracking, group):
    for i in individual:
        if isOverlapping(x, y, r, i):
            return False
    for t in tracking:
        if isOverlapping(x, y, r, t):
            return False
    for r in range(len(group)):
        for c in range(len(group[0])):
            if group[r][c] != None:
                if isOverlapping(x, y, r, group[r][c]):
                    return False
    return True 

#reads leaderboard and gets highest score in the leaderboard
def getHighestScore(data, filename):
    leaderboard = readFile(filename)
    leaderboard = leaderboard.splitlines()
    try:
        firstColon = leaderboard[0].find(":")
        highestScore = int(leaderboard[0][firstColon+1:])
        data.highestScore = highestScore
        return data.highestScore
    except:
        data.highestScore = 0
        return data.highestScore

def playGameTimerFired(data):
    data.timer += 1
    #moves background image and wraps around 
    data.scrollY += data.scrollYSpeed
    if data.scrollY >= data.height:
        data.scrollY = 0
    #each individual enemy and bullet has a unique timer
    #starts incrementing as soon as enemy and/or bullet is created
    for enemy in data.indEnemies:
        enemy.timer += 1
    for eBullet in data.enemyBullets:
        eBullet.timer += 1
    for r in range(len(data.grpEnemyBoard)):
        for c in range(len(data.grpEnemyBoard[0])):
            if data.grpEnemyBoard[r][c] != None:
                data.grpEnemyBoard[r][c].timer += 1
    #moves player bullets and removes those offscreen
    for bullet in data.playerBullets:
        bullet.move()
        if bullet.isOffScreen():
            data.playerBullets.remove(bullet)
    #moves enemy bullets and removes those offscreen
    for eBullet in data.enemyBullets:
        eBullet.move()
        if eBullet.isOffScreen(data.height):
            data.enemyBullets.remove(eBullet)
    #checks if individual enemies (kamikaze) have moved offscreen and removes them
    for i in data.indEnemies:
        if i.isOffScreen(data.height):
            data.indEnemies.remove(i)
    #adds a tracking enemy every 10 seconds
    if data.timer % 100 == 0:
        x = random.randint(data.enemySize, data.width-data.enemySize)
        y = random.randint(data.enemySize,data.height//2-data.enemySize)
        if checkOverlaps(data, x, y, data.enemySize, data.indEnemies, \
        data.trackingEnemies, data.grpEnemyBoard):
            data.trackingEnemies.append(trackingEnemy(x, y))
    #creates tracking bullets every 10 seconds
    for tracker in data.trackingEnemies:
        if data.timer % 100 == 0:
            data.trackingBullets.append(tracker.makeEnemyBullet())
    #loops through tracking bullets and shoots them (move function)
    for tBullet in data.trackingBullets:
        tBullet.shoot(data.player, data.height)
        if tBullet.isOffScreen(data.height):
            data.trackingBullets.remove(tBullet)
    #adds an individual enemy every 5 seconds
    if data.timer % 50 == 0:
        x = random.randint(data.enemySize, data.width-data.enemySize)
        y = random.randint(data.enemySize,data.height//2-data.enemySize)
        if checkOverlaps(data, x, y, data.enemySize, data.indEnemies, \
        data.trackingEnemies, data.grpEnemyBoard):
            data.indEnemies.append(individualEnemy(x, y))
    #creates enemy bullets at random times for each enemy 
    for enemy in data.indEnemies:
        y = random.randint(20, 50)
        if enemy.timer % y == 0:
            data.enemyBullets.append(enemy.makeEnemyBullet())
    #checks if player bullets are hitting enemies, takes a life away, adds score
    for bullet in data.playerBullets:
        for enemy in data.indEnemies:
            if bullet.hitEnemy(enemy):
                if bullet in data.playerBullets:
                    data.playerBullets.remove(bullet)
                    enemy.lives -= 1
                if enemy.lives == 0:
                    data.indEnemies.remove(enemy)
                    data.score += 10
    #checks if player bullets are hitting tracking enemies, takes life away
    for bullet in data.playerBullets:
        for tracker in data.trackingEnemies:
            if bullet.hitEnemy(tracker):
                if bullet in data.playerBullets:
                    data.playerBullets.remove(bullet)
                    tracker.lives -= 1
                if tracker.lives == 0:
                    data.trackingEnemies.remove(tracker)
                    data.score += 20
    #checks if player bullets are hitting group enemies, takes life away
    for bullet in data.playerBullets:
        for r in range(len(data.grpEnemyBoard)):
            for c in range(len(data.grpEnemyBoard[0])):
                if bullet.hitEnemy(data.grpEnemyBoard[r][c]):
                    if bullet in data.playerBullets:
                        data.playerBullets.remove(bullet)
                    data.grpEnemyBoard[r][c].lives -= 1
                    if data.grpEnemyBoard[r][c].lives == 0:
                        data.grpEnemyBoard[r][c] = None
                        data.score += 20 
    #checks if enemy bullets are hitting player, takes a life away 
    for eBullet in data.enemyBullets:
        if eBullet.hitPlayer(data.player):
            data.enemyBullets.remove(eBullet)
            print("player lives: ", data.player.lives)
            data.player.lives -= 1
    #checks if tracking bullets are hitting player, takes 2 lives away 
    for tBullet in data.trackingBullets:
        if tBullet.hitPlayer(data.player):
            data.trackingBullets.remove(tBullet)
            print("player lives: ", data.player.lives)
            data.player.lives -= 2
    #increments scrollX for group enemies
    if data.score > 100:
        for r in range(len(data.grpEnemyBoard)):
            for c in range(len(data.grpEnemyBoard[0])):
                if data.grpEnemyBoard[r][c] != None:
                    if data.isMovingRight:
                        data.grpEnemyBoard[r][c].x += 1
                        if data.grpEnemyBoard[r][c].x + data.enemySize > \
                        data.width:
                            data.isMovingRight = False
                    if not data.isMovingRight:
                        data.grpEnemyBoard[r][c].x -= 1
                        if data.grpEnemyBoard[r][c].x - data.enemySize < 0:
                            data.isMovingRight = True 
    #every 5 seconds, creates 2 new group enemies by changing None val to enemy obj
    if data.timer % 50 == 0:
        bound1 = 4
        bound2 = 2
        r1 = random.randint(0, bound1)
        c1 = random.randint(0, bound2)
        r2 = random.randint(0, bound1)
        c2 = random.randint(0, bound2)
        if data.grpEnemyBoard[r1][c1] == None:
            data.grpEnemyBoard[r1][c1] = groupEnemy(r1*data.grpEnemySize +\
            (data.grpEnemySize//2), c1*data.grpEnemySize + (data.grpEnemySize//2))
        if data.grpEnemyBoard[r2][c2] == None:
            data.grpEnemyBoard[r2][c2] = groupEnemy(r2*data.grpEnemySize+\
            (data.grpEnemySize//2), c2*data.grpEnemySize + (data.grpEnemySize//2))

    #every group enemy shoots a bullet every 4 seconds based on personal timer
    for r in range(len(data.grpEnemyBoard)):
        for c in range(len(data.grpEnemyBoard[0])):
            if data.grpEnemyBoard[r][c] != None:
                if data.grpEnemyBoard[r][c].timer % 40 == 0:
                    data.enemyBullets.append(data.grpEnemyBoard[r][c].makeEnemyBullet())
    #after a certain point, an enemy will kamikaze and try to hit player
    if len(data.indEnemies) > 0 and data.score > 100 and data.timer % 10 == 0:
        data.indEnemies[0].kamikaze(data.player, data.height)
    #checks if individual enemy hit player, kills player
    for i in data.indEnemies:
        if i.hitPlayer(data.player):
            data.indEnemies.remove(i)
            data.mode = "gameOver"
    #updates highest score
    if data.highestScore < data.score:
        data.highestScore = data.score 
    #checks if game is over 
    if data.player.lives <= 0:
        data.mode = "gameOver"

def playGameRedrawAll(canvas, data):
    if data.mode == "gameOver":
        gameOverRedrawAll(canvas, data)
    if data.mode == "startScreen":
        startScreenRedrawAll(canvas, data)
    canvas.create_image(data.width//2, data.scrollY, image = data.backgroundImage)
    data.player.draw(canvas, data)
    positioning = 15
    for bullet in data.playerBullets:
        bullet.draw(canvas)
    for enemy in data.indEnemies:
        enemy.draw(canvas, data)
    for eBullet in data.enemyBullets:
        eBullet.draw(canvas)
    for trackingEnemy in data.trackingEnemies:
        trackingEnemy.draw(canvas, data)
    for tBullet in data.trackingBullets:
        tBullet.draw(canvas)
    for r in range(len(data.grpEnemyBoard)):
        for c in range(len(data.grpEnemyBoard[0])):
            if data.grpEnemyBoard[r][c] != None:
                data.grpEnemyBoard[r][c].draw(canvas, data)
    canvas.create_text(data.width//2, positioning, fill = "Red", font = \
    "Courier 15", text = "score: " + str(data.score))
    canvas.create_text(0, 0, anchor = "nw", fill = "Red", font = "Courier 15", \
    text = "highest score: " + str(data.highestScore))
          
## gameOver 
#adds score to username to complete newPlayer
def updateNewPlayer(data):
    new = data.username + ":" + str(data.score)
    return new 
    
def gameOverMousePressed(event, data):
    pass

def gameOverKeyPressed(event, data):
    if event.char == "s":
        data.mode = "startScreen"
        data.username = ""
    if event.char == "l":
        data.mode = "leaderboard"

def gameOverTimerFired(data):
    if data.gameOverTimerFired == 0:
        #update newPlayer and leaderboard with current player info 
        newPlayer = updateNewPlayer(data)
        updated = updateLeaderboard("leaderboard.txt", newPlayer)
    data.gameOverTimerFired += 1

def drawGameOverScreen(canvas, data):
    quarterPage = 1/4
    threeFifthspage = 3/5
    fourFifthsPage = 4/5
    canvas.create_image(data.width//2, data.height//2, image = data.backgroundImage)
    canvas.create_text(data.width//2, data.height*(quarterPage), text = \
    "GAME OVER!", font = "Courier 30", fill = "white")
    canvas.create_text(data.width//2, data.height//2, text = "Final Score: " + \
    str(data.score), font = "Courier 15", fill = "white")
    canvas.create_text(data.width//2, data.height*(threeFifthspage), text = \
    "press 's' to start again", font = "Courier 15", fill = "white")
    canvas. create_text(data.width//2, data.height*(fourFifthsPage), text = \
    "press 'l' to see the leaderboard", font = "Courier 15", fill = "white")

def gameOverRedrawAll(canvas, data):
    drawGameOverScreen(canvas, data)
    
## leaderboard
def leaderboardMousePressed(event, data):
    pass

def leaderboardKeyPressed(event, data):
    if event.char == "s":
        data.mode = "startScreen"
        data.username = ""

def leaderboardTimerFired(data):
    pass 

def drawLeaderboardScreen(canvas, data):
    quarterPage = 1/4
    threeQuarterPage = 3/4
    canvas.create_image(data.width//2, data.height//2, image = data.backgroundImage)
    canvas.create_text(data.width//2, data.height*(quarterPage), \
    text = "---THE GALACTIC HEROES---", font = "Courier 20", fill = "Blue")
    leaderboard = readFile("leaderboard.txt")
    topFive = ""
    i = 0
    topNumber = 5
    #gets the top 5 players from leaderboard
    for line in leaderboard.splitlines():
        if i<topNumber:
            topFive = topFive + line + "\n"
            i += 1
    canvas.create_text(data.width//2, data.height//2, text = topFive, \
    font = "Courier 20", fill = "Red")
    canvas.create_text(data.width//2, data.height*(threeQuarterPage), \
    text = "press 's' to play again", font = "Courier 10", fill = "white")

def leaderboardRedrawAll(canvas, data):
    drawLeaderboardScreen(canvas, data)

## read/write file-- making leaderboard
#readFile and writeFile taken from 112 website
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

#reads current sorted leaderboard, inserts newPlayer in correct place, writes a new file with newPlayer added to old leaderboard
def updateLeaderboard(filename, newPlayer):
    leaderboard = readFile(filename)
    leaderboard = leaderboard.splitlines()
    colon = newPlayer.find(":")
    newPlayerScore = int(newPlayer[colon+1:])
    scores = []
    lenBefore = len(leaderboard)
    if len(leaderboard) >= 1:
        for line in leaderboard:
            colon = line.find(":")
            score = int(line[colon+1:])
            scores.append(score)
        for i in range(len(scores)):
            #if newPlayerScore is greater than the highest score
            #then newPlayer is put in the beginning of the leaderboard
            if i == 0 and newPlayerScore >= scores[0]:
                leaderboard.insert(0, newPlayer)
                break
            elif (i != 0) and (newPlayerScore < scores[i-1]) and (newPlayerScore > scores[i]):
                leaderboard.insert(i, newPlayer)
                break 
    lenAfter = len(leaderboard)
    #if newPlayerScore less than everyone else's, just added to the end
    if lenBefore == lenAfter:
        leaderboard.append(newPlayer)
    newFile = ""
    #writes new leaderboard with newPlayer 
    for line in leaderboard:
        newFile = newFile + line + "\n"
    updated = writeFile(filename, newFile)
    return updated

## updated run function from 112 website 
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    init(data)
    # create the root and the canvas
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")
    pause() #stops audio when user closes window 

run(600, 400)