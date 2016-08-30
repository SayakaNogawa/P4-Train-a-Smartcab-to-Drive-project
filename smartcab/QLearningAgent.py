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
        # TODO: Initialize any additional variables here
        self.dedline = self.env.get_deadline(self)
        self.possible_action = Environment.valid_actions
        self.Q_dict = dict()
        self.epsilon = 0.05
        self.alpfa = 0.9
        self.gamma = 0
        self.state = None
        self.action = None
        self.next_waypoint = None
        self.reward = None
        self.cum_rewards = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.next_waypoint = None

        self.state = None
        self.next_state = None

        self.action = None

        self.reward = 0
        self.cum_rewards = 0

    def get_Q(self, state, action):
        key = (state, action)
        return self.Q_dict.get(key, 10.0)

    def get_maxQ(self, state):
        """
        Returns maxQ(state,action)
        """
        best_Q = [self.get_Q(state, action) for action in self.possible_action]
        return max(best_Q)

    def get_action(self, state):
        """
        Choose the best action with Epsilon-Greedy approach
        """
        #return highest arm

        if random.random() > self.epsilon:
            action = random.choice(self.possible_action)
            best_Q = [self.get_Q(state, action) for action in self.possible_action]

            for action in self.possible_action:

                if self.next_state == self.state and self.get_Q(state, action) > max(best_Q):
                    best_action = action
                    best_Q = get_Q[(state, action)]
                    index = random.choice(best_action)
                else:
                    index = best_Q.index(max(best_Q))
                    action = self.possible_action[index]

        else:
            return action
            
    def update_Q(self, state, action, nextState, reward):
        """
        Q-Value update
        """
        key = (state, action)
        if (key not in self.Q_dict):
            self.Q_dict[key] = 10.0
        else:
            self.Q_dict[key] = self.Q_dict[key] + self.alpfa * (reward + self.gamma * self.get_maxQ(nextState) - self.Q_dict[key])

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        action_okay = True

        if self.next_waypoint == 'right':
            if inputs['light'] == 'red' and inputs['left'] == 'forward':
                action_okay = False
        elif self.next_waypoint == 'forward':
            if inputs['light'] == 'red':
                action_okay = False
        elif self.next_waypoint == 'left':
            if inputs['light'] == 'red' or (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
                action_okay = False

        if action_okay == False:
            action = None

        self.new_state = inputs
        self.new_state['next_waypoint'] = self.next_waypoint
        self.new_state = tuple(sorted(self.new_state.items()))
        #self.next_state = (inputs, self.next_waypoint, deadline)

        # TODO: Select action according to your policy
        action = self.get_action(self.next_state)

        # Execute action and get reward
        next_reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.reward != None:
            self.update_Q(self.state, self.action, self.next_state, self.reward)

        self.state = self.next_state
        self.action = action
        self.reward = next_reward
        self.cum_rewards += next_reward

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
