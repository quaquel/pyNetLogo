"""

"""

# Created on 7 Jan 2020
#
# .. codeauthor::  jhkwakkel

import numpy as np
import os
import pandas as pd
from SALib.sample import sobol

from src import pynetlogo


def run_simulation(experiment):
    """run a netlogo model

    Parameters
    ----------
    experiments : dict

    """

    # Set the input parameters
    for key, value in experiment.items():
        if key == "random-seed":
            # The NetLogo random seed requires a different syntax
            netlogo.command("random-seed {}".format(value))
        else:
            # Otherwise, assume the input parameters are global variables
            netlogo.command("set {0} {1}".format(key, value))

    netlogo.command("setup")
    # Run for 100 ticks and return the number of sheep and
    # wolf agents at each time step
    counts = netlogo.repeat_report(["count sheep", "count wolves"], 100)

    results = pd.Series(
        [np.mean(counts["count sheep"]), np.mean(counts["count wolves"])],
        index=["Avg. sheep", "Avg. wolves"],
    )
    return results


if __name__ == "__main__":
    modelfile = os.path.abspath("./models/Wolf Sheep Predation_v6.nlogo")

    netlogo = pynetlogo.NetLogoLink(gui=False)
    netlogo.load_model(modelfile)

    problem = {
        "num_vars": 6,
        "names": [
            "random-seed",
            "grass-regrowth-time",
            "sheep-gain-from-food",
            "wolf-gain-from-food",
            "sheep-reproduce",
            "wolf-reproduce",
        ],
        "bounds": [
            [1, 100000],
            [20.0, 40.0],
            [2.0, 8.0],
            [16.0, 32.0],
            [2.0, 8.0],
            [2.0, 8.0],
        ],
    }

    n = 1024
    param_values = sobol.sample(problem, n, calc_second_order=True)

    results = []
    for row in param_values:
        experiment = {k: v for k, v in zip(problem["names"], row)}
        result = run_simulation(experiment)
        results.append(result)
    results = pd.DataFrame(results)
    print("end")
