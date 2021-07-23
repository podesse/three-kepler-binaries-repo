# This is the associated repository for the Binary Stars paper

In this repository, you will find the data used in the analysis, scripts used throughout the paper, figures that didn't make the cut, and importantly the stellar models used in this analysis.

## Scripts

These are various scripts used to process data, for plotting, ext.

## Models

<<<<<<< HEAD
In the models directory, you will find the PHOEBE models used in this research, complete with datasets, solutions, and all settings. These models were generated using PHOEBE 2.3.40 -- they can be downloaded and imported with your own PHOEBE installation. If you have a different PHOEBE installaiton, this may require that you pass the `import_from_older` or `import_from_newer` option:

```python
import phoebe
b = phoebe.load('10727668.phoebe', import_from_older=True)
```

## Data

This directory contains raw data from the Kepler pipline for all three binaries studied, and the processed data we used in this research. Data processing scripts are visible in the ./scripts directory.

## Figures

Ideally, this will contain all the figures from the paper in high resolution, as well as some additional figures that may not have made the cut.
=======
In the models directory, you will literally find the PHOEBE models used in this research, complete with datasets, solutions, and all settings. You can download them and import them.

## Data

This directory contains raw data from the Kepler pipline, and the processed data we used in this research.

## Figures

Ideally, this will contain all the figures from the paper (hi-res), as well as some additional figures that may not have made the cut.
>>>>>>> 9bd6f13c0bc8df2be8dc8d3642dfcf992dc74900
