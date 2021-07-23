'''
This script is used to bin light curve data with a given period.
'''

import numpy as np
import matplotlib.pyplot as plt

flnm = 'binned_data.dat'


'''
The main function takes three inputs:
dataFile -- the raw light curve data you wish to process
period -- the period of the binary system. Can be found using PHOEBE's lc_periodogram solver
nBins -- the number of bins you wish to sort your light curve data into 
'''
def main(dataFile, period, nBins):
	time, flux, sigma = loadData(dataFile)

	tFold, fFold, sFold = phasefold(time, flux, sigma, period)

	tBin, fBin, sBin = binData(tFold, fFold, sFold, nBins)

	plot_lc(tBin, fBin, sBin, period)

	#Write everything to a file
	f = open(flnm, 'w')
	print(len(tBin))
	for i in range (0, len(tBin)):
		f.write(str(tBin[i]) + ' ' + str(fBin[i]) + ' ' + str(sBin[i]) + '\n')
	f.close()


def phasefold(time, flux, sigma, period):
	t0 = time[0]
	tShift = time #This will be our time-shifted array
	count = 0 #Gives us some idea of what shell size to start with in our shell sort.
	#Shift all datapoints so they are within one period
	print("period: ", period)
	print("t0: ", t0)
	print(tShift[1])
	for i in range(0, len(time)):
		if(tShift[i] - t0 > period):
			count += 1
			for j in range(i, len(tShift)): #len(time)
				tShift[j] = tShift[j] - period
	#Catch any outlying points that didn't get phasefolded for whatever reason
	limit = t0 + period
	index = 0
	while(index < len(tShift)):
		if (tShift[index] > limit):
			tShift[index] = tShift[index] - period
			index = 0 #Start back at the beginning, in case they weren't folded far enough
		index +=1
	#Now, we must sort our time-shifted list alongside the flux and sigma lists
	tFold, fFold, sFold = sort(tShift, flux, sigma, count)

	return tFold, fFold, sFold

#Sorts the time, flux, and sigma datapoints with respect to time.
def sort(tShift, flux, sigma, count):
	#I've never actually written a ShellSort... this could be fun
	n = len(tShift)
	shell = n//2 #Start with a large insertion sort, then reduce (Will this remain an int?)

	while(shell > 0):
		#Check shell size for debugging
		print("Shell size: ", shell)
		for i in range(shell, n):
			#Hold the value at i temporarily out of the array
			tTemp = tShift[i]
			fTemp = flux[i]
			sTemp = sigma[i]

			#Shift all elements in all arrays until the position for tTemp is found
			j = i
			while (j >= shell and tShift[j-shell] > tTemp):
				tShift[j] = tShift[j-shell]
				flux[j] = flux[j-shell]
				flux[j] = flux[j-shell]
				j -= shell
			#Put tTemp (and others) in its correct location
			tShift[j] = tTemp
			flux[j] = fTemp
			sigma[j] = sTemp
		shell //= 2

	return tShift, flux, sigma

def binData(time, flux, sigma, nBins):
	#Start our bins as emty lists
	tBin = []
	fBin = []
	sBin = []

	binSize = len(time)/nBins # Integer division. May lose one datapoint on the end.
	print("Bin size: {0}".format(binSize))
	print("Bin size * nBins: {0}".format(binSize*nBins))
	print("Length of (phasefolded) time: {0}".format(len(time)))
	for i in range(0, nBins):
		tBin.append(average(time[(int(i*binSize)):int((i*binSize)+binSize)]))
		fBin.append(average(flux[int(i*binSize):int((i*binSize)+binSize)]))
		#fBin.append(weightedAverage(flux[(i*binSize):((i*binSize)+binSize)], sigma[(i*binSize):((i*binSize)+binSize)]))
		#sBin.append(average(sigma[(i*binSize):((i*binSize)+binSize)]))
		#sBin.append(sigmaAverage(sigma[(i*binSize):((i*binSize)+binSize)]))
		#For uncertainty, use standard deviation because random uncertainty is so small
		sBin.append(stDev(flux[int(i*binSize):int((i*binSize)+binSize)]))
	
	return tBin, fBin, sBin

#Averages a subset of our time array
def average(array):
	s = 0
	for i in range(0, len(array)):
		s += array[i]
	try:
		ave = s/len(array)
	except ZeroDivisionError as err:
		print("Error: {0}".format(err))
		print("Encountered error while computing ave = s/len(array), where the guilty array was: {0}".format(array))
		raise
	return ave

#Performs a weighted average for the flux
def weightedAverage(array, sigmaList):
	weights = 1/(sigmaList**2)
	weightAve = np.sum(weights*array)/np.sum(weights)
	return weightAve

#Works similar to average, but properly propegates uncertainties
#Namely, the uncertainty in the weighted average of flux
def sigmaAverage(sigmaList):
	weights = 1/(sigmaList**2)
	swav = 1/np.sqrt(np.sum(weights)) #Uncertainty in the weighted average
	return swav

#Compute the standard deviation of an array
def stDev(array):
	ave = np.average(array)
	N = len(array)
	#print("N: {0}".format(N))
	err = []
	for i in range(0, len(array)):
		err.append((array[i]-ave)**2)
	stDev = np.sqrt(np.sum(err)/(N-1))
	#print(max(err))
	return stDev

'''
def stDevOfMean(sigmaList):
	sdom = average(sigmaList)/np.sqrt(len(sigmaList))
	return sdom
'''

def loadData(fName):
	data = np.loadtxt(fName)
	time = data[:,0]
	flux = data[:,1]
	sigma = data[:,2]
	return time, flux, sigma

# This will be rough, but I'd like to see a phasefolded plot
def plot_lc(tBin, fBin, sBin, period):
	# As an estimate of t0, take the time corresponding to the lowest flux value
	t0 = tBin[fBin.index(min(fBin))]
	tBin = tBin - t0 # Shift every data point by t0
	tBin = tBin/period # Normalize every point to the period
	# Fold everything to within phase +/- 0.5
	
	for i in range(0, len(tBin)):
		if(tBin[i] + 0.5 < 0):
			tBin[i] += 1.0
		if(tBin[i] - 0.5 > 0):
			tBin[i] -= 1.0
	
	plt.figure()
	plt.errorbar(tBin, fBin, xerr=sBin, yerr=sBin, fmt='b.', mfc='w')
	plt.ylabel("Fluxes [W/m^2]")
	plt.xlabel("Phase")
	plt.show()