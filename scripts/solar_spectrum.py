'''
A script to parse the solar spectrum datafile for appropriate wavelengths
File of interest: sorce_L3_combined_c24h_20030225_20200225.txt
'''
import mmap # A random access file parser
import matplotlib.pyplot as plt
import numpy as np

# Oops, better define these methods before I use them

# A sequential search because this code doesn't require optimization
def search(list, element_of_interest):
    for index in range(0,len(list)):
        if(list[index]==element_of_interest):
            return index
    return -1

# Compute the standard deviation of an array
def stDev(array):
    ave = np.average(array)
    N = len(array)
    err = []
    for i in range(0, len(array)):
        err.append((array[i]-ave)**2)
    stDev = np.sqrt(np.sum(err)/(N-1))
    return stDev

# Interpolate the value at xdesired from two adjacent points xmin and xmax with values
# ymin and ymax from some table. Performs a linear interpolation.
def interpol(xdesired, xmin, xmax, ymin, ymax):
    interp_val = ymin + (ymax-ymin)*(xdesired-xmin)/(xmax-xmin)#slope*(xdesired-xmin)/(xmax-xmin)
    return interp_val

# Load the file
f = open("sorce_L3_combined_c24h_20030225_20200225.txt", "r+b")

# Create the random access reader... thing
mm = mmap.mmap(f.fileno(), 0)

# We know this specific file begins with a number of comments, denoted by semicolons.
# Let us begin by traversing to the last comment.

mm.seek(mm.rfind(b';')) # Moves the current position to the last semicolon

print(mm.readline()) # Will read the line, and start us at the next line (which is the data)

start = mm.tell() # The starting byte of the data

length = len(mm.readline()) # Lines are of fixed length, so we'll grab that
mm.seek(start) # Move it back to the start after reading a line

# We know that the wavelength data is stored in column index 22 through 28
print(mm[start+22:start+28])

# We only need spectral irradiance values within the range of 348nm to 970nm,
# ideally with 1nm precision. So, we'll parse the data to find the first instance
# of 348nm, and move to it. We need to increment our position by 1, so that we start at the
# beginning of the wavelength number, and not at a space.
mm.seek(mm.find(b' 347.'))

# This drops us in the middle of that line, but that's fine. By moving 75 bytes along, we can
# reach the next wavelength value.

wavelengths = []
spectral_irradiance = []
uncertainty = []

# We want to parse by wavelength, but we only care about the first three sig figs (for now)
lbd = mm[mm.tell()+1:mm.tell()+4]
# We want lbd as an int so that we can compare it in our while loop. So, we do a roundabout
# thing whereby we first convert it to a string, and then to an int
lbd = int(lbd.decode('utf-8'))
print(lbd)

# Another while loop, to search the ENTIRE file
while(mm.tell() < len(mm)):

    # Now, parse through each wavelength up to and including our maxiumum of 970 
    # (The closest data point to 970 is actually 971.58)
    while(347 <= lbd <= 971):
        wavelength = mm[mm.tell()+1:mm.tell()+7] # We want the full wavelength, with decimals
        spec_irrad = mm[mm.tell()+22:mm.tell()+34]
        err = mm[mm.tell()+35:mm.tell()+45]

        # We add these values to our lists...
        if(float(spec_irrad.decode('utf-8')) > 0.5): # Easiest way to purge some weird artifacts from the data
            wavelengths.append(float(wavelength.decode('utf-8'))) # First index is wavelength
            spectral_irradiance.append(float(spec_irrad.decode('utf-8'))) # Second index is spectral irradiance
            uncertainty.append(float(err.decode('utf-8'))) # Third index is uncertainty

        # Move to the next line, at the position of the next wavelength
        try:
            mm.seek(mm.tell()+75)
            lbd = mm[mm.tell()+1:mm.tell()+4]
            lbd = int(lbd.decode('utf-8')) # Convert to a string, then to an int
        except ValueError as err:
            print(err)
            print("At byte {0}".format(mm.tell()))
            print(mm.readline())

    # Move to the next line, at the position of the next wavelength, looking for another 348nm
    try:
        mm.seek(mm.tell()+75)
        lbd = mm[mm.tell():mm.tell()+4]
        lbd = int(lbd.decode('utf-8'))
    except ValueError: # This will be thrown if we try to parse past the end of the file
        mm.seek(len(mm))


