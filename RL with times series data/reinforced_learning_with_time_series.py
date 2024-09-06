# -*- coding: utf-8 -*-
"""Reinforced Learning with Time Series.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IhHwcNRH6AuW30kn9mePHpYDhFFBmEVq
"""

'''
The goal of this project is to use Reinforced Learning together with time series data to predict the outcome of fuel prices.
We will begin with data validation and cleaning.
Then we will dive into Exploratory Data Analysis and Visualization to see insights
'''

#installing baselines3
!pip install stable-baselines3

#installing gym
!pip install gymnasium

#importing the relevant libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from stable_baselines3 import DQN
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3.common.env_checker import check_env

#reading the dataset into a csv
file_path =r'/content/fuel price.csv'

fuel_prices = pd.read_csv(file_path)

#printing the first five rows
fuel_prices.head()

#check for duplicates
fuel_prices.duplicated(subset='Unnamed: 0').sum()

'''
The dataset has no duplicate rows hence we can proceed with data validation and cleaning.
'''

#check the info of the dataset
fuel_prices.info()

'''
From the above, we can see that there are no missing values in all the rows. However, the 'Date' column is of the object data
type.
We will convert the  column to a date data type. Then we will continue to determine the relationship between the columns
'''

#converting the date column
fuel_prices['Date'] = pd.to_datetime(fuel_prices['Date'], format='%d/%m/%Y')

#checking the dataframe again
fuel_prices.info()

#rename the column names
rename_columns = {
    'Pump price in pence/litre (ULSP)':'Pump price (ULSP)',
    'Pump price in pence/litre (ULSD)':'Pump price (ULSD)',
    'Duty rate in pence/litre (ULSP)':'Duty rate (ULSP)',
    'Duty rate in pence/litre (ULSD)':'Duty rate (ULSD)',
}

fuel_prices.rename(columns=rename_columns, inplace=True)

#check the info
fuel_prices.info()

#check the relationionship between the prices and the external factors
columns = fuel_prices[['Pump price (ULSP)', 'Pump price (ULSD)', 'Duty rate (ULSP)', 'Duty rate (ULSD)', 'VAT percentage rate (ULSP)', 'VAT percentage rate (ULSD)']]

#create a pairplot
sns.pairplot(data=columns)

#show the plot
plt.show()

#checking the corrrelation between the columns
columns.corr()

'''
From the above visualitation and dataframe. We can see that there is a strong relationship between the Pump Prices (ULSP) and the Pump Prices (ULSD), the Pump price
and their respective duty rates. There is a weak relationship between the duty rates and the VAT rates.
Next we will drop the irrelevant columns and proceed to see the distribution of the dataset
'''

#dropp irrelevant column
fuel_prices.drop(['Unnamed: 0'], axis=1, inplace=True)

#check the dataframe
fuel_prices.head()

#visualizing the distribution for each column
columns = ['Pump price (ULSP)', 'Pump price (ULSD)', 'Duty rate (ULSP)', 'Duty rate (ULSD)', 'VAT percentage rate (ULSP)', 'VAT percentage rate (ULSD)']
for column in columns:
    plt.figure(figsize=(8,12))
    sns.histplot(data=fuel_prices, x=column, kde=True)
    plt.title(f'Distribution of {column}')

    #set tight_layout
    plt.tight_layout()

    #show the plot
    plt.show()

'''
From the visualization we can see that the distributions is not a normal one. this however does not affect the data for reinforcement learning.
Next we will look at the descriptive statistics, check for outliers and handle them if it arises.
'''

#check the descriptive statistics
fuel_prices.describe()

#visualizing the spread using boxplot
fuel_prices.boxplot(figsize=(10,10))

#show the plot
plt.show()

'''
From the descriptive statistics and the visualization above, there are no outliers in the dataset.
Next we will explore the trends in the fuel prices and their respective external factors.
'''

