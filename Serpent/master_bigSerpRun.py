##This is one big Serpent run to be saved in a file
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

file_res = open('Serpent for BL324.txt', mode ='w')

#We call Serpent ONCE ! 
n_pop=500000
n_cycles=1000

pins=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins,gt_x,gt_y,f,p2)

#Make the BL324_1_4 serpent input file 
txt=serp_input(p0,p2,f,npins,pins,gt_x,gt_y,asm_pitch,P_ass,n_pop,n_cycles)

#Run Serpent
subprocess.run("sss2 -omp 10 BL324_1_8 ", shell=True, capture_output=True, text=True)

#get result from Serpent
(P,P_total)=calc_P(npins,pins,P_ass)
plot_yes=True
peaking=heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,plot_yes)
print("power peaking = ", peaking)

file_res.write("The Serpent pin powers for BL324 \n")
file_res.write("n pop = " + str(n_pop)+"\n")
file_res.write("n cycles = " + str(n_cycles)+"\n")

file_res.write(str(P))
file_res.write("\n")
file_res.write("power peaking = " + str(peaking))
file_res.close()
