import random
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import sys  # For clean exit

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
balloonColors = ['balloon-01.png', 'balloon-02.png', 'balloon-03.png', 'balloon-04.png', 'balloon-05.png']  # Add other balloon file names here
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

print(f"Loaded {len(popFrames)} pop frames.")

# Variables
speed = 15
score = 0
startTime = time.time()
totalTime = 30

# Animation variables
isPopping = False  # Declare globally to avoid scope issues
popFrameIndex = 0  # Initialize pop animation frame index
popPosition = (0, 0)  # Initialize pop position

# Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


def resetBalloon():
    """Reset the balloon to a new random position and choose a new balloon."""
    global currentBalloon
    rectBalloon.x = random.randint(100, width - 100)
    rectBalloon.y = height + 50
    currentBalloon = random.choice(balloonImages)  # Select a new balloon image


# Main loop
start = True
while start:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()
            sys.exit()  # Ensure clean exit

    # Apply Logic
    timeRemain = int(totalTime - (time.time() - startTime))
    if timeRemain < 0:
        # Game over screen
        window.fill((255, 255, 255))
        font = pygame.font.Font('files/font/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Your Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time UP', True, (50, 50, 255))
        window.blit(textScore, (450, 350))
        window.blit(textTime, (530, 275))
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

        if isPopping:  # Handle pop animation
            if popFrameIndex < len(popFrames):
                print(f"Displaying pop frame {popFrameIndex}")  # Debug
                # Align pop frames to the balloon's center
                popRect = popFrames[popFrameIndex].get_rect(center=popPosition)
                window.blit(popFrames[popFrameIndex], popRect)  # Show pop frame
                popFrameIndex += 1
            else:
                isPopping = False  # Animation finished
                resetBalloon()
        else:  # Normal game logic when not popping
            rectBalloon.y -= speed  # Move the balloon up

            # Check if the balloon has reached the top without popping
            if rectBalloon.y < 0:
                resetBalloon()
                speed += 1

            # Check for hand collision with the balloon
            if hands:
                hand = hands[0]
                x, y, _ = hand['lmList'][8]  # Index finger tip position
                if rectBalloon.collidepoint(x, y):
                    print("Balloon popped!")  # Debug
                    isPopping = True  # Start pop animation
                    popFrameIndex = 0  # Reset the animation frame
                    # Save the center of the balloon for the pop animation
                    popPosition = rectBalloon.center
                    score += 10
                    speed += 1

            # Draw the balloon
            window.blit(currentBalloon, rectBalloon)

        # Draw score and time
        font = pygame.font.Font('files/font/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
        window.blit(textScore, (35, 35))
        window.blit(textTime, (1000, 35))

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
