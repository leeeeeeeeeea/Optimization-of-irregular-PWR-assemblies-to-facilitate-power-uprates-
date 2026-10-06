##The is for testing the WIMS-optimized assembly using Serpent.
import subprocess
import numpy as np
from get_pins import get_pins_1_8, get_w,get_sc
from BL324_1_8_maker import serp_input
from heat_map import cplot, calc_P, heat_map
from cobra_smallopti import cobra_input
from cobra_out import cobra_output
import matplotlib.pyplot as plt
import scipy.optimize 
import skopt as skopt
from scipy.stats import norm
from tqdm import tqdm
import json

asm_pitch = 21.5
P_ass=17.7E6
heated_length=3.66 #m

npins=324
p0 = 1.26
p2 = 17/19*p0 #new pitch
f=np.sqrt(264/npins) 
r= 0.4287 #outside radius of fuel pin (cm)
r_g=0.61 #outside radius of guide tube (cm)

gt_x,gt_y=get_w(p0)

def is_on_diagonal(pin_i):
    list_diagonal=[23,30,45,40,38,20,22]
    if pin_i in list_diagonal:
        return True
    return False

#See the original position 
file_res = open('Serpent for BL324.txt', mode ='r')
file_res.readline()
file_res.readline()
file_res.readline()
line_powers=file_res.readline()
P_original=json.loads(line_powers)
file_res.close()
pp_original=1.0863182242400666

#Test the optimum of power peaking given by WIMS 
#Getting the optimal positions into the pins list 
pins_original=get_pins_1_8(p0,p2,f,npins)

positions=[9.01943751, 1.12742969, 9.01943751, 2.25485938, 9.01943751, 3.38228907,
 9.01943751, 4.50971876, 9.01943751, 5.63714844, 9.01943751, 6.76457813,
 9.01943751, 7.89200782, 9.01943751, 1.12742969, 2.25485938, 1.12742969,
 3.38228907, 1.12742969, 4.50971876, 1.12742969, 5.63714844, 1.12742969,
 6.76457813, 1.12742969, 7.89189969, 1.12742969, 2.25485938, 3.38228907,
 2.29713569, 4.50971876, 2.25485938, 5.63714844, 2.25485938, 6.76457813,
 2.25485938, 7.89200782, 2.3112278,  8.11749376, 5.0734336,  6.82094962,
 4.63705199, 7.89200782, 8.11749376, 6.20086329, 7.12535563, 7.21555001,
 5.64580416, 5.0734336, 3.15680313, 6.20086329, 3.15680313, 5.63714844,
 4.05874688, 4.62246172, 5.86263438, 5.11502799]


moving_set=[]
for i in range (5,22):
    if i%2==0:
        moving_set.append(i)
moving_set=moving_set+list(range(23,47))

l_x=[]
l_y=[]
j=0 #marker in coords list 
for m in moving_set:
    if is_on_diagonal(m):
        l_x.append(positions[j])
        l_y.append(positions[j])
        j=j+1
    else:
        l_x.append(positions[j])
        l_y.append(positions[j+1])
        j=j+2

pins=pins_original.copy()
for i in range(len(moving_set)):
    m=moving_set[i]
    pins[m]=(l_x[i],l_y[i],f)

#Study the movement
distance_centers_avg=0
distance_centers_max=0
for i in moving_set:
    distance_centers=((pins[i][0] - pins_original[i][0]) ** 2 + (pins[i][1] - pins_original[i][1]) ** 2) ** 0.5
    if distance_centers>distance_centers_max:
        distance_centers_max=distance_centers
    distance_centers_avg+=distance_centers
distance_centers_avg=distance_centers_avg/len(moving_set)
print("average movement = ", distance_centers_avg)
print("max movement = ", distance_centers_max)

#Running Serpent to compare the pin powers between original and optimal positions 
n_pop=10000
n_cycles=1000

def func_serp():
    #Make the BL324_1_4 serpent input file 
    txt=serp_input(p0,p2,f,npins,pins,gt_x,gt_y,asm_pitch,P_ass,n_pop,n_cycles)

    #Run Serpent
    subprocess.run("sss2 -omp 10 BL324_1_8", shell=True, capture_output=True, text=True)

    #get result from Serpent
    (P,P_total)=calc_P(npins,pins,P_ass)

    diff_P=0
    for i in range(len(P)):
        diff_P+=np.abs(P[i]-P_original[i])/P[i]
    diff_P=diff_P/len(P)
    print("Average relative difference of pin powers is ",diff_P)
    # print("The optimized assembly pin powers")
    # print(str(P))

    #The power peakings
    plot_yes=True
    sc=get_sc(pins,gt_x,gt_y,f,p2)
    pp_new=heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,plot_yes)
    print("power peaking optimized = ", pp_new)
    print("power peaking original = ", pp_original)
    diff=pp_original-pp_new
    print("difference power peaking = ", diff)

    #create Cobra input
    plot_yes=True
    uprate_case = None #None, "pow "and "both"
    calc_dnb=True #inlet +2K, 95% nominal flow, 112% power and 1.587 radial peaking factor
    nax=16 #number of axial layers
    sc=get_sc(pins,gt_x,gt_y,f,p2)
    txt=cobra_input(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes,heated_length)

    #Run Cobra
    subprocess.run("/usr/software/COBRA/source/cobraen   /home/lg779/Small_optimisation_Ben_subchan/INPFILE ", shell=True, capture_output=True, text=True)

    #Cobra output 
    (P_drop_line,MDNBR)=cobra_output(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes)
    print("MDNBR = ", MDNBR)
    return (MDNBR,pp_new)

iter=100

MDNBR_list=[]
pp_list=[]
for i in tqdm(range(iter)):
    (MDNBR,pp)=func_serp()
    MDNBR_list.append(MDNBR)
    pp_list.append(pp)

# Fit a normal distribution to the data:
mu, std = norm.fit(MDNBR_list)
# Plot the histogram.
plt.hist(MDNBR_list, bins=25, density=True, alpha=0.6, color='g')
# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2)
title = "Fit results: MDNBR = %.4f,  std = %.4f" % (mu, std)
plt.title(title)
plt.savefig("MDNBR fit for WIMS optimized assembly.png")
plt.close()

mu, std = norm.fit(pp_list)
# Plot the histogram.
plt.hist(pp_list, bins=25, density=True, alpha=0.6, color='g')
# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2)
title = "Fit results: Power peaking = %.4f,  std = %.4f" % (mu, std)
plt.title(title)
plt.savefig("Peaking fit for WIMS optimized assembly.png")
plt.close()