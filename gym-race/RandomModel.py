import gym
import random

env = gym.make("gym_race:race-v0")

episodes = 10
for episode in range(1, episodes+1):
    state = env.reset()
    done = False
    score = 0
    
    while not done:
        env.render()
        action = random.choice([-1,0,1])
        n_state, reward, done, info = env.step(action)
        score+=reward
    print('Episode:{} score:{}'.format(episode, score))