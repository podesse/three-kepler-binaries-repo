'''
This script is used to read light curve data from a raw Kepler .fits file. It also converts
the flux units from electrons per second to Watts per square metre via. the method detailed
in our paper -- also see the script ab_magnitude_integral.py for the method of deriving this
conversion factor.
'''

from astropy.io import fits
import numpy as np
import scipy as sp
import os
import glob
from pylab import * # Gives us more functionality than just plotting, which we use


'''
Read Kepler data from multiple .fits file
KIC_name -- the name of the star in the Kepler catalouge. This only defines the file name
to which the processed data will be saved: kplr[KIC_name].dat
fitsDirectory -- the directory in which all the .fits files are saved.
fitsFiles -- the name of each .fits file in that directory you wish to process
join -- a boolean, where True means that you want to join mulitple quarters (ie. data from
all the .fits files will be saved into one file). This value is True by default.

Example:
kic_reader_new.readfits("10727668", 
	"./MAST_Data/Kepler/kplr010727668_lc_Q000000000000001111", 
	['kplr010727668-2012277125453_llc.fits',
	'kplr010727668-2013011073258_llc.fits',
	'kplr010727668-2013098041711_llc.fits',
	'kplr010727668-2013131215648_llc.fits']
	)
'''
def readfits(KIC_name, fitsDirectory, fitsFiles, join=True):
	dir_raw = '.'
	print("Current Directory: {0}".format(dir_raw))
	KIC = KIC_name
	Nfiles = len(fitsFiles)
	print("# of files: {0}".format(Nfiles))
	# Set up our timeseries inputs
	t = []
	fl = []
	err = []
	ind = zeros(Nfiles) #Not sure what this does
	print(ind)
	flnm = 'kplr'+KIC+'.dat' #The filename where we will save the output

	for j in range(0, Nfiles):
		filepath = fitsDirectory+'/'+fitsFiles[j]
		print("File path: {0}".format(filepath))
		hdufileList = fits.open(filepath)
		# Acquire all the useful information from the header
		data = hdufileList[1].data #The data in the HDU
		quarter = hdufileList[0].header['QUARTER']
		season = hdufileList[0].header['SEASON']
		Kep_mag = hdufileList[0].header['KEPMAG']
		Teff = hdufileList[0].header['TEFF']
		logg = hdufileList[0].header['LOGG']
		FeH = hdufileList[0].header['FEH']
		radius = hdufileList[0].header['RADIUS']
		grcolor = hdufileList[0].header['GRCOLOR']
		EBminusV = hdufileList[0].header['EBMINUSV']
		print("KEPMAG: {0}".format(Kep_mag))
		print("Teff: {0}".format(Teff))
		# This is the data we will process
		time = data.field(0)
		signal = data.field(7) # The signal is not quite a measure of flux... it's in electrons per second
		err_sig = data.field(8)
		print("Time stamps: {0}".format(time))
		#remove NaNs
		time = time[~isnan(signal)]
		err_sig = err_sig[~isnan(signal)]
		signal = signal[~isnan(signal)]
		# check time for NaNs as well just in case
		signal = signal[~isnan(time)]
		err_sig = err_sig[~isnan(time)]
		time = time[~isnan(time)]
		print("Signal: {0}".format(signal))
		print("Signal Error: {0}".format(err_sig))
		# Convert from fluxes in electron counts to fluxes in W/m^2
		# Based on my previous work calibrating the flux of a 12th magnitude solar-type 
		# star in the Kepler Passband (assuming an AB magnitude system)
		physical_fluxes = signal*6.640e-19
		print("Fluxes [W/m^2]: {0}".format(physical_fluxes))
		# Need to propegate the errors as well
		physical_err = err_sig*6.640e-19
		
		if(j==0):
			all_times = []
			all_fluxes = []
			all_err = []
			average_flux = []
		all_times.append(time)
		all_fluxes.append(physical_fluxes)
		all_err.append(physical_err)
		average_flux.append(np.average(physical_fluxes))

	if(join):
		# Joining multiple quarters, if we have them
		t = []
		fl = []
		err = []
		average = np.average(average_flux) # The average of averages
		for j in range(0, Nfiles):
			offset = 0#= average - average_flux[j] # amount by which we need to shift our flux values
			t = np.concatenate((t,all_times[j]),axis=0)
			fl = np.concatenate((fl,all_fluxes[j]+offset),axis=0)
			err = np.concatenate((err,all_err[j]),axis=0)
		print(len(t), len(fl))
		plot(t, fl)

		
		# Save our lightcurve data to a file
		f = open(flnm, 'w')
		print(t.size)
		for i in range(t.size):
			f.write(str(t[i]) + ' ' + str(fl[i]) + ' ' + str(err[i]) + '\n')
		f.close()

	else:
		# Save the multiple quarters in separate files
		for j in range(0, Nfiles):
			filepath = fitsDirectory+'/'+fitsFiles[j]
			#print("File path: {0}".format(filepath))
			hdufileList = fits.open(filepath)
			# Acquire all the useful information from the header
			quarter = hdufileList[0].header['QUARTER']
			flnm = 'kplr{0}{1}.dat'.format(KIC, quarter)

			f = open(flnm, 'w')
			print(all_times[j].size)
			for i in range(all_times[j].size):
				f.write(str(all_times[j][i]) + ' ' + str(all_fluxes[j][i]) + ' ' + str(all_err[j][i]) + '\n')
			f.close()

# I think we're done here!