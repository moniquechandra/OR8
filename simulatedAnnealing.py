
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as m
import random
import logging
import time

from product_details import Parameters
pm = Parameters()

class SA:

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

    initial_solution = {'WA': ['AK', 'ID', 'OR', 'WA'], 
         'TN': ['AL', 'AR', 'FL', 'GA', 'KS', 'KY', 'MO', 'MS', 'NC', 'OH', 'PA', 'SC', 'TN', 'VA', 'WV'],
         'UT': ['AZ', 'CA', 'CO', 'NV', 'UT', 'WY'], 
         'NY': ['CT', 'DE', 'HI', 'MA', 'MD', 'ME', 'NH', 'NJ', 'NY', 'RI', 'VT', 'DC'],
         'ND': ['IA', 'IN', 'MN', 'MT', 'ND', 'NE', 'SD', 'WI'],
         'IL': ['IL', 'MI'], 'TX': ['LA', 'NM', 'OK', 'TX'], 'PA': [],
        'KS': [],
        'CA': []}

    # Set the initial objective value as the reference for improvement
    total_penalty = pm.total_costs(initial_solution, as_is_dc)[0]

        # Make a copy of the initial solution to avoid modifying it directly
    improving_solution = initial_solution.copy()

    # Define the initial temperature, cooling rate, and tmax as the parameter of the algorithm
    # current_best = 12000 0.85 1000 - 150000 0.85
    initial_temperature = 50000
    cooling_rate = 0.85
    tmax = 1000

    # Initiate the lists for plotting the changes per iteration
    best_objective_value_list = [total_penalty]
    current_objective_value_list = [total_penalty]
    temperature_list = [initial_temperature]

    def evaluate_acceptance(self, delta_objective):
        # Calculate the probability of acceptance
        return m.exp(-delta_objective / self.initial_temperature)
    
    def move(self, state_to_move, dc_allocation, from_dc, to_dc, undo=False):
        # Feasible move: Move the state from one DC to another, then return the new DC allocation.
        states_from_dc = dc_allocation[from_dc]
        states_to_dc = dc_allocation[to_dc]
            
        if not undo:
            states_from_dc.remove(state_to_move)
            states_to_dc.append(state_to_move)

        elif undo:
            states_from_dc.append(state_to_move)
            states_to_dc.remove(state_to_move)

        return dc_allocation

    def annealing(self):
        # Find the local optima based on the annealing technique
        start_algorithm = time.time()
        best_current_penalty = self.total_penalty
        best_solution = self.initial_solution

        # Stop when t reached tmax
        for t in range(self.tmax):
            # Randomly select a feasible move
            dc_list = list(self.initial_solution.keys())
            while True:
                from_dc = random.choice(dc_list)
                if self.initial_solution[from_dc]:
                    break

            # Randomly select a DC as destination (avoid moving to an empty or same DC)
            while True:
                to_dc = random.choice(dc_list)
                if to_dc != from_dc:
                    break

            state_to_move = random.sample(self.improving_solution[from_dc], 1)[0]
            improving_solution = self.move(state_to_move, self.improving_solution, from_dc, to_dc)

            # states_from_dc = self.improving_solution[from_dc]
            # states_to_dc = self.improving_solution[to_dc]
            # self.improving_solution[from_dc] = states_to_dc
            # self.improving_solution[to_dc] = states_from_dc
            
            # Calculate the penalty of the current solution
            current_penalty = pm.total_costs(improving_solution, self.as_is_dc)[0]
            self.current_objective_value_list.append(current_penalty)

            # Evaluate the current solution using net objective function improvement
            delta_objective = current_penalty - best_current_penalty
            
            if delta_objective < 0:
                best_solution = self.improving_solution.copy()
                best_current_penalty = current_penalty
                logging.info(f"Improving allocation = {best_solution}")

            elif delta_objective > 0:
                probability = self.evaluate_acceptance(delta_objective)
                accepted = np.random.random() < probability

                if accepted:
                    # Means the non-improving solution is also included in the current solution
                    best_current_penalty = current_penalty
                    logging.info(f"Improving allocation = {best_solution}")

                if not accepted:
                    current_penalty = self.total_penalty
                    self.move(state_to_move, self.improving_solution, from_dc, to_dc, undo=True)

            # Temperature decreases as the number of iteration increases
            self.initial_temperature = self.initial_temperature * self.cooling_rate

            # Track the changes in the temperature level and best objective value for plotting
            self.temperature_list.append(self.initial_temperature)
            self.best_objective_value_list.append(best_current_penalty)
            print(t, current_penalty, best_current_penalty)
            
        # Calculate the algorithm time
        end_algorithm = time.time()
        elapsed_algorithm = end_algorithm - start_algorithm

        # Log the computation time and time complexity of the algorithm
        logging.info(f"Computation time = {elapsed_algorithm}")
        logging.info(f"\nTime complexity of the algorithm for {self.tmax} iterations = {elapsed_algorithm / self.tmax} seconds")
        logging.info(f"Best solution = {best_solution}")
        logging.info(f"Total costs = {pm.total_costs(best_solution, self.as_is_dc)[0]}")
        logging.info(f"Difference of costs = {self.total_penalty - pm.total_costs(best_solution, self.as_is_dc)[0]}")

        # Plot the improvements of the objective value (each dot represent each product)
        plt.plot(self.best_objective_value_list, marker="o", label="best solution")
        # plt.plot(self.current_objective_value_list, label="current solution")
        plt.plot(self.temperature_list, label="temperature")
        plt.title(f"Objective Value Changes in Simulated Annealing with {self.tmax} iteration, temp {self.initial_temperature})")
        plt.xlabel("Number of iterations")
        plt.legend()
        plt.show()

        return best_solution
    

sa = SA()
print(sa.annealing())