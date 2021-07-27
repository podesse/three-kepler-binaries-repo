'''
A rudementary python script as a follow-up to solar spectrum.py. This one computes the
AB magnitude of a solar-type star in the Kepler passband by numerically solving the
appropriate integrals (Eqn. 4 of Tonry et. al. 2012)

This may be one of the ugliest scripts I have ever written.
'''
import numpy as np
import mmap # Because one of my files is being naughty

import matplotlib.pylab as plt
from matplotlib import rc

c = 2.998e8 # The speed of light, roughly

# Load a file which is encoded as bytes for some reason
# New solution involved copying all the data to a new file, as text. But, this functionality
# is now here, and I'm not deleting it.
def loadDat(filename):
    # A convoluted method of bypassing all comments, which start with #
    with open(filename, "r+b") as f:
        # Create the random access file reader
        mm = mmap.mmap(f.fileno(), 0)
        # First, move to the last comment
        try: # Perhaps the comments don't exist
            mm.seek(mm.rfind(b'#'))
        except:
            print("Found no comments")
        mm.readline() # Will start us at the next line (which contains the data!)
        data = []
        # Parse the entire file
        while(mm.tell() < mm.size()):
            line = mm.readline().decode('utf-8')
            line = line.rstrip().split(' ') # Removes the EOL char, then splits the line
            data.append(np.array(line).astype(float))
    return data

# Switch the axes of an array so that we have x in terms of y, not x and y in a list at each
# element. Perhaps a numpy method already exists to handle this...
def moveAxes(array):
    axedList = []
    for j in range(0, len(array[0])): # For each axis
        axis = [] # Set aside memory for the axis
        for i in range(0, len(array)): # For each element along that axis
            axis.append(array[i][j]) # Put that element in our sub-list
        axedList.append(axis)
    return np.array(axedList)

# Convert all our wavelengths to frequency
# The wavelength array is always the list at index 0
# We also take into account that our wavelength values are in units of nanometers 
def toFrequency(array):
    for i in range(0, len(array[0])):
        array[0][i] = c/(array[0][i]*1e-9)
    return array

# Important to do this BEFORE switching the wavelengths to frequencies
# Our wavelengths are in nm, and the spectral response function in W/m^2/nm.
# To simplify, converted everything to meters before continuing
def irradToFrequency(array):
    for i in range(0, len(array[1])):
        array[1][i] = (array[1][i]/1e-9)*((array[0][i]*1e-9)**2)/c
    return array

# Numerically approximate the integral, using the specific integrand for this formula 
def riemannSum(frequencies, fluxDensity, responseFunciton):
    h = 6.626e-34 # Planck's constant
    sumTotal = 0
    # Put the first and last data points in separately!
    first = fluxDensity[0]*(1/(h*frequencies[0]))*responseFunciton[0]*(frequencies[1]-frequencies[0])
    length = len(frequencies)-1 # Trying to get the last data point, but the count starts at 0
    last = fluxDensity[length]*(1/(h*frequencies[length]))*responseFunciton[length]*(frequencies[length]-frequencies[length-1])
    sumTotal += first
    sumTotal += last
    #print("First and Last: {0} and {1}".format(first, last)) # Debugging
    #print("Sum total (before the full Riemann Sum): {0}".format(sumTotal)) # Debugging
    for i in range(1, (len(frequencies)-1)):
        dnu = 0.5*(frequencies[i+1]-frequencies[i-1]) # The width over which we sum.
        integrand = fluxDensity[i]*(1/(h*frequencies[i]))*responseFunciton[i]*dnu
        sumTotal += integrand
    # Our arrays are technically backwards, since we converted from wavelength to frequency.
    # So, we need to return the negative of the integral
    return -sumTotal

# Obtain the flux by integrating flux density through some passband w.r.t. frequency 
def getTheFlux(frequencies, fluxDensity, responseFunciton):
    sumTotal = 0
    # Put the first and last data points in separately!
    first = fluxDensity[0]*responseFunciton[0]*(frequencies[1]-frequencies[0])
    length = len(frequencies)-1 # Since we start at 0
    last = fluxDensity[length]*responseFunciton[length]*(frequencies[length]-frequencies[length-1])
    sumTotal += first
    sumTotal += last
    for i in range(1, (len(frequencies)-1)):
        dnu = 0.5*(frequencies[i+1]-frequencies[i-1]) # The width over which we sum.
        integrand = fluxDensity[i]*responseFunciton[i]*dnu
        sumTotal += integrand
    # Our arrays are technically backwards, since we converted from wavelength to frequency.
    # So, we need to return the negative ouf the integral
    return -sumTotal

solSpec = np.loadtxt("solar_spectrum.dat")
solSpec = moveAxes(solSpec) # This way, wavelength is its own list, separate from irradiance

