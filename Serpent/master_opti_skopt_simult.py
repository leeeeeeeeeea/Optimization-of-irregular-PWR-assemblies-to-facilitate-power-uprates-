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
n_cycles=100

#The maximum relative error likely to happen on MDNBR 
rel_error=0.05
if n_pop==5000 and n_cycles==100:
    rel_error=0.03

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
sc=get_sc(npins)

iter=0
position_list=[]
peaking_list=[]
MDNBR_list=[]

def func_double(coords):
    [(x_m1,y_m1),(x_m2,y_m2)]=coords
    #Test distances (two pins among each other, both with other pins, both with guide tubes)
    distance = ((x_m1 - x_m2) ** 2 + (y_m1 - y_m2) ** 2) ** 0.5
    if distance<=2*r+0.2:
        F=100
        return F
    for p in pins_original:
        x=p[0]
        y=p[1]
        distance = ((x_m1 - x) ** 2 + (y_m1 - y) ** 2) ** 0.5
        if distance<=2*r+0.2:
            F=100
            return F
        distance = ((x_m2 - x) ** 2 + (y_m2 - y) ** 2) ** 0.5
        if distance<=2*r+0.2:
            F=100
            return F

    for i in range(len(gt_x)):
        x=gt_x[i]
        y=gt_y[i]
        distance = ((x_m1 - x) ** 2 + (y_m1 - y) ** 2) ** 0.5
        if distance<=r+r_g:
            F=100
            return F
        distance = ((x_m2 - x) ** 2 + (y_m2 - y) ** 2) ** 0.5
        if distance<=r+r_g:
            F=100
            return F

    pins=pins_original.copy()
    pins[moving_set[0]]=(x_m1,y_m1,f)
    pins[moving_set[1]]=(x_m2,y_m2,f)
    global iter
    iter+=1
    position_list.append(coords)

    #Make the BL324_1_4 serpent input file 
    txt=serp_input(p0,p2,f,npins,pins,gt_x,gt_y,asm_pitch,P_ass,n_pop,n_cycles)
    #print(txt)

    #Run Serpent
    subprocess.run("sss2 -omp 10 BL324_1_4", shell=True, capture_output=True, text=True)
    #print("Serpent ran")

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
    #print(txt)

    #Run Cobra
    subprocess.run("/usr/software/COBRA/source/cobraen   /home/lg779/Small_optimisation_Ben_subchan/INPFILE ", shell=True, capture_output=True, text=True)
    #print("Cobra ran")

    #Cobra output 
    (P_drop_line,MDNBR)=cobra_output(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes)
    print("MDNBR = ", MDNBR)
    MDNBR_list.append(MDNBR)
    if MDNBR<1.91-rel_error*1.91: #reference assembly MDNBR is 1.91, we have margin of error from stuyding 
        print("Low MDNBR, refused this design")
        F=100 
    return F


def func_diag_double(arg):
    (x_m1,x_m2)=arg
    F=func_double([(x_m1,x_m1),(x_m2,x_m2)])
    return F


#moving the pins
moving_set=[71,68]
pins_original=get_pins_original(p0,p2,f,npins)
file_res = open('Optimized assembly simult.txt', mode ='w')
x_pin1_o=pins_original[moving_set[0]][0] #For now they are both diagonal 
x_pin2_o=pins_original[moving_set[1]][1]
print(x_pin1_o,x_pin2_o)
pins_original[moving_set[0]]=(0,0,f) #we keep the spot open (and it won't cause an undy overlapping)
pins_original[moving_set[1]]=(0,0,f)

#Optimize 
origin=[x_pin1_o,x_pin2_o]
y0=func_diag_double((x_pin1_o,x_pin2_o))

res=skopt.gbrt_minimize(func_diag_double,[(0,asm_pitch/2),(0,asm_pitch/2)],n_calls=5000,n_initial_points=50,x0=origin,y0=[y0])
print(res.x)
x_min1=res.x[0]
x_min1=res.x[1]


file_res.write("Final optimized assembly \n")
for m in moving_set:
    file_res.writelines([str(m),str(pins[m]),'\n'])
file_res.write(str(pins_original))
file_res.close()

#le code va marcher par magie si j'ajoute cette ligne tkt <3