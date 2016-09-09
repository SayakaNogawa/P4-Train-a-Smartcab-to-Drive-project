import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.dedline = self.env.get_deadline(self)
        self.possible_actions = Environment.valid_actions
        self.Q_dict = dict() # Q(s,a)

        self.alpha = 0.8 # learning rate
        self.gamma = 0.4 # discount maxQ(s',a')
        self.epsilon = 0.1 # pick a random action
        self.deg_epsilon = 0.01 # degradation of ramdom action

        self.state = None
        self.next_state = None
        self.action = None
        self.reward = None
        self.cum_rewards = 0

        self.num_moves = 0
        self.penalty = 0

        self.next_waypoint = None

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.state = None
        self.next_state = None
        self.action = None
        self.reward = 0
        self.cum_rewards = 0

        self.num_moves = 0
        self.penalty = 0

        self.next_waypoint = None

    def qval(self, state, action):
        # Q value (s,a)
        key = (state, action)
        return self.Q_dict.get(key, 2.0)

    def maxQ(self, state):
        # Returns maxQ(s,a)
        q = [self.qval(state, a) for a in self.possible_actions]
        return max(q)

    def epsilon_greedy(self, state):
        # Choose the best action with Epsilon-Greedy approach
        if random.random() < self.epsilon:
            self.epsilon -= self.deg_epsilon
            max_action = random.choice(self.possible_actions)

        else:
            max_action = self.possible_actions[0]
            max_reward = None
            # Find maximum
            for action in self.possible_actions:
                cur_reward = self.qval(state, action)
                if cur_reward > max_reward:
                    max_reward = cur_reward
                    max_action = action # max_action is argmax
                elif cur_reward == max_reward:
                    max_action = random.choice([max_action, action])
        return max_action

    def Q_learn(self, state, action, nextState, reward):
        key = (state, action)
        if (key not in self.Q_dict):
			# initialize the q values
			self.Q_dict[key] = 2.0
        else:
            self.Q_dict[key] = self.Q_dict[key] + self.alpha * (reward + self.gamma * self.maxQ(nextState) - self.Q_dict[key])

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        self.next_state = (tuple(inputs.values()), self.next_waypoint)
        #self.next_state = (inputs["light"], self.next_waypoint)

        # Update action
        next_action = self.epsilon_greedy(self.next_state)

        # Execute action and get reward
        next_reward = self.env.act(self, next_action)

        # Learn policy based on state, action, reward
        if self.reward != None:
            # update Q-value
            self.Q_learn(self.state, self.action, self.next_state, self.reward)

        # Update stats
        self.state = self.next_state
        self.action = next_action
        self.reward = next_reward
        self.cum_rewards += next_reward
        self.num_moves += 1

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, next_action, next_reward)  # [debug]

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=.0001, display=False)  # create simulator (uses pygame when display=True, if available)
    # To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    # Status reports
    print "Win: {} / ".format(e.win) + "Lose: {} ".format(e.lose) # Success rates
    print "Penalty: {} / ".format(e.penalty) + "Reward: {} / ".format(a.cum_rewards) + "Move: {} ".format(a.num_moves) # Other evaluation

if __name__ == '__main__':
    run()
