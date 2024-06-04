import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as m
import logging
import time
import random

import import_ipynb
from to_be import To_Be

# Choose any starting feasible solution
initial_solution = To_Be.dc_allocation

num_states = 51
num_dc = 10

class SimulatedAnnealing:

    # Set the initial objective value as the reference for improvement
    total_costs = To_Be.outbound_costs(initial_solution)
    print(total_costs)
    # Make a copy of the initial solution to avoid modifying it directly
    current_solution = initial_solution.copy()
    
    # Define the initial temperature, cooling rate, and tmax as the parameter of the algorithm
    initial_temperature = 2000
    cooling_rate = 0.5
    tmax = 200

    # Initiate the lists for plotting the changes per iteration
    best_objective_value_list = [total_costs]
    current_objective_value_list = [total_costs]
    temperature_list = [initial_temperature]

    def evaluate_acceptance(self, delta_objective):
        # Calculate the probability of acceptance
        return m.exp(-delta_objective / self.initial_temperature)
    
    def annealing(self):
        # # Find the local optima based on the annealing technique
        # start_algorithm = time.time()

        # Stop when t reached tmax
        for t in range(self.tmax):
            # Randomly select a feasible move
            
            def moveBetweenKeys(dictionary, src_key, dest_key, value):
                """
                Move the value <value> from the key <src_key> to the key <dest_key>
                Raises ValueError if the value was not found in the list of the keywork
                <src_key>
                """

                src_list = dictionary[src_key]
                dest_list = dictionary[dest_key]

                if value not in src_list:
                    pass

                src_list.remove(value)
                dest_list.append(value)

                return dictionary

            dc_list = list(initial_solution.keys())

            # Randomly select a DC to move states from
            while True:
                source_dc = random.choice(dc_list)
                if len(initial_solution[source_dc]) > 1:
                    break
            
            # Randomly select a non-empty DC as destination (avoid moving to an empty DC)
            while True:
                destination_dc = random.choice(dc_list)
                if (destination_dc != source_dc):
                    break

            # Randomly select a subset of states from source DC
            states_to_move = random.sample(initial_solution[source_dc], 1)[0]
            print(source_dc, destination_dc, states_to_move)

            # Create the new dictionary
            new_dict = moveBetweenKeys(initial_solution, source_dc, destination_dc, states_to_move)

            # Calculate new costs for the current solution
            current_total_costs = To_Be.outbound_costs(new_dict)
            self.current_solution = new_dict
            # print(t, current_total_costs)

            # Calculate the costs of the current solution
            self.current_objective_value_list.append(current_total_costs)

            # Evaluate the current solution using net objective function improvement
            delta_objective = current_total_costs - self.total_costs
            
            if delta_objective < 0:
                self.total_costs = current_total_costs
                best_solution = self.current_solution.copy()
                best_current_total_costs = current_total_costs
                # print('>0')

            elif delta_objective >= 0:
                probability = self.evaluate_acceptance(delta_objective)
                accepted = np.random.random() < probability
                if (accepted):
                    print('hhhh')
                if accepted:
                    # Means the non-improving solution is also included in the current solution
                    self.total_costs = current_total_costs
                    best_current_total_costs = current_total_costs

                if not accepted:
                    best_current_total_costs = self.total_costs
                    best_solution = self.current_solution

            # Temperature decreases as the number of iteration increases
            self.initial_temperature = self.initial_temperature * self.cooling_rate

            # Track the changes in the temperature level and best objective value for plotting
            self.temperature_list.append(self.initial_temperature)
            self.best_objective_value_list.append(best_current_total_costs)
            
        # # Calculate the algorithm time
        # end_algorithm = time.time()
        # elapsed_algorithm = end_algorithm - start_algorithm

        # # Log the computation time and time complexity of the algorithm
        # logging.info(f"Computation time = {elapsed_algorithm}")
        # logging.info(f"\nTime complexity of the algorithm for {self.tmax} iterations = {elapsed_algorithm / self.tmax} seconds")

        # # Plot the improvements of the objective value (each dot represent each product)
        # plt.plot(self.best_objective_value_list, marker="o", label="best solution")
        # plt.plot(self.current_objective_value_list, label="current solution")
        # plt.plot(self.temperature_list, label="temperature")
        # plt.title(f"Objective Value Changes in Simulated Annealing with {self.tmax} iteration, temp 5000")
        # plt.xlabel("Number of iterations")
        # plt.legend()
        # plt.show()

        print(self.best_objective_value_list)
        return best_current_total_costs

    # def scheduling(self, x):
    #     # Insert the built schedule in a dataframe and log the scheduling time + assigned line for each product
        
    #     # Log the production line that is assigned for each product
    #     product_index, col_index = np.where(x == 1)
    #     for p, l in zip(product_index, col_index):
    #         product = model.product_list[p]
    #         line = model.line_headers[l]
    #         logging.info(f"Product {product} has been reassigned to Line {line}")

    #     start_schedule = time.time()
    #     # Insert the built schedule in a dataframe
    #     rows = att.get_product_attributes(x)
    #     columns = ["Product", "Line", "Start", "Process Time", "End", "Deadline", "Tardiness", "Total Penalty Cost"]
    #     schedule = pd.DataFrame(rows, columns=columns)
        
    #     # Calculate the elapsed time and log the scheduling time to the log file
    #     end_schedule = time.time()
    #     elapsed_time = end_schedule - start_schedule
    #     logging.info("Scheduling time: %s seconds", elapsed_time)
        
    #     return schedule

# # Second solution method execution
# def main():
sa = SimulatedAnnealing()
print(sa.annealing())
#     x = sa.annealing()
#     print(x)
#     # sa.scheduling(x).to_excel("s_a_schedule.xlsx",index=False)
#     # Log the final objective value of the current solution and print it as an output
#     # logging.info(f"SA's objective value: {att.total_costs}")
#     # print(f"SA's objective value: {att.total_costs}")

#     # return att.total_costs

# main()
