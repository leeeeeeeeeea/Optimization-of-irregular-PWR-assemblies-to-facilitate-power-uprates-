import subprocess
import numpy as np
from get_pins import get_pins_1_8, get_w,get_sc
from BL324_1_8_WIMSmaker import WIMS_input
from heat_map import cplot, calc_P, heat_map
import matplotlib.pyplot as plt
import scipy.optimize 
import skopt as skopt
from scipy.stats import norm
from cobra_smallopti import cobra_input
from cobra_out import cobra_output
from tqdm import tqdm
import scipy

asm_pitch = 21.5
P_ass=17.7E6
heated_length=3.66 

npins=324
p0 = 1.26
p2 = 17/19*p0 #new pitch
f=np.sqrt(264/npins) 
r= 0.4287 #outside radius of fuel pin (cm)
r_g=0.61 #outside radius of guide tube (cm)

gt_x,gt_y =get_w(p0)

pins_original=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins_original,gt_x,gt_y,f,p2)

iter=0
position_list=[]
peaking_list=[]
MDNBR_list=[]

def is_on_diagonal(pin_i):
    list_diagonal=[23,30,45,40,38,20,22]
    if pin_i in list_diagonal:
        return True
    return False

def func_simult(coords):

    #lists of x and y for all pins moving 
    l_x=[]
    l_y=[]
    j=0 #marker in coords list 
    for m in moving_set:
        if is_on_diagonal(m):
            l_x.append(coords[j])
            l_y.append(coords[j])
            j=j+1
        else:
            l_x.append(coords[j])
            l_y.append(coords[j+1])
            j=j+2

    #Test distances (pins among each other, all with other pins, all with guide tubes)
    for i in range(len(moving_set)):
        for j in range(len(moving_set)):
            if i!=j:
                distance= ((l_x[i] - l_x[j]) ** 2 + (l_y[i] - l_y[j]) ** 2) ** 0.5
                if distance<=2*r+0.2:
                    F=100
                    return F

    for p in pins_original:
        x=p[0]
        y=p[1]
        for i in range(len(moving_set)):
            distance = ((l_x[i] - x) ** 2 + (l_y[i] - y) ** 2) ** 0.5
            if distance<=2*r+0.2:
                F=100
                return F

    for i in range(len(gt_x)):
        x=gt_x[i]
        y=gt_y[i]
        for i in range(len(moving_set)):
            distance = ((l_x[i] - x) ** 2 + (l_y[i] - y) ** 2) ** 0.5
            if distance<=2*r+0.2:
                F=100
                return F

    pins=pins_original.copy()
    for i in range(len(moving_set)):
        pins[moving_set[i]]=(l_x[i],l_y[i],f)
    position_list.append(coords)
    global iter
    iter+=1
    print("iteration = ", iter)

    #Make the WIMS input file 
    WIMS_input(p0,p2,pins,gt_x,gt_y,asm_pitch,P_ass/8,npins)
    #remove previous powermap.txt for the new output to be written 
    subprocess.run("rm powermap.txt", shell=True, capture_output=True, text=True)
    #Run WIMS
    subprocess.run("./runwims", shell=True, capture_output=True, text=True)

    #get result from WIMS
    (P,P_tot)=calc_P(pins, gt_x, gt_y,P_ass/8)
    plot_yes=True
    peaking=heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,plot_yes)
    print("Power peaking = ", peaking)
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
    # if MDNBR<1.91: #reference assembly MDNBR is 1.91
    #     print("Low MDNBR, refused this design")
    #     F=100 
    return F


#moving the pins
moving_set=[]
for i in range (5,22):
    if i%2==0:
        moving_set.append(i)
moving_set=moving_set+list(range(23,47))
print(moving_set)
pins_original=get_pins_1_8(p0,p2,f,npins)

pins_original=get_pins_1_8(p0,p2,f,npins)

file_res = open('Optimized assembly simult.txt', mode ='w')

origin=[]
for m in moving_set:
    if is_on_diagonal(m):
        origin.append(pins_original[m][0])
    else:
        origin.append(pins_original[m][0])
        origin.append(pins_original[m][1])
for m in moving_set:
    pins_original[m]=(0,0,f) #we keep the spot open (and it won't cause an undy overlapping)

bounds=[]
for m in moving_set:
    if is_on_diagonal(m):
        bounds.append((0,asm_pitch/2))
    else:
        bounds.append((0,asm_pitch/2))
        bounds.append((0,asm_pitch/2))

options={
    'xatol': 0.01,   # stop when position changes < 0.01 cm
    'fatol': 0.001,  # stop when F changes < 0.001
    'maxiter': 10,
        }
res=scipy.optimize.minimize(func_simult,origin,bounds=bounds, method='Nelder-Mead',options=options)

file_res.write("Final optimized assembly \n")
file_res.write(str(moving_set)+'\n')
file_res.write(str(res))
file_res.write("\n")
file_res.write(str(res.x))
file_res.close()

plt.plot(range(iter),peaking_list,marker='x')
plt.xlabel("iteration")
plt.ylabel("Power peaking")
plt.title("Power peaking for iterations simultaneous optimisation")
plt.savefig("Peaking for iterations simult opti.png")
plt.close()

plt.plot(range(iter),MDNBR_list,marker='x')
plt.xlabel("iteration")
plt.ylabel("MDNBR")
plt.title("MDNBR for iterations simultaneous optimisation")
plt.savefig("MDNBR for iterations simult opti.png")
plt.close()
