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
        self.state = None
        self.action = None
        self.next_waypoint = None
        self.reward = None

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None
        self.action = None
        self.next_waypoint = None
        self.reward = 0

    def get_Q(self, state, action):
        key = (state, action)
        return self.Q_dict.get(key, 10.0)

    def get_maxQ(self, state):
         """
         Returns maxQ(state,action)
         """
        best_Q = [self.get_Q(state, action) for action in self.possible_action]
        return max(best_Q)

    def get_policy(self, state):
        """
        Choose the best action
        """
        best_action = random.choice(self.possible_action)
        qval = qtable[(current_state, best_action)]
        for all (state, action) pairs in qtable:
            if state == current_state and qtable[(state, action)] > qval:
                best_action = action
                qval = qtable[(state, action)]
            else:
                continue
        return best_action

    def update_Q(self, state, action, next_state, reward):
        

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

        self.state = (inputs, self.next_waypoint, deadline)

        # TODO: Select action according to your policy
        action = random.choice(Environment.valid_actions)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.update_Qvalue(self.state, action, reward)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


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
