import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as m
import logging
import time
import random

from to_be import To_Be
from prod_details import Parameters
tb = To_Be()
pm = Parameters()

# Initiate a logger to log necessary information
log_format = "%(asctime)s - %(module)s - %(message)s"
logging.basicConfig(filename='log_file.log', level=logging.INFO, format=log_format, filemode='w')

# Choose any starting feasible solution
as_is_dc = tb.as_is_dc
initial_solution = {'WA': ['AK', 'ID', 'MT', 'OR', 'WA'], 'TN': ['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'OH', 'SC', 'VA', 'WV'], 'TX': ['AR', 'LA', 'NM', 'OK', 'TN', 'TX'], 'UT': ['AZ', 'CO', 'NV', 'UT', 'WY'], 'CA': ['CA'], 'NY': ['CT', 'DE', 'MA', 'ME', 'NH', 'NJ', 'NY', 'RI', 'VT'], 'PA': ['HI', 'MD', 'PA', 'DC'], 'KS': ['IA', 'KS', 'MO', 'NE'], 'IL': ['IL', 'MI', 'MN'], 'ND': ['IN', 'ND', 'SD', 'WI']}


class SimulatedAnnealing:

    # Set the initial objective value as the reference for improvement
    initial_obj_value = pm.total_costs(initial_solution)
    # Make a copy of the initial solution to avoid modifying it directly
    current_solution = initial_solution.copy()
    
    # Define the initial temperature, cooling rate, and tmax as the parameter of the algorithm
    initial_temperature = 10000
    cooling_rate = 0.7
    tmax = 200

    # Initiate the lists for plotting the changes per iteration
    best_objective_value_list = [initial_obj_value]
    current_objective_value_list = [initial_obj_value]
    temperature_list = [initial_temperature]

    def move(self, state, dc_allocation, from_dc, to_dc):
        # Feasible move: Move the state from one DC to another, then return the new DC allocation.
        # while True:
        #     states_from_dc = dc_allocation[from_dc]
        #     states_to_dc = dc_allocation[to_dc]
        #     if state in states_from_dc:
        #         break

        # states_from_dc.remove(state)
        # states_to_dc.append(state)

        return dc_allocation

    def evaluate_acceptance(self, delta_objective):
        # Calculate the probability of acceptance
        return m.exp(-delta_objective / self.initial_temperature)
    
    def annealing(self):
        # # Find the local optima based on the annealing technique
        start_algorithm = time.time()

        # Stop when t reached tmax
        for t in range(self.tmax):

            # Randomly select a DC to move states from
            dc_list = list(initial_solution.keys())
            while True:
                from_dc = random.choice(dc_list)
                if len(initial_solution[from_dc]) > 1:
                    break

            # Randomly select a DC as destination (avoid moving to an empty DC)
            while True:
                to_dc = random.choice(dc_list)
                if (to_dc != from_dc):
                    break

            # Randomly select a subset of states from source DC
            states_to_move = random.sample(initial_solution[from_dc], 1)[0]

            # Create the new dc_allocation, appending the recent move
            new_dict = self.move(states_to_move, initial_solution, from_dc, to_dc)

            # Calculate new costs for the current solution
            current_obj_value = pm.total_costs(new_dict)
            self.current_solution = new_dict

            # Calculate the costs of the current solution
            self.current_objective_value_list.append(current_obj_value)

            # Evaluate the current solution using net objective function improvement
            delta_objective = current_obj_value - self.initial_obj_value
            
            if delta_objective < 0:
                self.initial_obj_value = current_obj_value
                best_solution = self.current_solution.copy()
                best_current_obj_value = current_obj_value

            elif delta_objective >= 0:
                probability = self.evaluate_acceptance(delta_objective)
                accepted = np.random.random() < probability
                
                if accepted:
                    # Means the non-improving solution is also included in the current solution
                    self.initial_obj_value = current_obj_value
                    best_current_obj_value = current_obj_value

                if not accepted:
                    best_current_obj_value = self.initial_obj_value
                    best_solution = self.current_solution

            # Temperature decreases as the number of iteration increases
            self.initial_temperature = self.initial_temperature * self.cooling_rate

            # Track the changes in the temperature level and best objective value for plotting
            self.temperature_list.append(self.initial_temperature)
            self.best_objective_value_list.append(best_current_obj_value)
            print(t, 'Best current obj. value:', best_current_obj_value)

        # # Calculate the algorithm time
        end_algorithm = time.time()
        elapsed_algorithm = end_algorithm - start_algorithm

        # Log the computation time and time complexity of the algorithm
        logging.info(f"Computation time = {elapsed_algorithm}")
        logging.info(f"\nTime complexity of the algorithm for {self.tmax} iterations = {elapsed_algorithm / self.tmax} seconds")

        # Plot the improvements of the objective value (each dot represent each product)
        plt.plot(self.best_objective_value_list, marker="o", label="best solution")
        plt.plot(self.current_objective_value_list, label="current solution")
        plt.plot(self.temperature_list, label="temperature")
        plt.title(f"Objective Value Changes in Simulated Annealing with {self.tmax} iteration, temp 5000")
        plt.xlabel("Number of iterations")
        plt.legend()
        plt.show()

        # print(best_solution)
        print(best_current_obj_value)
        # outbound = sum(pm.outbound_costs(best_solution, pm.demand_data, pm.outbound_data))
        logging.info(f"SA's objective value: {best_current_obj_value}")
        # logging.info(f"Outbound Costs: {outbound}")

# def main():
sa = SimulatedAnnealing()
print(sa.annealing())
# logging.info(f"SA's objective value: {sa.annealing()}")

#     x = sa.annealing()
#     print(x)
#     # sa.scheduling(x).to_excel("s_a_schedule.xlsx",index=False)
#     # Log the final objective value of the current solution and print it as an output
#     # 
#     # print(f"SA's objective value: {att.total_costs}")

#     # return att.total_costs

# main()
