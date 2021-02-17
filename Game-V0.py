import pygame
import time
import random

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

def things(thingx, thingy, thingw, thingh, color):
    gameDisplay.blit(coneImg, (thingx,thingy))
    gameDisplay.blit(coneImg, (thingx+track_width,thingy))
    
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