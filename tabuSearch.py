import random
import time
import logging
import copy
import matplotlib.pyplot as plt
from product_details import Parameters
from to_be import To_Be

tb = To_Be()
pm = Parameters()

as_is_dc = {
        "NY": ['CT', 'DC', 'DE', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT'],
        "ND": ['MN', 'MT', 'ND', 'SD', 'WY'],
        "IL": ['HI', 'IA', 'IL', 'IN', 'KS', 'KY', 'MI', 'MO', 'NE', 'OH', 'VA', 'WI', 'WV'],
        "TN": ['AL', 'FL', 'GA', 'NC', 'SC', 'TN'],
        "WA": ['AK', 'ID', 'OR', 'WA'],
        "TX": ['AR', 'AZ', 'LA', 'MS', 'NM', 'OK', 'TX'],
        "UT": ['CA', 'CO', 'NV', 'UT'],
        "PA": [],
        "KS": [],
        "CA": []}

# Initiate a logger to log necessary information
log_format = "%(asctime)s - %(module)s - %(message)s"
logging.basicConfig(filename='log_file.log', level=logging.INFO, format=log_format, filemode='w')

# Function to generate neighboring solutions
def generate_neighbor(current_solution):
    neighbor_solution = copy.deepcopy(current_solution)  # Use deep copy to avoid unintentional changes
    # Randomly select a DC to move states from
    dc_list = list(neighbor_solution.keys())
    while True:
        from_dc = random.choice(dc_list)
        if neighbor_solution[from_dc]:
            break

    # Randomly select a DC as destination (avoid moving to the same DC)
    while True:
        to_dc = random.choice(dc_list)
        if to_dc != from_dc:
            break

    # Randomly select a state from source DC
    state_to_move = random.choice(neighbor_solution[from_dc])

    # Move the state
    neighbor_solution[from_dc].remove(state_to_move)
    neighbor_solution[to_dc].append(state_to_move)

    return neighbor_solution

def add_tabu(tabu_list, move, tenure):
    tabu_list.append((move, tenure))
    if len(tabu_list) > tenure:
        tabu_list.pop(0)

# Function to check if a move is tabu
def is_tabu(move, tabu_list):
    for tabu_move, _ in tabu_list:
        if move == tabu_move:
            return True
    return False

# Tabu Search algorithm
def tabu_search(initial_solution, max_iterations, tabu_tenure):
    try:
        start_algorithm = time.time()
        current_solution = copy.deepcopy(initial_solution)
        current_cost = pm.total_costs(current_solution, as_is_dc)[0]
        best_cost = current_cost
        best_solution = copy.deepcopy(current_solution)
        tabu_list = []
        best_objective_value_list = []
        current_objective_value_list = []

        for iteration in range(max_iterations):
            neighbor = generate_neighbor(current_solution)
            cost = pm.total_costs(neighbor, as_is_dc)[0]

            move = (tuple(sorted(current_solution.items())), tuple(sorted(neighbor.items())))  # Convert dict to sorted tuple for tabu list
            if not is_tabu(move, tabu_list) or cost < best_cost:  # Aspiration criteria
                current_solution = copy.deepcopy(neighbor)
                current_cost = cost
                current_objective_value_list.append(cost)

                if cost < best_cost:
                    best_solution = copy.deepcopy(neighbor)
                    best_cost = cost

                best_objective_value_list.append(best_cost)
                print(iteration, current_cost, best_cost)
                add_tabu(tabu_list, move, tabu_tenure)
            else:
                current_objective_value_list.append(current_cost)
                best_objective_value_list.append(best_cost)

        # Calculate the algorithm time
        end_algorithm = time.time()
        elapsed_algorithm = end_algorithm - start_algorithm

        # Log the computation time and time complexity of the algorithm
        logging.info(f"Best allocation = {best_solution}")
        logging.info(f"Total costs = {pm.total_costs(best_solution, as_is_dc)[0]}")
        logging.info(f"Computation time = {elapsed_algorithm}")
        logging.info(f"Time complexity of the algorithm for {max_iterations} iterations = {elapsed_algorithm / max_iterations} seconds")
        
        # Plot the improvements of the objective value (each dot represent each product)
        plt.plot(best_objective_value_list, marker="o", label="best solution")
        plt.plot(current_objective_value_list, label="current solution")
        plt.title(f"Objective Value Changes in Tabu Search with {max_iterations} iterations, tenure = {tabu_tenure}")
        plt.xlabel("Number of iterations")
        plt.legend()
        plt.show()

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        best_solution = copy.deepcopy(initial_solution)

    return best_cost, best_solution

# Define the initial solution
# initial_solution = tb.greedy_dc_allocation
initial_solution = {'WA': ['AK', 'ID', 'MT', 'OR', 'WA'],
                    'TN': ['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'OH', 'SC', 'VA', 'WV'],
                    'TX': ['AR', 'LA', 'NM', 'OK', 'TN', 'TX'],
                    'UT': ['AZ', 'CO', 'NV', 'UT', 'WY'], 'CA': ['CA'],
                    'NY': ['CT', 'DE', 'MA', 'ME', 'NH', 'NJ', 'NY', 'RI', 'VT'],
                    'PA': ['HI', 'MD', 'PA', 'DC'], 'KS': ['IA', 'KS', 'MO', 'NE'],
                    'IL': ['IL', 'MI', 'MN'], 'ND': ['IN', 'ND', 'SD', 'WI']}


# Define the Tabu Search parameters
tabu_tenure = 7
max_iterations = 2000

# Execute the algorithm
cost, solution = tabu_search(initial_solution, max_iterations, tabu_tenure)

print("Best Cost:", cost)
print("Best Solution:", solution)