mm.close() # Just so I don't forget!
print("I'm free!")

print("Wavelengths: {0}".format(wavelengths[0:10]))
print("Spectral Irradiance: {0}".format(spectral_irradiance[0:10]))
print("Uncertainty: {0}".format(uncertainty[0:10]))


# All the data points are collected at the same wavelength. 
# So, let us average the spectral radiance at each wavelength.

wlgth = [] # The shortened wavelength list
spc_ir = [] # The shortened spectral irradiance
unc = [] # The shortened uncertainty
for i in range (0, len(wavelengths)):
    posn = search(wlgth, wavelengths[i]) # The position of the (maybe) existing wavelength
    if(posn == -1): # If we haven't processed this data point yet
        wlgth.append(wavelengths[i])
        spc_ir.append([spectral_irradiance[i]]) # This we process as lists, so that we can average them later
        unc.append([uncertainty[i]]) # Again, process as list
    else: # We must have processed data at this point already
        # Append the spectral irradiance and uncertainty to the lists at that wavelength
        spc_ir[posn].append(spectral_irradiance[i]) 
        unc[posn].append(uncertainty[i])

# Now that our data is collected into lists of lists, we can average things quickly
for i in range(0, len(spc_ir)):
    # I'm overwriting all the previous error I dragged along, since the standard deviation is
    # some orders of magnitude more signifacant than the measurement error
    unc[i] = stDev(spc_ir[i])
    spc_ir[i] = np.average(spc_ir[i])

print("Wlgth: {0}".format(wlgth[0:10]))
print("Spc Ir: {0}".format(spc_ir[0:10]))
print("Unc: {0}".format(unc[0:10]))

plt.errorbar(wlgth, spc_ir, yerr=unc, label="Averaged Data", fmt='k.')

# Finally, we need to bin our data into 1nm bins to align with the kepler sensitivity.
# I'm thinking we perform a linear interpolation between the two nearest datapoints, with
# wavelengths just above and below the desired value...
kepler_wlgth = np.linspace(348, 970, 970-348+1) # Perfect
spc_ir_binned = []
unc_binned = []
for i in range(0, len(kepler_wlgth)):
    j = 0
    while(wlgth[j]<kepler_wlgth[i]):
        j+=1
    spc_ir_binned.append(interpol(kepler_wlgth[i], wlgth[j-1], wlgth[j], spc_ir[j-1], spc_ir[j]))
    unc_binned.append(interpol(kepler_wlgth[i], wlgth[j-1], wlgth[j], unc[j-1], unc[j]))

print("kepler_wlgth: {0}".format(kepler_wlgth[0:10]))
print("spc_ir_binned: {0}".format(spc_ir_binned[0:10]))
print("unc_binned: {0}".format(unc_binned[0:10]))

# Save our lightcurve data to a file
out = open("solar_spectrum.dat", 'w')
print(kepler_wlgth.size)
for i in range(kepler_wlgth.size):
    out.write(str(kepler_wlgth[i]) + ' ' + str(spc_ir_binned[i]) + ' ' + str(unc_binned[i]) + '\n')
out.close()

# Plot our data, as a final check.
plt.errorbar(kepler_wlgth, spc_ir_binned, yerr=unc_binned, label="Binned Data", fmt='r.')
plt.xlabel("Wavelength [nm]")
plt.ylabel("Spectral Irradiance [?]")
plt.legend()
plt.show()