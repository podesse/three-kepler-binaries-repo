# Data

Here you will find the Kepler light curve data used in this research, both pre- and post-treatment. The original `.fits` data files may be obtained from MAST: https://mast.stsci.edu

## kplr*.dat

These are the original data files, directly interpreted from the Kepler `.fits` files using the script `kic_reader.py` script found in the `../scripts` directory.

## kplr*_detrended.dat

These are the results of de-trending the Kepler data using a chain of fifth-order Legendre polynomials.

## kplr*_final.dat

These files contain the photometric data used in the analysis of these three binaries. They are simply the detrended data files with all outliers removed.

## kplr*_binned.dat

These data files were generated with the script `lc_bins.py` and were used in the initial analysis of binned data for each system.