# Plotting fuel prices ULSP and external factors over time
plt.figure(figsize=(10, 6))
plt.plot(fuel_prices['Date'], fuel_prices['Pump price (ULSP)'], label='ULSP Price')
plt.plot(fuel_prices['Date'], fuel_prices['Duty rate (ULSP)'], label='ULSP Duty Rate', linestyle='--')
plt.plot(fuel_prices['Date'], fuel_prices['VAT percentage rate (ULSP)'], label='ULSP VAT Rate', linestyle='--')

plt.xlabel('Date')
plt.ylabel('Price (Pence per Litre)')
plt.title('Fuel Prices (ULSP) and External Factors Over Time')
plt.legend()
plt.show()

# Plotting fuel prices ULSD and external factors over time
plt.figure(figsize=(10, 6))
plt.plot(fuel_prices['Date'], fuel_prices['Pump price (ULSD)'], label='ULSD Price')
plt.plot(fuel_prices['Date'], fuel_prices['Duty rate (ULSD)'], label='ULSD Duty Rate', linestyle='--')
plt.plot(fuel_prices['Date'], fuel_prices['VAT percentage rate (ULSD)'], label='ULSD VAT Rate', linestyle='--')

plt.xlabel('Date')
plt.ylabel('Price (Pence per Litre)')
plt.title('Fuel Prices (ULSD) and External Factors Over Time')
plt.legend()
plt.show()

'''
From the above we see that fuel prices have sudden spikes and dips. However their respective duty rates and VAT rates are somewhat stable.
This means that the VAT rates and Duty rates do not have strong influence on the fuel prices.
Next we will see try new feature exchange rate. We will use numpy random function to generate new features and add these to our dataset.
We will add the exchange rate values 1.2 and 1.6 indicating a low and high exchange rate respectively.
'''

# Set random seed for reproducibility
np.random.seed(42)

# Generate random exchange rate values (baseline, between 1.2 and 1.6)
num_rows = len(fuel_prices)
exchange_rates = np.random.uniform(low=1.2, high=1.6, size=num_rows)

# Introduce random spikes/dips
# Choose 5% of the data points to have spikes/dips
num_spikes = int(0.05 * num_rows)
spike_indices = np.random.choice(num_rows, num_spikes, replace=False)

# Apply spikes (e.g., multiply by a random factor between 1.5 and 3.0 for spikes)
exchange_rates[spike_indices] *= np.random.uniform(1.5, 3.0, size=num_spikes)

# You can also introduce dips (by multiplying by 0.5 to 0.8)
dip_indices = np.random.choice(num_rows, num_spikes, replace=False)
exchange_rates[dip_indices] *= np.random.uniform(0.5, 0.8, size=num_spikes)

# Add the modified exchange rates to the DataFrame as a new column
fuel_prices['Exchange Rate'] = exchange_rates

# Check the first few rows to verify the new column with spikes and dips
fuel_prices.head()

# Plott fuel prices ULSP and external factors over time again
plt.figure(figsize=(10, 6))
plt.plot(fuel_prices['Date'], fuel_prices['Pump price (ULSP)'], label='ULSP Price')
plt.plot(fuel_prices['Date'], fuel_prices['Duty rate (ULSP)'], label='ULSP Duty Rate', linestyle='--')
plt.plot(fuel_prices['Date'], fuel_prices['VAT percentage rate (ULSP)'], label='ULSP VAT Rate', linestyle='--')
plt.plot(fuel_prices['Date'], fuel_prices['Exchange Rate'], label='Exchange Rate', linestyle='--')

plt.xlabel('Date')
plt.ylabel('Price (Pence per Litre)')
plt.title('Fuel Prices (ULSP) and External Factors Over Time')
plt.legend()
plt.show()

'''
Adding a new feature did not work. We will proceed without the 'Exchange Rate' feature.
We will drop the 'Exchange Rate' column and proceed with the reinforcement learning.
'''

#drop the exchange rate column
fuel_prices.drop(['Exchange Rate'], axis=1, inplace=True)

