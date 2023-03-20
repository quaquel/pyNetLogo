import os
import pandas as pd
from SALib.sample import saltelli
from multiprocessing import Pool

from src import pynetlogo


def initializer(modelfile):
    """initialize a subprocess

    Parameters
    ----------
    modelfile : str

    """

    # we need to set the instantiated netlogo
    # link as a global so run_simulation can
    # use it
    global netlogo

    netlogo = pynetlogo.NetLogoLink(gui=False)
    netlogo.load_model(modelfile)


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
        [counts["count sheep"].values.mean(), counts["count wolves"].values.mean()],
        index=["Avg. sheep", "Avg. wolves"],
    )
    return results


if __name__ == "__main__":
    modelfile = os.path.abspath("./models/Wolf Sheep Predation_v6.nlogo")

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

    n = 1000
    param_values = saltelli.sample(problem, n, calc_second_order=True)

    # cast the param_values to a dataframe to
    # include the column labels
    experiments = pd.DataFrame(param_values, columns=problem["names"])

    with Pool(4, initializer=initializer, initargs=(modelfile,)) as executor:
        results = []
        for entry in executor.map(run_simulation, experiments.to_dict("records")):
            results.append(entry)
        results = pd.DataFrame(results)
