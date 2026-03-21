import numpy as np

def train_agent(env, n_episodes=100000, alpha=0.1, gamma=1.0, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.999):

    state_space_size = env.n * (1 << env.n)
    action_space_size = env.n

    Q = np.zeros((state_space_size, action_space_size))

    for episode in range(n_episodes):
        state = env.reset()
        done = False

        while not done:
            actions = env.available_actions()

            if np.random.rand() < epsilon:
                action = np.random.choice(actions)
            else:
                q_vals = Q[state, actions]
                action = actions[np.argmax(q_vals)]

            next_state, reward, done, _ = env.step(action)

            next_actions = env.available_actions()
            if done or not next_actions:
                best_next_q = 0.0
            else:
                best_next_q = np.max(Q[next_state, next_actions])

            td_target = reward + gamma * best_next_q
            Q[state, action] = (1 - alpha) * Q[state, action] + alpha * td_target

            state = next_state

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return Q


def get_greedy_route(env, Q):
    state = env.reset()
    done = False
    route = [env.current_node]

    while not done:
        actions = env.available_actions()
        q_vals = Q[state, actions]
        action = actions[np.argmax(q_vals)]
        next_state, reward, done, _ = env.step(action)
        route.append(env.current_node)
        state = next_state

    return route, env.total_time





