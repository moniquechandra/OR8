import random
import time
import logging
import matplotlib.pyplot as plt
from attributes.product_details import Parameters
from attributes.to_be import To_Be

tb = To_Be()
pm = Parameters()

# Initiate a logger to log necessary information
log_format = "%(asctime)s - %(module)s - %(message)s"
logging.basicConfig(filename='log_file.log', level=logging.INFO, format=log_format, filemode='w')

# Function to generate neighboring solutions
def generate_neighbor(current_solution):
    # Randomly select a DC to move states from
    dc_list = list(current_solution.keys())
    while True:
        from_dc = random.choice(dc_list)
        if len(current_solution[from_dc]) > 1:
            break

    # Randomly select a DC as destination (avoid moving to an empty DC)
    while True:
        to_dc = random.choice(dc_list)
        if (to_dc != from_dc):
            break

    # Randomly select a subset of states from source DC
    # num_state_to_move = random.randint(1, len(from_dc))
    state_to_move = random.sample(current_solution[from_dc], 1)[0]

    states_from_dc = current_solution[from_dc]
    states_to_dc = current_solution[to_dc]
        
    states_to_dc.append(state_to_move)
    states_from_dc.remove(state_to_move)

    return current_solution

def add_tabu(tabu_list, move, tenure):
        tabu_list.append((move, tenure))
        if len(tabu_list) > tenure:
            tabu_list.pop(0)

# Tabu Search algorithm
def tabu_search(initial_solution, max_iterations):
    try:
        start_algorithm = time.time()
        current_solution = initial_solution.copy()
        current_cost = pm.total_costs(current_solution)[0]
        best_cost = current_cost
        tabu_list = []
        best_objective_value_list = []
        current_objective_value_list = []
        
        for iteration in range(max_iterations):
            # n =   # Generate a number of neighbors
            neighborhood = [(generate_neighbor(current_solution), pm.total_costs(generate_neighbor(current_solution))[0])]
            # neighborhood.sort(key=lambda x: x[1])  # Sort neighbors by cost

            for neighbor, cost in neighborhood:
                move = (current_solution, neighbor)
                if move not in tabu_list:  # Aspiration criteria
                    current_cost = cost
                    current_objective_value_list.append(cost)
                    print(iteration, current_cost, best_cost)
                    add_tabu(tabu_list, move, tabu_tenure)

                    if cost < best_cost:
                        best_solution = neighbor
                        best_objective_value_list.append(cost)
                        best_cost = cost
                        logging.info(f"Improving allocation = {best_solution}")
                    break
    
        # Calculate the algorithm time
        end_algorithm = time.time()
        elapsed_algorithm = end_algorithm - start_algorithm

        # Log the computation time and time complexity of the algorithm
        logging.info(f"Computation time = {elapsed_algorithm}")
        logging.info(f"\nTime complexity of the algorithm for {max_iterations} iterations = {elapsed_algorithm / max_iterations} seconds")
        logging.info(f"Best solution = {best_solution}")
        logging.info(f"Total costs = {pm.total_costs(best_solution, tb.as_is_dc)[0]}")
        # logging.info(f"Difference of costs = {total_penalty - pm.total_costs(best_solution, self.as_is_dc)[0]}")

        # Plot the improvements of the objective value (each dot represent each product)
        plt.plot(best_objective_value_list, marker="o", label="best solution")
        plt.plot(current_objective_value_list, label="current solution")
        plt.title(f"Objective Value Changes in Tabu Search with {max_iterations} iterations, tenure = 5")
        plt.xlabel("Number of iterations")
        plt.legend()
        plt.show()

    except UnboundLocalError:
        best_solution = initial_solution.copy()
    
    return best_cost

# Define the initial solution
# initial_solution = {'WA': ['CT', 'DE', 'HI', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'RI', 'VT', 'DC'], 'ND': ['IA', 'IN', 'MN', 'MT', 'ND', 'NE', 'SD', 'WI'],
#                     'IL': ['LA', 'NM', 'OK', 'TX'], 'TX': ['IL', 'MI'], 
#                     'TN': ['AL', 'AR', 'FL', 'GA', 'KS', 'KY', 'MO', 'MS', 'NC', 'OH', 'PA', 'SC', 'TN', 'VA', 'WV'],
#                     'UT': ['AZ', 'CA', 'CO', 'NV', 'UT', 'WY'], 
#                     'NY': ['AK', 'ID', 'OR', 'WA']}
         
initial_solution = tb.greedy_dc_allocation
# Define the tabu Search parameters
tabu_tenure = 5
max_iterations = 200

# Execute the algorithm
best_cost = tabu_search(initial_solution, max_iterations)

# print("Best Allocation:", best_solution)
print("Best Cost:", best_cost)
