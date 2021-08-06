import numpy as np
import matplotlib.pyplot as plt


def simulate(n_generator, n_iterations, generator_fixed_cost, generator_capacity,
             variable_cost, penalty_cost, unit_revenue):
    print(f'Number of Generators: {n_generator}')

    capacity = n_generator * generator_capacity
    fixed_cost = n_generator * generator_fixed_cost

    profit_per_each_iteration = np.zeros(n_iterations)


    for iteration in range(n_iterations):
        industrial_demand = np.random.uniform(3e5, 5e5)
        household_demand = np.random.normal(1e6, 2e5)
        total_demand = industrial_demand + household_demand

        produced_supply = min(total_demand, capacity)
        imported_supply = max(total_demand - capacity, 0)

        total_revenue = total_demand * unit_revenue
        total_cost = fixed_cost + produced_supply * variable_cost + imported_supply * penalty_cost
        profit = total_revenue - total_cost
        profit_per_each_iteration[iteration] = profit

    mean_profit = np.mean(profit_per_each_iteration)
    std_profit = np.std(profit_per_each_iteration)
    # ci_lower_bound = np.percentile(a=profit_per_each_iteration, q=2.5)
    # ci_upper_bound = np.percentile(a=profit_per_each_iteration, q=97.5)

    ci_lower_bound = mean_profit - 1.96 * std_profit / np.sqrt(n_iterations)
    ci_upper_bound = mean_profit + 1.96 * std_profit / np.sqrt(n_iterations)

    print(f'Mean Profit: {mean_profit}')
    print(f'0.95 Confidence Interval: {ci_lower_bound} {ci_upper_bound}')
    print(f'0.95 Confidence Interval Width: {ci_upper_bound - ci_lower_bound}')

    return profit_per_each_iteration


def main(name):
    print(name)

    n_generators = [3, 4, 5, 6, 7, 8, 9, 10]

    generator_fixed_cost = 7000  # USD
    generator_capacity = 2e5  # in kW (200,000 kW)
    variable_cost = 0.05  # USD per kW
    penalty_cost = 0.12  # USD per kW
    unit_revenue = 0.10  # USD per kW

    n_iterations = 100000

    plt.figure()

    for n in n_generators:
        profit_per_each_iteration = simulate(n, n_iterations, generator_fixed_cost, generator_capacity, variable_cost,
                                             penalty_cost, unit_revenue)

        if n % 2 == 1:
            plt.hist(profit_per_each_iteration, label=n, alpha=0.75, bins=200)

    plt.legend()
    plt.show()





if __name__ == '__main__':
    main('Electricity Supply Monte Carlo Simulation')
