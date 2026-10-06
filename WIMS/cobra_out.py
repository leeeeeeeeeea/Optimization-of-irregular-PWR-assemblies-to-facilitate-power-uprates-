import numpy as np
from heat_map import cplot
import matplotlib as mpl
import csv
mpl.rcParams['figure.dpi'] = 300
from cobra_smallopti import get_subchan_coords


def cobra_output(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes):
    nchan=len(sc)
    subchan_coords=get_subchan_coords(sc,npins,p0,p2,f,gt_x,gt_y,pins)
    #read the output file
    with open("OUTFILE","r") as OF:
        data=OF.readlines()

    T_out=[]
    for j,line in enumerate(data):
        if "AVERAGE PRESSURE DROP (Pa)" in line:
            P_drop_line=line
        
        if "CHANNEL EXIT SUMMARY RESULTS" in line:
            for k in range(j+13,j+13+nchan):
                T_out.append(float(data[k].split()[3])-293.15)
        
        if "MDNBR" in line:
            MDNBR=[]
            for k in range(j+3,j+3+nax):
                value = float(data[k].split()[2])
                if value > 0:
                    MDNBR.append(value)

    T_max=np.max(T_out)
    T_min=np.min(T_out)
    #print(T_max,T_min)

    T_out = np.array(T_out)
    T_out -= 300
    T_out /= 3.0

    if plot_yes:
        #create a new subchan plot which draws the temperature as heat map and then has white pins over the top
        cplot(T_out,0.475*f,p0,pins,gt_x,gt_y,P,"heat subchannels.png",subchan=subchan_coords,sc_out=True,colorbar=True,vbounds=[300,303])
    return (P_drop_line, min(MDNBR)) #fixing the MDNBR problem ??

