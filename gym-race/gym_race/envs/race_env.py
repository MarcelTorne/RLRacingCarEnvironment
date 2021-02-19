import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pygame
import time
import random
import math
from math import tan
from math import sqrt


"""
    3 Actions:
        - LEFT (-1)
        - RIGTH (1)
        - NOTHING (0)
    Observation Space:
        - 3 LIDARS in angles 45, 90, 135
    Reward:
        - (1) if no collision
        - (-1) if collision
"""
class RaceEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    """
    Custom Environment that follows gym interface.
    Space game with random enemies. 
    """

    def __init__(self):
        pygame.init()
        super(RaceEnv, self).__init__()

        self.fps = 30
        self.fps_clock = pygame.time.Clock() #todo: should it be pygame.time.Clock()?
        self.display_width = 800
        self.display_height = 600
        self.black = (0,0,0)
        self.white = (255,255,255)

        #do init game
        self.carImg = pygame.image.load('car.png')
        self.coneImg = pygame.image.load('cone.png')
        self.car_width = 100
        self.track_width = 400
        self.cone_width = 51
        self.cone_height = 51
        self.cone_speed = 5
        self.track = [] #(x,y)
        self.score = 0

        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Racing Game')
        self.gameDisplay.fill(self.white)
        n_actions = 2
        self.action_space = spaces.Discrete(n_actions)
        self.observation_space = spaces.Box(low=0, high=255, shape=(3, 1), dtype=float) # verify wether the space is correct


    def step(self, action):
        scoreholder = self.score
        self.gameDisplay.fill(self.white)

        reward = 1
        done = False

        if action == -1:
            car_x_change = -5
        if action == 1:
            car_x_change = 5
        if action == 0:
            car_x_change = 0
        
        self.car_x+=car_x_change

        self.draw_track()
        self.update_track()

        self.car(self.car_x,self.car_y)
        
        if not self.did_it_crash(self.car_x, self.car_y):
            reward = 1
            self.score += reward
        else:
            done = True
            reward = -1
            self.__init__()

        lidar_state = self.draw_lidar(self.car_x, self.car_y)
        info = {'score': scoreholder}
        self.fps_clock.tick(self.fps)
        #pygame.display.update()

        ##TODO: return state
        return lidar_state, reward, done, info

    def reset(self):
        
        self.gameDisplay.fill(self.white)

        self.car_x = self.display_width*0.45
        self.car_y = self.display_height*0.75
        self.car_x_change = 0
        
        self.score = 0

        self.create_track()
        #TODO: return state
        return self.draw_lidar(car_x=self.car_x, car_y=self.car_y)

    def render(self, mode='human'):
        # Show score
        font = pygame.font.SysFont("comicsans", 40)
        showscore = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.gameDisplay.blit(showscore, (self.display_width - 10 - showscore.get_width(), 10))  

        # Update display
        pygame.display.update()

    def close(self):
        pygame.quit()
        pass

    #auxiliary functions for the game
    def car(self,x,y):
        self.gameDisplay.blit(self.carImg, (x,y))
    
    def crash():
        print('You Crashed!')

    #create initial straight track
    def create_track(self):
        self.track.clear()
        for i in range(16):
            self.track.append((200, self.display_height- i*self.cone_height)) #(x,y)
            self.track.append((600, self.display_height- i*self.cone_height)) #(x,y)

    def draw_track(self):
        for (x,y) in self.track:
            self.gameDisplay.blit(self.coneImg, (x,y))

    def did_it_crash(self,car_x, car_y):
        for (x,y) in self.track:
            if car_y < y + self.cone_height:
                if car_x > x and car_x < x + self.cone_width or car_x + self.car_width > x and car_x+self.car_width < x + self.cone_width:
                    return True
        return False

    def update_track(self):
        for i in range(len(self.track)):
            x, y = self.track.pop(0)
            self.track.append((x, y+self.cone_speed))
        x, y = self.track[0]
        if(y > self.display_height):
            self.track.pop(0)
            self.track.pop(0)
            value = random.randint(-1,1)
            x_last, y_last = self.track[28]
            x_pos = max(min(x_last + value*self.cone_width, self.display_width-self.track_width),0)
            self.track.append((x_pos,y_last-self.cone_height))
            self.track.append((x_pos + self.track_width ,y_last-self.cone_height))
    
    def front_lidar(self,car_x, car_y):
        front_lidar_x = car_x + self.car_width/2
        front_lidar_dist = car_y
        for (x,y) in self.track:
            if(front_lidar_x > x and front_lidar_x < x + self.cone_width):
                front_lidar_dist = min(front_lidar_dist, car_y-y-self.cone_height)

        pygame.draw.line(self.gameDisplay, self.black, (front_lidar_x, car_y), (front_lidar_x, car_y-front_lidar_dist))
        return front_lidar_dist

    def distance(self, x1, y1, x2, y2):
        return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

    def cone_crosses_line(self,start_x, start_y, end_x, end_y, x,y, right_side):
        a = (end_y - start_y) / (end_x-start_x)
        b = end_y - a*end_x

        cross_horizontal_x = (y + self.cone_height - b)/a
        cross_vertical_y = a*(x+ (self.cone_width if right_side else 0))+b

        if(cross_vertical_y >= y and cross_vertical_y <= y + self.cone_height):
            return True, x + ( self.cone_width if right_side else 0), cross_vertical_y 
        if(cross_horizontal_x >= x and cross_horizontal_x <= x + self.cone_width):
            return True, cross_horizontal_x, y + self.cone_height
        return False, 0, 0

    def left_lidar(self, car_x, car_y):
        start_lidar_x = car_x + self.car_width/2
        start_lidar_y = car_y
        display_side_x = 0
        display_side_y = start_lidar_y-tan(math.pi/6)*start_lidar_x
        extreme_x = display_side_x
        extreme_y = display_side_y
        lidar_dist = self.distance(start_lidar_x, start_lidar_y , display_side_x, display_side_y)
        
        counter = 0
        for (x,y) in self.track:
            if(counter % 2 == 0):
                answer, point_x, point_y = self.cone_crosses_line(start_lidar_x, start_lidar_y, display_side_x, display_side_y, x,y, True)
                if answer:
                    dist = self.distance(start_lidar_x, start_lidar_y, point_x, point_y)
                    if  dist < lidar_dist:
                        lidar_dist = dist
                        extreme_x = point_x
                        extreme_y = point_y
            counter+=1

        pygame.draw.line(self.gameDisplay, self.black, (start_lidar_x, start_lidar_y ), (extreme_x, extreme_y))
        return lidar_dist

    def right_lidar(self, car_x, car_y):
        start_lidar_x = car_x + self.car_width/2
        start_lidar_y = car_y
        display_side_x = self.display_width
        display_side_y = start_lidar_y-tan(math.pi/6)*(self.display_width-start_lidar_x)
        extreme_x = display_side_x
        extreme_y = display_side_y
        lidar_dist = self.distance(start_lidar_x, start_lidar_y , display_side_x, display_side_y)
        
        counter = 0
        for (x,y) in self.track:
            if(counter % 2 == 1):
                answer, point_x, point_y = self.cone_crosses_line(start_lidar_x, start_lidar_y, display_side_x, display_side_y, x,y, False)
                if answer:
                    dist = self.distance(start_lidar_x, start_lidar_y, point_x, point_y)
                    if  dist < lidar_dist:
                        lidar_dist = dist
                        extreme_x = point_x
                        extreme_y = point_y
            counter+=1

        pygame.draw.line(self.gameDisplay, self.black, (start_lidar_x, start_lidar_y ), (extreme_x, extreme_y))
        return lidar_dist

    def draw_lidar(self, car_x, car_y):
        return  self.left_lidar(car_x, car_y), self.front_lidar(car_x, car_y), self.right_lidar(car_x,car_y)
    