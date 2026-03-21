class TimeEnv:

    def __init__(self, time_matrix, start_node=0):
        self.time_matrix = time_matrix
        self.n = time_matrix.shape[0]
        self.start_node = start_node
        self.reset()

    def _state_id(self):
        return self.current_node + self.n * self.visited_mask

    def reset(self):
        self.current_node = self.start_node
        self.visited_mask = 1 << self.start_node
        self.total_time = 0.0
        self.steps = 0
        return self._state_id()

    def available_actions(self):
        actions = []

        if self.visited_mask != (1 << self.n) - 1: # Don't get where the 6 is coming from?
            for nxt in range(self.n):
                if not (self.visited_mask & (1 << nxt)):
                    actions.append(nxt)
        else:
            if self.current_node != self.start_node:
                actions = [self.start_node]

        return actions

    def step(self, action):

        assert 0 <= action < self.n

        done = False

        time_cost = self.time_matrix[self.current_node, action]
        self.total_time += time_cost
        reward = -time_cost
        self.current_node = action # Don't get this?

        if not (self.visited_mask & (1 << action)):
            self.visited_mask |= (1 << action)

        self.steps += 1

        if self.visited_mask == (1 << self.n) - 1 and self.current_node == self.start_node:
            done = True

        if self.steps > self.n * 3:
            done = True

        return self._state_id(), reward, done, {}