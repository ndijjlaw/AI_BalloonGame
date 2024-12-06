import random
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import sys

# Initialize
pygame.init()

# Create Window/Display
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Balloon Pop")

# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

# Load all balloon images
balloonColors = ['balloon-01.png', 'balloon-02.png', 'balloon-03.png', 'balloon-04.png', 'balloon-05.png']
balloonImages = [pygame.image.load(f'files/balloons/{color}').convert_alpha() for color in balloonColors]

# Variable to store the current balloon
currentBalloon = random.choice(balloonImages)
rectBalloon = currentBalloon.get_rect()
rectBalloon.x, rectBalloon.y = 500, 300

# Pop effect
popFrames = [
    pygame.image.load(f'files/pop/{i}.png').convert_alpha()
    for i in range(1, 10)
]

# Variables
speed = 15
score = 0
highScore = 0  # High score variable
startTime = time.time()
totalTime = 30
gameOver = False

# Animation variables
isPopping = False
popFrameIndex = 0
popPosition = (0, 0)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


def resetBalloon():
    """Reset the balloon to a new random position and choose a new balloon."""
    global currentBalloon
    rectBalloon.x = random.randint(100, width - 100)
    rectBalloon.y = height + 50
    currentBalloon = random.choice(balloonImages)


def displayGameOver():
    """Display the Game Over screen with Replay button, High Score, and instructions."""
    global highScore, score, gameOver

    # Update high score
    if score > highScore:
        highScore = score

    # Fonts
    titleFont = pygame.font.Font('files/font/Marcellus-Regular.ttf', 60)
    subFont = pygame.font.Font('files/font/Marcellus-Regular.ttf', 40)
    smallFont = pygame.font.Font('files/font/Marcellus-Regular.ttf', 30)

    # Text Elements
    title = titleFont.render("AItech Computer Vision Game", True, (0, 0, 0))
    instructions1 = subFont.render("Can you beat the high score?", True, (0, 0, 0))
    instructions2 = smallFont.render(
        "Use your hand to control the red dot to 'RESTART', then make a fist to simulate a left mouse click and begin playing.",
        True, (50, 50, 50)
    )
    instructions3 = smallFont.render(
        "Use your index finger to pop as many balloons as you can before the time runs out!",
        True, (50, 50, 50)
    )
    textScore = subFont.render(f'Your Score: {score}', True, (50, 50, 255))
    textHighScore = subFont.render(f'High Score to Beat: {highScore}', True, (255, 50, 50))

    # Replay Button
    replayButton = pygame.Rect(540, 400, 200, 80)  # Button position and size

    # Draw Game Over screen
    window.fill((255, 255, 255))
    window.blit(title, (width // 2 - title.get_width() // 2, 50))
    window.blit(instructions1, (width // 2 - instructions1.get_width() // 2, 130))
    window.blit(instructions2, (width // 2 - instructions2.get_width() // 2, 180))
    window.blit(instructions3, (width // 2 - instructions3.get_width() // 2, 220))
    window.blit(textScore, (width // 2 - textScore.get_width() // 2, 300))
    window.blit(textHighScore, (width // 2 - textHighScore.get_width() // 2, 350))

    # Replay Button
    pygame.draw.rect(window, (0, 255, 0), replayButton)
    replayText = subFont.render("Replay", True, (255, 255, 255))
    window.blit(replayText, (replayButton.x + replayButton.width // 2 - replayText.get_width() // 2,
                             replayButton.y + replayButton.height // 2 - replayText.get_height() // 2))

    return replayButton

# Main loop
start = True
while start:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()
            sys.exit()

    # Game Over logic
    if gameOver:
        replayButton = displayGameOver()

        # OpenCV: Read webcam input
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        # Draw camera feed
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))

        # Redraw Game Over screen on top of camera feed
        replayButton = displayGameOver()

        # Check for hand input
        if hands:
            hand = hands[0]
            x, y = hand['lmList'][8][0:2]  # Index finger position (cursor)
            fingers = detector.fingersUp(hand)

            # Draw a debug cursor on the screen
            pygame.draw.circle(window, (255, 0, 0), (x, y), 10)

            # Check for click gesture (fist)
            if fingers == [0, 0, 0, 0, 0]:  # All fingers down (fist)
                if replayButton.collidepoint(x, y):
                    print("Replay button clicked!")  # Debug log
                    time.sleep(0.3)  # Prevent rapid restarts
                    score = 0
                    speed = 15
                    startTime = time.time()
                    gameOver = False

        pygame.display.update()
        clock.tick(fps)
        continue

    # Main game logic
    timeRemain = int(totalTime - (time.time() - startTime))
    if timeRemain < 0:
        gameOver = True
    else:
        # OpenCV
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        # Draw the camera feed
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))

        if isPopping:
            if popFrameIndex < len(popFrames):
                popRect = popFrames[popFrameIndex].get_rect(center=popPosition)
                window.blit(popFrames[popFrameIndex], popRect)
                popFrameIndex += 1
            else:
                isPopping = False
                resetBalloon()
        else:
            rectBalloon.y -= speed
            if rectBalloon.y < 0:
                resetBalloon()
                speed += 1

            if hands:
                hand = hands[0]
                x, y, _ = hand['lmList'][8]
                if rectBalloon.collidepoint(x, y):
                    isPopping = True
                    popFrameIndex = 0
                    popPosition = rectBalloon.center
                    score += 10
                    speed += 1

            window.blit(currentBalloon, rectBalloon)

        # Draw score and time
        font = pygame.font.Font('files/font/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
        window.blit(textScore, (35, 35))
        window.blit(textTime, (1000, 35))

    # Update Display
    pygame.display.update()
    clock.tick(fps)
