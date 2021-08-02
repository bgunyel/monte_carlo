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

    dataFilePath = './questions/diet_data.xlsx'

    df = pd.read_excel(dataFilePath, sheet_name='Daily', engine='openpyxl')
    daily_weight_change_vector = np.around(df.dropna()['Kilo Değişim'].to_numpy(), 2)

    x, ecdf = compute_ecdf(daily_weight_change_vector)
    x_random = generate_empirical_random_sample(x=x, ecdf=ecdf, n_samples=10000)

    x_dummy, ecdf_dummy = compute_ecdf(x_random)

    dummy = -32


if __name__ == '__main__':
    main('Getting Fit -- Monte Carlo Simulations')
