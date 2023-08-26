"""
main entry point for visualization
"""
import numpy as np
import matplotlib.pyplot as plt


def viz(data, reckless=False):
    r, c = data.shape

    fig, ax = plt.subplots(r, c)
    pass