#check the dataframe
fuel_prices.head()

'''
We will now move on to the next step of this project: Reinforcement Learning.
First we will create an environment for the reinforcement learning and define the actions and observations.
'''

class FuelPriceEnv(gym.Env):  # Inherit from gymnasium.Env
    def __init__(self, data):
        super(FuelPriceEnv, self).__init__()
        self.data = data
        self.current_step = 0

        # Define action and observation space
        self.action_space = spaces.Discrete(5)  # Actions: Buy ULSP, Sell ULSP, etc.
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)

    def reset(self, seed=None):
      self.current_step = 0
      observation = self._next_observation()
      info = {}
      return observation, info

    def _next_observation(self):
        return np.array([
            self.data['Pump price (ULSP)'].iloc[self.current_step],
            self.data['Pump price (ULSD)'].iloc[self.current_step],
            self.data['Duty rate (ULSP)'].iloc[self.current_step],
            self.data['Duty rate (ULSD)'].iloc[self.current_step],
            self.data['VAT percentage rate (ULSP)'].iloc[self.current_step],
            self.data['VAT percentage rate (ULSD)'].iloc[self.current_step]
        ], dtype=np.float32) # Explicitly set the data type to float32

    def step(self, action):
        self.current_step += 1
        ulsp_price_current = self.data['Pump price (ULSP)'].iloc[self.current_step - 1]
        ulsp_price_next = self.data['Pump price (ULSP)'].iloc[self.current_step]
        ulsd_price_current = self.data['Pump price (ULSD)'].iloc[self.current_step - 1]
        ulsd_price_next = self.data['Pump price (ULSD)'].iloc[self.current_step]

        reward = 0
        if action == 1:  # Buy ULSP
            reward = ulsp_price_next - ulsp_price_current
        elif action == 2:  # Sell ULSP
            reward = ulsp_price_current - ulsp_price_next
        elif action == 3:  # Buy ULSD
            reward = ulsd_price_next - ulsd_price_current
        elif action == 4:  # Sell ULSD
            reward = ulsd_price_current - ulsd_price_next

        done = False
        if self.current_step >= len(self.data) - 1:
            done = True

        # Separate done into terminated and truncated
        terminated = done
        truncated = False

        obs = self._next_observation()
        # Return five values: obs, reward, terminated, truncated, info
        return obs, reward, terminated, truncated, {}

    def render(self, mode='human'):
        pass

# Create the environment using your dataset
env = FuelPriceEnv(fuel_prices)

# Check if the environment is valid
check_env(env)

# Initialize the DQN model
model = DQN('MlpPolicy', env, verbose=1)

# Train the agent
model.learn(total_timesteps=10000)

# Save the model
model.save("fuel_price_dqn_model")

# Load the trained model
model = DQN.load("fuel_price_dqn_model")

# Initialize cumulative reward for tracking
cumulative_reward = 0
episodes = 10  # Number of episodes to test

for episode in range(episodes):
    obs, info = env.reset()  # Reset the environment at the start of each episode
    episode_reward = 0

    for _ in range(1000):
        # The model selects the next action
        action, _states = model.predict(obs)

        # The environment takes the action and returns the next observation and reward
        obs, reward, done, _, _ = env.step(action)

        # Accumulate the reward for the current episode
        episode_reward += reward

        if done:
            break

    # Track the total reward across all episodes
    cumulative_reward += episode_reward
    print(f"Episode {episode + 1} reward: {episode_reward}")

# Average reward over all episodes
average_reward = cumulative_reward / episodes
print(f"Average reward over {episodes} episodes: {average_reward}")

#Tracking the win rate of the agent
wins = 0
losses = 0

for episode in range(episodes):
    obs, info = env.reset()
    episode_reward = 0

    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, reward, done, _, _ = env.step(action)
        episode_reward += reward

        if done:
            break

    if episode_reward > 0:
        wins += 1
    else:
        losses += 1

print(f"Wins: {wins}, Losses: {losses}")