# Models

These models were generated with PHOEBE version 2.3.40, which may be downloaded from: http://phoebe-project.org/install

## PHOEBE Models

These bundle files (`5957123.phoebe` and so on) do not contain the solutions from the MCMC run. Those are rather large, and so are saved separately. 

These bundles do contain all the settings we used for our models. They also contain posterior distributions from the binned and full dataset analaysis, along with the original initializing distribution and any prior distributions.

Note that these models do not contain the original parameter values obtained by manual fitting and Nelder-mead optimization. Rather, they contain the values adoped from the MCMC analysis, as these were found to give better fits to the light curve overall.

## Solutions

The output from each MCMC run is saved in the emcee_sol_*.out.progress files. These are saved separately from the models and compressed, since they otherwise require a few hundred MB of memory each. To view a solution first requires loading the appropriate PHOEBE bundle, and then importing the solution.

```
import phoebe

b = phoebe.load('10727668.phoebe')

b.import_solution('emcee_sol_10727668.out.progress, solution='emcee_solution_progress')
```

From here, all of the diagnostic plots found within the ../figures directory may be generated.

## Residuals

These `.dat` files contain the light curve residuals. Residuals were computed based on the median light curve of 10 forward models drawn from the final posterior distributions.
