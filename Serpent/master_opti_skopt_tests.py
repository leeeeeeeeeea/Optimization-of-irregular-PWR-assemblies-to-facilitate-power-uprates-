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
from tqdm import tqdm

n_pop=10000
n_cycles=1000

#The standard deviation for MDNBR 
MDNBR_error=0.03
if n_pop==5000 and n_cycles==100:
    MDNBR_error=0.02
if n_pop==5000 and n_cycles==500:
    MDNBR_error=0.0132
if n_pop==5000 and n_cycles==1000:
    MDNBR_error=0.0091
if n_pop==10000 and n_cycles==1000:
    MDNBR_error=0.0067

#The standard deviation for power peaking  
pp_error=0.01
if n_pop==5000 and n_cycles==100:
    pp_error=0.01
if n_pop==5000 and n_cycles==500:
    pp_error=0.0041
if n_pop==5000 and n_cycles==1000:
    pp_error=0.0023
if n_pop==10000 and n_cycles==1000:
    pp_error=0.0018


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

    #Make the BL324_1_4 serpent input file 
    txt=serp_input(p0,p2,f,npins,pins,gt_x,gt_y,asm_pitch,P_ass,n_pop,n_cycles)

    #Run Serpent
    subprocess.run("sss2 -omp 10 BL324_1_8 ", shell=True, capture_output=True, text=True)

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
    if MDNBR<1.91-MDNBR_error: #reference assembly MDNBR is 1.91, we allow 1 standard deviation 
        print("Low MDNBR, refused this design")
        F=100 
    return F


def func_diag(x_m):
    #returns the figure of merit F
    # if type(x_m) is list:
    #     x_m=x_m[0]
    F=func_basic((x_m,x_m))
    return F


#moving the pins
m=45
print("m=", m)

pins_original=get_pins_1_8(p0,p2,f,npins)
sc=get_sc(pins_original,gt_x,gt_y,f,p2)
x_m_o=pins_original[m][0] #original position of the pin m
y_m_o=pins_original[m][1]
pins_original[m]=(0,0,f)

# #Plot names of pins 
# for i,p in enumerate(pins_original):
#     plt.plot(p[0],p[1],marker="$"+str(i)+"$")
# plt.savefig("Name of pins 1_8th.png")
# plt.close()


#Test 1, distribution of power peaking and MDNBR
if m==45:
    origin=x_m_o
    for i in tqdm(range(10)):
        F=func_diag(origin)

#     l_ref=[]
#     for i in range(iter):
#         l_ref.append(1.91)
#     plt.plot(range(iter),MDNBR_list,marker='x',label='BL324 assembly')
#     plt.plot(range(iter),l_ref,label='Reference assembly')
#     plt.legend()
#     plt.xlabel("Iterations")
#     plt.ylabel("MDNBR")
#     plt.title("MDNBR for original BL324 assembly")
#     plt.savefig("MDNBR position of pin 84.png")
#     plt.close()

#     plt.plot(range(iter),peaking_list,marker='x')
#     plt.xlabel("Iterations")
#     plt.ylabel("Power peaking")
#     plt.title("Power peaking for original BL324 assembly")
#     plt.savefig("Peaking position of pin 84.png")    
#     plt.close()

#     # Fit a normal distribution to the data:
#     mu, std = norm.fit(MDNBR_list)
#     # Plot the histogram.
#     plt.hist(MDNBR_list, bins=25, density=True, alpha=0.6, color='g')
#     # Plot the PDF.
#     xmin, xmax = plt.xlim()
#     x = np.linspace(xmin, xmax, 100)
#     p = norm.pdf(x, mu, std)
#     plt.plot(x, p, 'k', linewidth=2)
#     title = "Fit results: MDNBR = %.4f,  std = %.4f" % (mu, std)
#     plt.title(title)
#     plt.savefig("MDNBR fit.png")
#     plt.close()

