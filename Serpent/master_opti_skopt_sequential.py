##The file that commands the others 
#Runs the optimization then calls BL324_1_4_maker, Serpent,heat_map with Serpent results, cobra_smallopti, COBRA itself,cobra_out
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

n_pop=5000
n_cycles=1000

#The standard deviation for MDNBR 
MDNBR_error=0.03
if n_pop==5000 and n_cycles==100:
    MDNBR_error=0.02
if n_pop==5000 and n_cycles==500:
    MDNBR_error=0.0132
if n_pop==5000 and n_cycles==1000:
    MDNBR_error=0.0091

#The standard deviation for power peaking  
pp_error=0.01
if n_pop==5000 and n_cycles==100:
    pp_error=0.01
if n_pop==5000 and n_cycles==500:
    pp_error=0.0041
if n_pop==5000 and n_cycles==1000:
    pp_error=0.0023

asm_pitch = 21.5
P_ass=17.7E6
heated_length=3.66 #m

npins=324
p0 = 1.26
p2 = 17/19*p0 #new pitch
f=np.sqrt(264/npins) 
r= 0.4287 #outside radius of fuel pin (cm)
r_g=0.61 #outside radius of guide tube (cm)

gt_x,gt_y =get_w(p0)

iter=0
position_list=[]
peaking_list=[]
MDNBR_list=[]

def func_basic(coords):
    (x_m,y_m)=coords
    #returns the figure of merit F
    for p in pins_original:
        x=p[0]
        y=p[1]
        distance = ((x_m - x) ** 2 + (y_m - y) ** 2) ** 0.5
        if distance<=2*r+0.2:
            F=100
            #print("problem pin position : too close to another pin")
            return F

    for i in range(len(gt_x)):
        x=gt_x[i]
        y=gt_y[i]
        distance = ((x_m - x) ** 2 + (y_m - y) ** 2) ** 0.5
        if distance<=r+r_g:
            F=100
            #print("problem pin positon : overlap with guide tube")
            return F

    pins=pins_original.copy()
    pins[m]=(x_m,y_m,f)
    print("moving pin ", m, 'to', x_m,y_m)
    global iter
    iter+=1
    position_list.append(coords)

    #Make the BL324_1_4 serpent input file 
    txt=serp_input(p0,p2,f,npins,pins,gt_x,gt_y,asm_pitch,P_ass,n_pop,n_cycles)

    #Run Serpent
    subprocess.run("sss2 -omp 10 BL324_1_8", shell=True, capture_output=True, text=True)

    #get result from Serpent
    (P,P_total)=calc_P(npins,pins,P_ass)
    plot_yes=True
    peaking=heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,plot_yes)
    print("power peaking = ", peaking)
    peaking_list.append(peaking)
    F=peaking

    #create Cobra input
    uprate_case = None #None, "pow "and "both"
    calc_dnb=True #inlet +2K, 95% nominal flow, 112% power and 1.587 radial peaking factor
    nax=16 #number of axial layers

    txt=cobra_input(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes,heated_length)

    #Run Cobra
    subprocess.run("/usr/software/COBRA/source/cobraen   /home/lg779/Small_optimisation_Ben_subchan/INPFILE ", shell=True, capture_output=True, text=True)

    #Cobra output 
    (P_drop_line,MDNBR)=cobra_output(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes)
    print("MDNBR = ", MDNBR)
    MDNBR_list.append(MDNBR)
    if MDNBR<1.91-MDNBR_error: #reference assembly MDNBR is 1.91, we have margin of error of 1 standard deviation
        print("Low MDNBR, refused this design")
        F=100 
    return F


def func_diag(x_m):
    #returns the figure of merit F
    if type(x_m) is list:
        x_m=x_m[0]
    F=func_basic((x_m,x_m))
    return F


#moving the pins
moving_order=[45]
pins_original=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins_original,gt_x,gt_y,f,p2)

file_res = open('Optimized assembly.txt', mode ='w')

for m in moving_order:
    print("Moving pin ", m)
    x_m_o=pins_original[m][0] #original position of the pin m
    y_m_o=pins_original[m][1]
    pins_original[m]=(0,0,f) #we keep the spot open (and it won't cause an undy overlapping)

    #Optimize 
    if m in [23,30,45,40,38,20,22]: #diagonal pins
        origin=[x_m_o]
        y0=func_diag(x_m_o)

        res=skopt.gbrt_minimize(func_diag,[(0,asm_pitch/2)],n_calls=100,n_initial_points=10,x0=origin,y0=[y0])
        x_min=res.x[0]
        pins_original[m]=(x_min,x_min,f)
        file_res.writelines(["Results for m =", str(m),", x0 = ",str(x_m_o),", F at x0=",str(y0),", x_min =",str(x_min),", F at x_min =",str(res.fun),'\n'])

    else: #non diagonal pins, curently allows 39 and 85
        l_positions=[(x_m_o,y_m_o)]
        origin=(x_m_o,y_m_o)
        y0=func_basic(origin)

        res=skopt.gbrt_minimize(func_basic,[(0,asm_pitch/2),(0,asm_pitch/2)],n_calls=600,n_initial_points=60,x0=origin,y0=y0)
        pos_min=res.x
        pins_original[m]=pos_min
        file_res.writelines(["Results for m =", str(m),", x0 = ",str(origin),", F at x0=",str(y0),", x_min =",str(pos_min),", F at x_min =",str(res.fun),'\n'])

file_res.write("Final optimized assembly \n")
for m in moving_order:
    file_res.writelines([str(m),str(pins_original[m]),'\n'])
file_res.write(str(pins_original))
file_res.close()
