import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as m
import logging
import time


# Initiate a logger to log necessary information
log_format = "%(asctime)s - %(module)s - %(message)s"
logging.basicConfig(filename='log_file.log', level=logging.INFO, format=log_format, filemode='w')


# Choose any starting feasible solution x
# In this case, I use the feasible solution from the first solution method (Greedy Constructive Heuristics)
initial_solution = gch.construct_decision_variable()

class SimulatedAnnealing:

    # Set the initial objective value as the reference for improvement
    total_costs = 9981023.5

    # Make a copy of the initial solution to avoid modifying it directly
    improving_solution = initial_solution.copy()

    # Define the initial temperature, cooling rate, and tmax as the parameter of the algorithm
    initial_temperature = 5000
    cooling_rate = 0.95
    tmax = 5000

    # Initiate the lists for plotting the changes per iteration
    best_objective_value_list = [total_costs]
    current_objective_value_list = [total_costs]
    temperature_list = [initial_temperature]

    def evaluate_acceptance(self, delta_objective):
        # Calculate the probability of acceptance
        return m.exp(-delta_objective / self.initial_temperature)
    
    def annealing(self):
        # Find the local optima based on the annealing technique
        start_algorithm = time.time()

        # Stop when t reached tmax
        for t in range(self.tmax):
            # Randomly select a feasible move
            prod_index = np.random.randint(0, model.num_prod)
            line_index = np.random.randint(0, model.num_prod_lines)

            # Find the line to which this product is currently assigned, then move it based on the pre-selected move
            where_one = np.where(self.improving_solution[prod_index] == 1)[0][0]

            # Ensure that the line the product is currently assigned to is not the same as the line it will move to.
            if line_index != where_one:
                self.improving_solution[prod_index][where_one] = 0
                self.improving_solution[prod_index][line_index] = 1

            elif line_index == where_one:
                continue

            # Calculate the penalty of the current solution
            attributes = att.get_product_attributes(self.improving_solution)
            current_penalty = att.calculate_total_costs(attributes)
            self.current_objective_value_list.append(current_penalty)

            # Evaluate the current solution using net objective function improvement
            delta_objective = current_penalty - self.total_costs
            
            if delta_objective < 0:
                self.total_costs = current_penalty
                best_solution = self.improving_solution.copy()
                best_current_penalty = current_penalty

            elif delta_objective > 0:
                probability = self.evaluate_acceptance(delta_objective)
                accepted = np.random.random() < probability

                if accepted:
                    # Means the non-improving solution is also included in the current solution
                    self.total_costs = current_penalty
                    best_current_penalty = current_penalty

                if not accepted:
                    current_penalty = self.total_costs
                    self.improving_solution[prod_index][where_one] = 1
                    self.improving_solution[prod_index][line_index] = 0

            # Temperature decreases as the number of iteration increases
            self.initial_temperature = self.initial_temperature * self.cooling_rate

            # Track the changes in the temperature level and best objective value for plotting
            self.temperature_list.append(self.initial_temperature)
            self.best_objective_value_list.append(best_current_penalty)
        
        # Calculate the algorithm time
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

        return best_solution

    def scheduling(self, x):
        # Insert the built schedule in a dataframe and log the scheduling time + assigned line for each product
        
        # Log the production line that is assigned for each product
        product_index, line_index = np.where(x == 1)
        for p, l in zip(product_index, line_index):
            product = model.product_list[p]
            line = model.line_headers[l]
            logging.info(f"Product {product} has been reassigned to Line {line}")

        start_schedule = time.time()
        # Insert the built schedule in a dataframe
        rows = att.get_product_attributes(x)
        columns = ["Product", "Line", "Start", "Process Time", "End", "Deadline", "Tardiness", "Total Penalty Cost"]
        schedule = pd.DataFrame(rows, columns=columns)
        
        # Calculate the elapsed time and log the scheduling time to the log file
        end_schedule = time.time()
        elapsed_time = end_schedule - start_schedule
        logging.info("Scheduling time: %s seconds", elapsed_time)
        
        return schedule

# Second solution method execution
def main():
    sa = SimulatedAnnealing()
    x = sa.annealing()

    sa.scheduling(x).to_excel("s_a_schedule.xlsx",index=False)
    # Log the final objective value of the current solution and print it as an output
    logging.info(f"SA's objective value: {att.total_costs}")
    print(f"SA's objective value: {att.total_costs}")

    return att.total_costs

main()
