# Virtual NDD brain

This usecase describes the steps implementing the modeling of neurodegenerative disease trajectories as described in [1]. Currently, the code replicates the workflow on synthetic data.

## Installation

The usecase is organized as an installable project (read more on the rationale [here](https://drivendata.github.io/cookiecutter-data-science/)). After cloning the repository, run the following commands to initialize the environment.

First create a virtual environment. Alternatively use `conda`. Please use Python version at least 3.8.  

```shell
$ python -mvenv env
$ . env/bin/activate
```

Next install the dependencies and the project itself.

```shell
$ pip install --upgrade pip # just in case your system is old
$ pip install -r requirements.txt
$ pip install -e .
```

And finally initialize the `dvc` cache and checkout the data. 

```shell
$ python -m src.init_cache
$ dvc checkout
```

And that is all. You are now all set to work through the usecase.

## References

[1] Yalçınkaya, B. H., Ziaeemehr, A., Fousek, J., Hashemi, M., Lavanga, M., Solodkin, A., McIntosh, A. R., Jirsa, V. K., & Petkoski, S. (2023). Personalized virtual brains of Alzheimer’s Disease link dynamical biomarkers of fMRI with increased local excitability. In bioRxiv. https://doi.org/10.1101/2023.01.11.23284438
