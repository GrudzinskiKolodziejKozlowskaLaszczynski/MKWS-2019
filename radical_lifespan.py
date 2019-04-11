"""
code based on: 
http://cantera.github.io/docs/sphinx/html/cython/examples/reactors_combustor.html?fbclid=IwAR34uYtWAVZ9yuoU9lQK9lO_OJxof3Mi5EV7kj5lgfxfHvOQxid3MPs6PrY

"""
# Some variables named in Polish, there are descriptions for better understanding
# libraries import
import math
import cantera as ct


print 'Starting conditions: T0=300 K, P0 = 101 325 Pa, fi=0.5'
print 'Increase in condtions" values: deltaT = 20 K, deltaP = 1 000 Pa'
print 'It"s a test, only temperature gets increased for now, 40 iterations to be executed'
licz = 0

#declaring starting conditions: temperature, pressure and mass fractions as an equivalence ratio
T0 = 300.0
P0 = ct.one_atm
fi = 0.5                # equivalence ratio of methane/air mixture
epsilon = 0.0008        # limit, over which OH is classified as "present in significant amount" in mixture
czasy = []              # list holding solutions - lifespans
temperatury = []        # list holding solutions - temperatures
cisnienia = []          # list holding solutions - pressures
maxstezenia = []        # list holding solutions - maximal mass fracions of OH

# time mark before current iteration
t_ante =0.0 


for i in range(40):
    
    
    t_life = 0.0 # lifespan counter 
    ymax =0.0 # maximal mass fraction indicator
 # starting conditions updating algorithm  
    T=T0+20*i
# creating object to simulate gas
    gas = ct.Solution('gri30.xml')

# methane container as a source of mass stream
    gas.TPX = T, P0, 'CH4:1.0'
    fuel_in = ct.Reservoir(gas)
    fuel_mw = gas.mean_molecular_weight

# use predefined function Air() for the air inlet
    air = ct.Solution('air.xml')
    air_in = ct.Reservoir(air)
    air_mw = air.mean_molecular_weight

# to ignite the fuel/air mixture, we'll introduce a pulse of radicals. The
# steady-state behavior is independent of how we do this, so we'll just use a
# stream of pure atomic hydrogen.
    gas.TPX = T, P0, 'H:1.0'
    igniter = ct.Reservoir(gas)

# create the combustor, and fill it in initially with N2
    gas.TPX = T, P0, 'N2:1.0'
    przestrzen_obliczeniowa = ct.IdealGasReactor(gas)
    przestrzen_obliczeniowa.volume = 1.0

# outlet from reactor
    exhaust = ct.Reservoir(gas)


# mass streams of methane and air - setting A/F ratio
    factor = 0.1
    air_mdot = factor * 9.52 * air_mw
    fuel_mdot = factor * fi * fuel_mw

# mass flow stabilizer for methane
    m1 = ct.MassFlowController(fuel_in, przestrzen_obliczeniowa, mdot=fuel_mdot)

# mass flow stabilizer for air
    m2 = ct.MassFlowController(air_in, przestrzen_obliczeniowa, mdot=air_mdot)

# ignition modelled by Gaussian pulse
    fwhm = 0.2
    amplitude = 0.1
    t0 = 1.0
    igniter_mdot = lambda t: amplitude * math.exp(-(t-t0)**2 * 4 * math.log(2) / fwhm**2)
    m3 = ct.MassFlowController(igniter, przestrzen_obliczeniowa, mdot=igniter_mdot)

# pressure constraint on exhaust, applied by using a valve
    v = ct.Valve(przestrzen_obliczeniowa, exhaust, K=1.0)

# creating simulation of reactor network
    sim = ct.ReactorNet([przestrzen_obliczeniowa])

# setting time limits of simulation
    tfinal = 5.0
    tnow = 0.0
    
   # print '     t[s]       P[PA]       T[K]        CH4[%]    O2[%]       OH[%]     N2[%]'       

    while tnow < tfinal:
            tnow = sim.step()
           # print przestrzen_obliczeniowa.Y[gas.species_index('OH')]
            if przestrzen_obliczeniowa.Y[gas.species_index('OH')] > epsilon:
        
                t_life=t_life+(tnow-t_ante)
                
            if przestrzen_obliczeniowa.Y[gas.species_index('OH')] > ymax:
               ymax=przestrzen_obliczeniowa.Y[gas.species_index('OH')]
    # solution lists updating and also updating time counter           
            t_ante=tnow   
    czasy.append(t_life)
    temperatury.append(T)
    cisnienia.append(P0)
    maxstezenia.append(ymax)

# printing solution for each set of starting conditions
# respectably: lifespan, temperature, pressure and maximum mass fraction of OH radicals
print 't_life [s]       T [K]      P [Pa]      OHmax [%]'
for i in xrange(len(czasy)):
    print ('%10.6f  %10.2f  %10.2f  %10.4f' ) % (czasy[i], temperatury[i], cisnienia[i], 100*maxstezenia[i])