#     mu, std = norm.fit(peaking_list)
#     # Plot the histogram.
#     plt.hist(peaking_list, bins=25, density=True, alpha=0.6, color='g')
#     # Plot the PDF.
#     xmin, xmax = plt.xlim()
#     x = np.linspace(xmin, xmax, 100)
#     p = norm.pdf(x, mu, std)
#     plt.plot(x, p, 'k', linewidth=2)
#     title = "Fit results: Power peaking = %.4f,  std = %.4f" % (mu, std)
#     plt.title(title)
#     plt.savefig("Peaking fit.png")
#     plt.close()


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
#     n_iter=50
#     for i in tqdm(range(n_iter)):
#         l_x.append(x_guide_limit+0.001+i*(x_pins_limit-x_guide_limit-0.001)/n_iter)
#         F=func_diag(x_guide_limit+0.001+i*(x_pins_limit-x_guide_limit-0.001)/n_iter)

#     plt.errorbar(l_x,MDNBR_list,yerr=MDNBR_error,marker='x')
#     plt.xlabel("Position of pin 45")
#     plt.ylabel("MDNBR")
#     plt.title("MDNBR for different positions of pin 45")
#     plt.savefig("MDNBR for different positions of pin 45.png")
#     plt.close()

#     plt.errorbar(l_x,peaking_list,yerr=pp_error,marker='x')
#     plt.xlabel("Position of pin 45")
#     plt.ylabel("Power peaking")
#     plt.title("Power peaking for different positions of pin 45")
#     plt.savefig("Peaking for different positions of pin 45.png")    
#     plt.close()


# #Optimize 
# if m==45:
#     origin=[x_m_o]
#     y0=func_diag(x_m_o)
#     res=skopt.gbrt_minimize(func_diag,[(0,asm_pitch/2)],n_calls=100,n_initial_points=10,x0=origin,y0=[y0])
#     x_min=res.x
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
#     plt.title("MDNBR for different positions of pin 84")
#     plt.savefig("MDNBR for different positions of pin 84.png")
#     plt.close()

#     plt.plot(l_x_plot,peaking_plot,marker='x')
#     plt.xlabel("Iterations")
#     plt.ylabel("Power peaking")
#     plt.title("Power peaking for different position of pin 84")
#     plt.savefig("Peaking for different position of pin 84.png")    
#     plt.close()


# elif m==71 or m==68: #diagonal pins
#     origin=[x_m_o]
#     l_x=[x_m_o]
#     y0=func_diag(x_m_o)

#     res=skopt.gbrt_minimize(func_diag,[(0,asm_pitch/2)],n_calls=100,n_initial_points=10,x0=origin,y0=[y0])
#     print("\n Results")
#     print("x0 = ",x_m_o)
#     print("F at x0=",y0)
#     x_min=res.x
#     print("x_min =",x_min)
#     print("F at x_min =",res.fun)
#     #study the minimum
#     (peaking,MDNBR)=func_final((x_min,x_min))
#     print("power peaking = ", peaking)
#     print("MDNBR = ", MDNBR)

#     #plot positions taken by optimization
#     plt.plot(range(iter+1),l_x,marker='x')
#     plt.savefig("Positions.png")

# else: #non diagonal pins, curently allows 39 and 85
#     l_positions=[(x_m_o,y_m_o)]
#     origin=(x_m_o,y_m_o)
#     y0=func_basic(origin)

#     res=skopt.gbrt_minimize(func_basic,((0,asm_pitch/2),(0,asm_pitch/2)),n_calls=2000,n_initial_points=50,x0=origin,y0=y0)

#     print("\n Results")
#     print("x0 = ",origin)
#     print("F at x0=",y0)
#     pos_min=res.x
#     print("position min =",pos_min)
#     print("F at position min =",res.fun)
#     #study the minimum
#     (peaking,MDNBR)=func_final(pos_min)
#     print("power peaking = ", peaking)
#     print("MDNBR = ", MDNBR)
