import numpy as np
import subprocess
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

from mpl_toolkits.mplot3d import Axes3D

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

pins_original=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins_original,gt_x,gt_y,f,p2)

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
    global iter
    iter+=1
    position_list.append(coords)


    #Make the WIMS input file 
    WIMS_input(p0,p2,pins,gt_x,gt_y,asm_pitch,P_ass/8,npins)
    #remove previous powermap.txt for the new output to be written 
    subprocess.run("rm powermap.txt", shell=True, capture_output=True, text=True)
    #Run WIMS
    subprocess.run("./runwims", shell=True, capture_output=True, text=True)

    #get result from Serpent
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


def func_diag(x_m):
    # scipy.optimize.minimize always passes x as a numpy array,
    # even for scalar problems — extract the float explicitly
    x_m = float(np.asarray(x_m).flat[0])
    F = func_basic((x_m, x_m))
    return F

#moving the pins
m=38
print("m=", m)

pins_original=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins_original,gt_x,gt_y,f,p2)
x_m_o=pins_original[m][0] #original position of the pin m
y_m_o=pins_original[m][1]
pins_original[m]=(0,0,f)


##Test 1, distribution of power peaking and MDNBR
origin=x_m_o
for i in tqdm(range(1)):
    F=func_diag(origin)
# l_ref=[]
# for i in range(iter):
#     l_ref.append(1.91)
# plt.plot(range(iter),MDNBR_list,marker='x',label='BL324 assembly')
# plt.plot(range(iter),l_ref,label='Reference assembly')
# plt.legend()
# plt.xlabel("Iterations")
# plt.ylabel("MDNBR")
# plt.title("MDNBR for original BL324 assembly")
# plt.savefig("MDNBR position of pin 84.png")
# plt.close()

# plt.plot(range(iter),peaking_list,marker='x')
# plt.xlabel("Iterations")
# plt.ylabel("Power peaking")
# plt.title("Power peaking for original BL324 assembly")
# plt.savefig("Peaking position of pin 84.png")    
# plt.close()

# # Fit a normal distribution to the data:
# mu, std = norm.fit(MDNBR_list)
# # Plot the histogram.
# plt.hist(MDNBR_list, bins=25, density=True, alpha=0.6, color='g')
# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# plt.plot(x, p, 'k', linewidth=2)
# title = "Fit results: MDNBR = %.4f,  std = %.4f" % (mu, std)
# plt.title(title)
# plt.savefig("MDNBR fit.png")
# plt.close()
# mu, std = norm.fit(peaking_list)
# # Plot the histogram.
# plt.hist(peaking_list, bins=25, density=True, alpha=0.6, color='g')
# # Plot the PDF.
# xmin, xmax = plt.xlim()
# x = np.linspace(xmin, xmax, 100)
# p = norm.pdf(x, mu, std)
# plt.plot(x, p, 'k', linewidth=2)
# title = "Fit results: Power peaking = %.4f,  std = %.4f" % (mu, std)
# plt.title(title)
# plt.savefig("Peaking fit.png")
# plt.close()


# #Test 2, moving pin 
# if m==45:
#     origin=x_m_o
#     print(origin)

#     #Limitations for position of pin 45 calculated by hand 
#     #From guide tube 
#     x_g=3*p0
#     x_guide_limit=x_g+(r+r_g)/np.sqrt(2)
#     #from the couple of pins : 46 and symmetric
#     coord_1=(5.2*p2,4.53*p2,f) #pin 46
#     coord_2=(4.53*p2,5.2*p2,f)
#     coord_C=((coord_1[0]+coord_2[0])/2,(coord_1[1]+coord_2[1])/2)
#     d=np.sqrt((coord_C[0]-coord_1[0])**2+(coord_C[1]-coord_1[1])**2)
#     a=np.sqrt((2*r+0.2)**2-d**2)
#     x_pins_limit=coord_C[0]-a/np.sqrt(2)
#     l_x=[]
#     file_res = open('WIMS power peaking position 45 long.txt', mode ='w')
#     l_pp=[]

#     n_iter=50
#     for i in tqdm(range(n_iter)):
#         l_x.append(x_guide_limit+0.001+i*(x_pins_limit-x_guide_limit-0.001)/n_iter)
#         l_pp.append(func_diag(x_guide_limit+0.001+i*(x_pins_limit-x_guide_limit-0.001)/n_iter))
    
#     file_res.write("l_x")
#     file_res.write(str(l_x))
#     file_res.write("l_pp \n")
#     file_res.write(str(l_pp))