# We'll need to get rid of the comments at the start of this file
kepRes = loadDat("kepler_response_hires1_parsable.dat")
kepRes = moveAxes(kepRes)


# Plot the two curves
rc('font',**{'family':'serif','serif':['Courier']})
rc('text', usetex=True)
o_color = '#e87932'
p_color = '#3d398c'
pref_figsize=[3.5, 3.5]

fig, ax1 = plt.subplots(figsize=pref_figsize)
#plt.title("Solar Irradiance and Spectral Response Function vs. Wavelength")
ln1 = ax1.plot(solSpec[0], solSpec[1], label="SSI", color=o_color)
ax1.set_xlabel("Wavelength (nm)")
ax1.set_ylabel('Spectral Irradiance (W/m'r'$^2$''/nm)')
ax2 = ax1.twinx()
ax2.set_ylabel('Response Function (Transmission Fraction)')
ln2 = ax2.plot(kepRes[0], kepRes[1], label="Kepler", color=p_color)
lns = ln1+ln2
lbls = [l.get_label() for l in lns]
ax1.legend(lns, lbls)
fig.tight_layout()
plt.savefig("wavelength_functions.png", dpi=300)


# Cool. The integral is with respect to frequency, rather than wavelength. So, we will need to
# convert our wavelength arrays to frequency arrays using the wave equation, c = \nu\lambda.
solSpec = irradToFrequency(solSpec)
# Do I have to give the Kepler response function a similar treatment, or is it just a ratio?

solSpec = toFrequency(solSpec)
kepRes = toFrequency(kepRes)

print("Way past cool.")
# Time to integrate. Or Riemann sum.

numerator_integral = riemannSum(solSpec[0], solSpec[1], kepRes[1])
print(numerator_integral)

# We can use our function again if we pass in 3631Jy for all the fluxDensity values instead!
Jy = 1e-26 # one jansky in SI units of W/m^2/Hz
janskys = 3631*Jy*np.ones_like(solSpec[0])

denominator_integral = riemannSum(solSpec[0], janskys, kepRes[1])
print(denominator_integral)

ABmag = -2.5*np.log10(numerator_integral/denominator_integral)
print("AB magnitude of the Sun through the Kepler filter: {0}".format(ABmag))


fig, ax1 = plt.subplots(figsize=pref_figsize)
#plt.title("Sol Irad. & Spect. Resp. Function vs. Frequency")
ln1 = ax1.plot(solSpec[0], solSpec[1], label="SSI", color=o_color)
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel('Spectral Irradiance (W/m'r'$^2$''/Hz)')
ax2 = ax1.twinx()
ax2.set_ylabel("Response Function (Transmission Fraction)")
ln2 = ax2.plot(kepRes[0], kepRes[1], label="Kepler", color=p_color)
lns = ln1+ln2
lbls = [l.get_label() for l in lns]
ax1.legend(lns, lbls)
fig.tight_layout()
plt.savefig("frequency_functions.png", dpi=300)


# Seeing how easily we were able to compute that integral... we can probably just search for
# an appropriate flux-scaling factor numerically to get ABmag = 12 ! That would certainly be
# easier than re-arranging our integrals...

# For instance:
orderOfMag = 12 - ABmag # We need to decrease by this order of magnitude
print("Desired increase along magnitude scale: {0}".format(orderOfMag))
# A increase in 5 ABmags corresponds to decreasing our flux by 2 orders of magnitude
k = 10**(-2*orderOfMag/5) # Let this be our scaling factor
print("Scaling our flux by: {0}".format(k))
numerator_integral = riemannSum(solSpec[0], k*solSpec[1], kepRes[1])
# denominator_integral can remain unchanged, since it is independent of our flux scaling
AB12 = -2.5*np.log10(numerator_integral/denominator_integral)
print("Our resulting magnitude, which we want to be equal to 12: {0}".format(AB12))
#print("The value of the numerator integral is: {0}".format(numerator_integral))
#print("That is far too high to be the flux of the star as observed by Kepler...")
flux = getTheFlux(solSpec[0], k*solSpec[1], kepRes[1])
print("By integrating our scaled spectral energy density without photon counting, we find the flux to be: {0} W/m^2.".format(flux))
solarflux = getTheFlux(solSpec[0], solSpec[1], kepRes[1])
print("As a sanity check, here is the Sun's flux through the Kepler passband: {0} W/m^2".format(solarflux))

#rearranged_numerator = denominator_integral*10**(-12/2.5)
#print("If we just re-arrange and solve for the numerator, we get: {0} Hz^2/m.".format(rearranged_numerator))
#print("The numerator cannot just be flux, since it does not have the correct units!")