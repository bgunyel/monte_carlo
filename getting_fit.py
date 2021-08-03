import pandas as pd
import numpy as np
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns


def compute_ecdf(input_vector):
    counts = Counter(input_vector)
    ecdf_matrix = np.array(list(counts.items()))
    idx = np.argsort(ecdf_matrix[:, 0])
    x = ecdf_matrix[:, 0][idx]
    y = ecdf_matrix[:, 1][idx]
    y = np.cumsum(y) / np.sum(y)
    return x, y


def generate_empirical_random_sample(x, ecdf, n_samples):
    number_of_intervals = len(x) - 1
    u = np.random.uniform(low=np.min(ecdf), high=np.max(ecdf), size=n_samples)
    idx = np.searchsorted(ecdf, u)
    x_low = x[idx - 1]
    x_high = x[idx]
    out = x_low + (x_high - x_low) * (u - ecdf[idx-1]) / (ecdf[idx] - ecdf[idx-1])
    return out


def main(name):
    print(name)

    n_iterations = 1000
    n_simulation_days = 30
    initial_weight = 114.6

    dataFilePath = './questions/diet_data.xlsx'

    df = pd.read_excel(dataFilePath, sheet_name='Daily', engine='openpyxl')
    daily_weight_change_vector = np.around(df.dropna()['Kilo Değişim'].to_numpy(), 2)
    weight_vector = np.concatenate((np.array([0]), np.cumsum(daily_weight_change_vector))) + initial_weight

    x, ecdf = compute_ecdf(daily_weight_change_vector)

    iteration_random_vectors = np.zeros(shape=(n_iterations, n_simulation_days))

    plt.figure()
    plt.plot(weight_vector, label='Actual Weight', marker='*', linewidth=2.5)

    for iteration in range(n_iterations):
        x_random = generate_empirical_random_sample(x=x, ecdf=ecdf, n_samples=n_simulation_days)
        weight_estimate_vector = np.cumsum(x_random) + weight_vector[-1]
        iteration_random_vectors[iteration, :] = x_random

        if iteration % 100 == 0:
            plt.plot(range(len(weight_vector)-1, len(weight_vector) + len(weight_estimate_vector)),
                     np.concatenate((np.array(weight_vector[-1], ndmin=1), weight_estimate_vector)))

    plt.legend()
    plt.show()

    weight_estimations = np.cumsum(iteration_random_vectors, axis=1) + weight_vector[-1]

    mean_estimation = np.mean(weight_estimations, axis=0)
    median_estimation = np.median(weight_estimations, axis=0)
    lower_ci = np.percentile(weight_estimations, q=2.5, axis=0)
    higher_ci = np.percentile(weight_estimations, q=97.5, axis=0)

    plt.figure()
    plt.plot(weight_vector, label='Actual Weight')
    plt.plot(range(len(weight_vector)-1, len(weight_vector) + len(median_estimation)),
             np.concatenate((np.array(weight_vector[-1], ndmin=1), median_estimation)),
             label='Median Estimation')
    plt.plot(range(len(weight_vector), len(weight_vector) + len(lower_ci)),
             lower_ci, label='0.95 Confidence Interval - Lower Bound')
    plt.plot(range(len(weight_vector), len(weight_vector) + len(higher_ci)),
             higher_ci, label='0.95 Confidence Interval - Upper Bound')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main('Getting Fit -- Monte Carlo Simulations')