#     file_res.close()

    # plt.plot(l_x,MDNBR_list,marker='x')
    # plt.xlabel("Position of pin 45")
    # plt.ylabel("MDNBR")
    # plt.title("MDNBR for different positions of pin 45")
    # plt.savefig("MDNBR for different positions of pin 45.png")
    # plt.close()

    # plt.plot(l_x,peaking_list,marker='x')
    # plt.xlabel("Position of pin 45")
    # plt.ylabel("Power peaking")
    # plt.title("Power peaking for different positions of pin 45")
    # plt.savefig("Peaking for different positions of pin 45.png")    
    # plt.close()


# #Optimize 
# if m==45 or m==40 or m==38 :
#     origin=[x_m_o]
#     y0=func_diag(x_m_o)
#     options={
#         'xatol': 0.01,   # stop when position changes < 0.01 cm
#         'fatol': 0.001,  # stop when F changes < 0.001
#         'maxiter': 50,
#     }
#     res=scipy.optimize.minimize(func_diag,x_m_o,bounds=[(0,asm_pitch/2)], method='Nelder-Mead',options=options)    
#     x_min=res.x[0]
#     print("x_min =",x_min)
#     print("F at x_min =",res.fun)
#     l_x=[]
#     for p in position_list:
#         l_x.append(p[0])
#     l_x_plot=l_x.copy()
#     l_x_plot.sort()
#     MDNBR_plot=[]
#     peaking_plot=[]
#     for el in l_x_plot:
#         i=l_x.index(el)
#         MDNBR_plot.append(MDNBR_list[i])
#         peaking_plot.append(peaking_list[i])
#     plt.plot(l_x_plot,MDNBR_plot,marker='x')
#     plt.xlabel("Position (x=y)")
#     plt.ylabel("MDNBR")
#     plt.title("MDNBR for different positions of pin opti")
#     plt.savefig("MDNBR for different positions of pin opti.png")
#     plt.close()

#     plt.plot(l_x_plot,peaking_plot,marker='x')
#     plt.xlabel("Position (x=y)")
#     plt.ylabel("Power peaking")
#     plt.title("Power peaking for different position of pin opti")
#     plt.savefig("Peaking for different position of pin opti.png")    
#     plt.close()
#     file_res = open('Serpent power peaking position 38.txt', mode ='w')

    
#     file_res = open('WIMS power peaking position 38.txt', mode ='w')
#     file_res.write(str(position_list))
#     file_res.write("l_p \n")
#     file_res.write(str(peaking_list))
#     file_res.close()



# else: #non diagonal pins
#     #l_positions=[(x_m_o,y_m_o)]
#     origin=(x_m_o,y_m_o)
#     y0=func_basic(origin)

#     options={
#         'xatol': 0.01,   # stop when position changes < 0.01 cm
#         'fatol': 0.001,  # stop when F changes < 0.001
#         'maxiter': 50,
#     }
#     res=scipy.optimize.minimize(func_basic,origin,bounds=[(0,asm_pitch/2)], method='Nelder-Mead',options=options)
#     print("\n Results")
#     print("x0 = ",origin)
#     print("F at x0=",y0)
#     pos_min=res.x
#     print("position min =",pos_min)
#     # print("position list", position_list)
#     # print("peaking list", peaking_list)
#     #print("F at position min =",res.fun)
#     l_x=[]
#     l_y=[]
#     for el in position_list:
#         l_x.append(el[0])
#         l_y.append(el[1])

#     fig = plt.figure()
#     plt.scatter(l_x, l_y, c=peaking_list, cmap='summer')
#     plt.colorbar()
#     plt.xlabel("x (cm)")
#     plt.ylabel("y (cm)")
#     plt.title("Power peaking for different position of pin " + str(m))
#     fig.savefig("Peaking for different position of pin opti.png")    


# #Test 4, compare Serpent  
# #For pin 45
# m=45
# print("m=", m)

# pins_original=get_pins_1_8(p0,p2,f,npins)
# sc=get_sc(pins_original,gt_x,gt_y,f,p2)
# x_m_o=pins_original[m][0] #original position of the pin m
# y_m_o=pins_original[m][1]
# pins_original[m]=(0,0,f)

# origin=x_m_o
# print(origin)

# file_res = open('WIMS power peaking position 45.txt', mode ='w')

# l_x=[4.52,4.55,4.56,4.59,4.61,4.65,4.7,4.75,4.8]
# l_pp=[]
# for x in tqdm(l_x):
#     F=func_diag(x)
#     l_pp.append(F)

# file_res.write(str(l_pp))
# file_res.close()

