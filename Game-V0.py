import pygame
import time
import random
import math
from math import tan
from math import sqrt
pygame.init()

display_width = 800
display_height= 600
fps = 30

black = (0,0,0) #RGB
white = (255,255,255) #RGB
red = (255, 0, 0)

gameDisplay = pygame.display.set_mode((display_width, display_height))

pygame.display.set_caption('A bit Racey')

clock = pygame.time.Clock()

carImg = pygame.image.load('car.png')
coneImg = pygame.image.load('cone.png')
car_width = 100
track_width = 400
cone_width = 51
cone_height = 51
cone_speed = 5
track = [] #(x,y)
    
def car(x,y):
    gameDisplay.blit(carImg, (x,y))
    
    
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()
    
def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 115)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = (display_width/2, display_height/2)
    
    gameDisplay.blit(TextSurf, TextRect)
    pygame.display.update()
    
    time.sleep(2)
    
    game_loop()
    
def crash():
    message_display('You Crashed')

def front_lidar(car_x, car_y):
    front_lidar_x = car_x + car_width/2
    front_lidar_dist = car_y
    for (x,y) in track:
        if(front_lidar_x > x and front_lidar_x < x + cone_width):
            front_lidar_dist = min(front_lidar_dist, car_y-y-cone_height)

    pygame.draw.line(gameDisplay, black, (front_lidar_x, car_y), (front_lidar_x, car_y-front_lidar_dist))
    print(front_lidar_dist)
    return front_lidar_dist

def distance(x1, y1, x2, y2):
    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

def cone_crosses_line(start_x, start_y, end_x, end_y, x,y, right_side):
    a = (end_y - start_y) / (end_x-start_x)
    b = end_y - a*end_x

    cross_horizontal_x = (y + cone_height - b)/a
    cross_vertical_y = a*(x+ (cone_width if right_side else 0))+b

    if(cross_vertical_y >= y and cross_vertical_y <= y + cone_height):
        return True, x + ( cone_width if right_side else 0), cross_vertical_y 
    if(cross_horizontal_x >= x and cross_horizontal_x <= x + cone_width):
        return True, cross_horizontal_x, y + cone_height
    return False, 0, 0

def left_lidar(car_x, car_y):
    start_lidar_x = car_x + car_width/2
    start_lidar_y = car_y
    display_side_x = 0
    display_side_y = start_lidar_y-tan(math.pi/6)*start_lidar_x
    extreme_x = display_side_x
    extreme_y = display_side_y
    lidar_dist = distance(start_lidar_x, start_lidar_y , display_side_x, display_side_y)
    
    counter = 0
    for (x,y) in track:
        if(counter % 2 == 0):
            answer, point_x, point_y = cone_crosses_line(start_lidar_x, start_lidar_y, display_side_x, display_side_y, x,y, True)
            if answer:
                dist = distance(start_lidar_x, start_lidar_y, point_x, point_y)
                if  dist < lidar_dist:
                    lidar_dist = dist
                    extreme_x = point_x
                    extreme_y = point_y
        counter+=1

    pygame.draw.line(gameDisplay, black, (start_lidar_x, start_lidar_y ), (extreme_x, extreme_y))
    return lidar_dist

def right_lidar(car_x, car_y):
    start_lidar_x = car_x + car_width/2
    start_lidar_y = car_y
    display_side_x = display_width
    display_side_y = start_lidar_y-tan(math.pi/6)*(display_width-start_lidar_x)
    extreme_x = display_side_x
    extreme_y = display_side_y
    lidar_dist = distance(start_lidar_x, start_lidar_y , display_side_x, display_side_y)
    
    counter = 0
    for (x,y) in track:
        if(counter % 2 == 1):
            answer, point_x, point_y = cone_crosses_line(start_lidar_x, start_lidar_y, display_side_x, display_side_y, x,y, False)
            if answer:
                dist = distance(start_lidar_x, start_lidar_y, point_x, point_y)
                if  dist < lidar_dist:
                    lidar_dist = dist
                    extreme_x = point_x
                    extreme_y = point_y
        counter+=1

    pygame.draw.line(gameDisplay, black, (start_lidar_x, start_lidar_y ), (extreme_x, extreme_y))
    return lidar_dist

def draw_lidar(car_x, car_y):
    return front_lidar(car_x, car_y), left_lidar(car_x, car_y), right_lidar(car_x,car_y)
    
#create initial straight track
def create_track():
    track.clear()
    for i in range(16):
        track.append((200, display_height- i*cone_height)) #(x,y)
        track.append((600, display_height- i*cone_height)) #(x,y)

def draw_track():
    for (x,y) in track:
        gameDisplay.blit(coneImg, (x,y))

def did_it_crash(car_x, car_y):
    for (x,y) in track:
        if car_y < y + cone_height:
            if car_x > x and car_x < x + cone_width or car_x + car_width > x and car_x+car_width < x + cone_width:
                return True
    return False

def update_track():
    for i in range(len(track)):
        x, y = track.pop(0)
        track.append((x, y+cone_speed))
    x, y = track[0]
    if(y > display_height):
        track.pop(0)
        track.pop(0)
        value = random.randint(-1,1)
        x_last, y_last = track[28]
        x_pos = max(min(x_last + value*cone_width, display_width-track_width),0)
        track.append((x_pos,y_last-cone_height))
        track.append((x_pos + track_width ,y_last-cone_height))

#Game loop
def game_loop():
    gameExit = False
    
    car_x = display_width*0.45
    car_y = display_height*0.75
    car_x_change = 0
    
    create_track()

    while not gameExit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    car_x_change = -5
                elif event.key == pygame.K_RIGHT:
                    car_x_change = 5
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    car_x_change = 0

        car_x+=car_x_change

        gameDisplay.fill(white)
       
        draw_track()
        update_track()
        draw_lidar(car_x, car_y)

        car(car_x,car_y)
        
        #logic
        if car_x > display_width - car_width or car_x < 0:
            crash()

        if did_it_crash(car_x, car_y):
            crash()
        
        pygame.display.update()

        clock.tick(fps)

game_loop()
pygame.quit() #quit pygame
quit() #quit python