# Figures for MCMC Analysis of the Binned Light Curve for KIC 8314879

## The log-probability plot

It should be noted that there is a sudden distinct increase in the log-probability function near iteration 5000. After this run started, we decided to increase the resolution of binned data points from 200 to 500. However, we did not wish to lose all the progress this run had made so far, so we simply continued the run with the updated dataset. This had minimal impact on the shape of the light curve, but since more points were being compared, the log-probability increased. 

<img src="https://github.com/podesse/binary-paper-repo/blob/main/figures/binned_runs/8314879/lnprob_burned.png" width=500/>

<figcaption>
The log-probability plot, with burn-in and thinning applied.
</figcaption>


## Trace plots

The sudden increase in resolution halfway through the run also decreased the acceptance of new positions in the parameter space. This can be seen in the trace plots: after 5000 iterations, the walkers begin to take smaller steps. For several parameters, such as the sum of fractional radii 
$\frac{R_1+R_2}{a}$, the walkers become more clustered.

<img src="https://github.com/podesse/binary-paper-repo/blob/main/figures/binned_runs/8314879/trace_full.png" width=500/>

<figcaption>
The full trace plot, without burn-in or thinning applied, highlights the change in sampling behaviour after 5000 iterations.
</figcaption>