import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Security
from pydantic import BaseModel, Field
from typing import List
import os
from fastapi.security import APIKeyHeader


from env import TimeEnv
from agent import train_agent, get_greedy_route

# 1. Define the API Schema
class TSPRequest(BaseModel):
    # Expects a 2D list of floats representing the time matrix
    time_matrix: List[List[float]]
    start_node: int = 0
    # Add a safety limit to episodes so a rogue API call doesn't hang the server
    n_episodes: int = Field(default=50000, le=100000)

class TSPResponse(BaseModel):
    best_route: List[int]
    total_time: float


api_key_header = APIKeyHeader(name="X-API-Token", auto_error=True)

EXPECTED_TOKEN = os.environ.get("API_AUTH_TOKEN", "local-dev-token")


def verify_token(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Token")
    return api_key


# 2. Initialize the FastAPI App
app = FastAPI(
    title="TSP Reinforcement Learning Solver",
    description="An API that uses Tabular Q-Learning to solve routing optimizations.",
    version="1.0.0"
)


# 3. Define the POST Endpoint
@app.post("/solve", response_model=TSPResponse, dependencies=[Security(verify_token)])
def solve_tsp(request: TSPRequest):
    # Convert incoming JSON list to NumPy array
    matrix = np.array(request.time_matrix, dtype=float)

    # Validation: Matrix must be square
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise HTTPException(status_code=400, detail="Time matrix must be a square 2D array.")

    n_nodes = matrix.shape[0]

    # Validation: Start node must be within bounds
    if request.start_node < 0 or request.start_node >= n_nodes:
        raise HTTPException(status_code=400, detail=f"start_node must be between 0 and {n_nodes - 1}")

    try:
        # Inject data into the environment
        env = TimeEnv(matrix, start_node=request.start_node)

        # Train the agent
        trained_Q_table = train_agent(env, n_episodes=request.n_episodes)

        # Extract the best route
        best_route, best_time = get_greedy_route(env, trained_Q_table)

        return TSPResponse(best_route=best_route, total_time=best_time)

    except Exception as e:
        # Catch any unexpected RL math errors to prevent silent server crashes
        raise HTTPException(status_code=500, detail=f"Internal RL Engine Error: {str(e)}")


# For local testing only
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)