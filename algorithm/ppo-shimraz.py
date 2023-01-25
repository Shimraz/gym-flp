# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 14:24:30 2022

@author: Shimraz
"""

import gym
import gym_flp
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3 import DDPG
from stable_baselines3.common.env_util import make_vec_env
import matplotlib.animation as animation
import datetime
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
from stable_baselines3.common.vec_env import VecEnv, VecTransposeImage, DummyVecEnv
import imageio
from PIL import Image
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
instance = 'P6'
timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
environment = 'ofp'
algo = 'ppo'
mode = 'rgb_array'
train_steps = np.append(np.outer(10.0**(np.arange(4, 6)), np.arange(1,10,1)).flatten(), 10**6)
train_steps = [2e6]

vec_env = make_vec_env('ofp-v1', env_kwargs={'mode': mode, "instance":instance})
print("1")
wrap_env = gym.make('ofp-v1', mode = mode, instance=instance)
print("2")
wrap_env = VecTransposeImage(vec_env)
print("3")
vec_eval_env = make_vec_env('ofp-v1', env_kwargs={'mode': mode, "instance":instance})
print("4")

wrap_eval_env = gym.make('ofp-v1', mode = mode, instance=instance)
print("5")
wrap_eval_env = VecTransposeImage(vec_eval_env)
print("6")

experiment_results={}

for ts in train_steps:
    ts = int(ts)
    print('=====',ts)
    save_path = f"{timestamp}_{instance}_{algo}_{mode}_{environment}_movingavg_nocollisions_{ts}_exp4"
    
    eval_callback = EvalCallback(wrap_eval_env , 
                              best_model_save_path=f'./models/best_model/{save_path}',
                              log_path='./logs/', 
                              eval_freq=10000,
                              deterministic=True, 
                              render=False,
                              n_eval_episodes = 5)
    
    model = PPO("CnnPolicy", 
                wrap_env, 
                learning_rate=0.0003, 
                n_steps=2048, 
                batch_size=2048, 
                n_epochs=10, 
                gamma=0.99, 
                gae_lambda=0.95, 
                clip_range=0.2, 
                clip_range_vf=None, 
                ent_coef=0.0, 
                vf_coef=0.5, 
                max_grad_norm=0.5, 
                use_sde=False, 
                sde_sample_freq=- 1, 
                target_kl=None, 
                tensorboard_log=f'logs/{save_path}', 
                create_eval_env=False, 
                policy_kwargs=None, 
                verbose=1, 
                seed=None, 
                device='cuda',
                _init_setup_model=True)
    model.learn(total_timesteps=ts, callback=eval_callback)
    model.save(f"./models/{save_path}")
    '''
    # checkpoint_callback = CheckpointCallback(save_freq=10000, save_path=save_path,
    #                                               name_prefix='FLP_Training')
    # model = DDPG('CnnPolicy', wrap_env, verbose= 1)
        
    #     # Model Learning
    # model.learn(total_timesteps=ts, 
    #                 callback=checkpoint_callback, eval_env=wrap_eval_env)
    
    
    # model.save(f"./models/{save_path}")
    # model = DDPG.load("./FLP_Training/FLP_Training_v0_ttsteps_50000/FLP_Training_50000_steps.zip", env = wrap_eval_env)
    # model = DDPG.load("./models/220813_1225_P6_ddpg_rgb_array_ofp_movingavg_nocollisions_50000")'''
    # model = PPO.load(r"D:\Study\Arbeit IPEM\gym-flp\algorithm\models\220828_0220_P6_ppo_rgb_array_ofp_movingavg_nocollisions_1000000.zip")
    # model = PPO.load(r"D:\Study\Arbeit IPEM\gym-flp\algorithm\models\220828_1417_P6_ppo_rgb_array_ofp_movingavg_nocollisions_2000000.zip")
    
    fig, (ax1,ax2) = plt.subplots(2,1)
    
    obs = wrap_env.reset()
    start_cost =  wrap_env.get_attr("last_cost")[0]  #getattr(wrap_env,"last_cost")
    #print(start_cost)
    rewards = []
    mhc = []
    images = []
    gain = 0
    gains = []
    actions = []
    done = False
    while done != True:
        action, _states = model.predict(obs, deterministic = True)
        actions.append(action)
        obs, reward, done, info = wrap_env.step(action)
        
        gain += reward
        img =  wrap_env.render(mode='rgb_array')
        rewards.append(reward)
        # print(info)
        mhc.append(info[0]['mhc'])
        gains.append(gain)
        images.append(img)
    # print(mhc)
    # print(rewards)
    final_cost = mhc[-1]
    # print("finalcost",final_cost)
    cost_saved = final_cost-start_cost
    cost_saved_rel = 1-(start_cost/final_cost)
    # print(cost_saved, cost_saved_rel, '%')
    experiment_results[ts]=[cost_saved, cost_saved_rel]
    ax1.plot(rewards)
    ax2.plot(mhc)
    # print(actions)
    imageio.mimsave(f'gifs/{save_path}_test_env.gif', [np.array(img.resize((200,200),Image.NEAREST)) for i, img in enumerate(images) if i%2 == 0], fps=29)
    plt.show()
    wrap_eval_env.close()
    del model
y = np.array([i for i in experiment_results.values()])

# print(experiment_results, y)
# print(train_steps, abs(y[:,0]))
fig1, axs = plt.subplots(1,1)
axs.plot(train_steps,abs(y[:,0]),)
plt.title("Plot flp")
# print("end")