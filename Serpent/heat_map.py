import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300
import csv

def cplot(color_weights,r,p0,pins,gt_x,gt_y,P,name_fig,subchan=None,sc_out=False,vbounds=None,colorbar=False):
    cmap = plt.cm.get_cmap('jet')
    
    gt_rad = 0.61
    
    figure, axes = plt.subplots()
    axes.set_xlim(0,11)
    axes.set_ylim(0,11)
    axes.set_aspect(1)
    
       
    if not sc_out:
        for j,_ in enumerate(gt_x):
            axes.add_artist(plt.Circle((gt_x[j],gt_y[j]),gt_rad,color='grey'))
        
        for j,pin in enumerate(pins):
            axes.add_artist(plt.Circle((pin[0],pin[1]),r,color=cmap(color_weights[j])))
            if P is not None and not colorbar:
                if np.max(P)<5:
                    axes.annotate("{0:.2f}".format(P[j]),xy=(pin[0],pin[1]),fontsize=6)
                else: #pin numbering
                    axes.annotate("{0:.0f}".format(P[j]),xy=(pin[0],pin[1]),fontsize=10)
    
    if subchan is not None:
        if not sc_out:
            for i,sc in enumerate(subchan):
                px = np.mean(np.array([s[0] for s in sc]))
                py = np.mean(np.array([s[1] for s in sc]))
    
                #axes.annotate("{0:.0f}".format(i),xy=(px,py),fontsize=8)
                axes.add_artist(plt.Polygon(sc,fill=None,edgecolor='red'))
        else:
            for i,sc in enumerate(subchan):
                axes.add_artist(plt.Polygon(sc,color=cmap(color_weights[i])))
    if sc_out:
        for j,pin in enumerate(pins):
            axes.add_artist(plt.Circle((pin[0],pin[1]),r,color='white'))
        for j,_ in enumerate(gt_x):
            axes.add_artist(plt.Circle((gt_x[j],gt_y[j]),gt_rad,color='white'))
            
    if vbounds is None:
        vbounds=[np.min(P),np.max(P)]
    
    if colorbar:
        plt.colorbar(plt.cm.ScalarMappable(norm=Normalize(vmin=vbounds[0],vmax=vbounds[1]), cmap=cmap), ax=axes)
        
    # Hide X and Y axes label marks
    axes.xaxis.set_tick_params(labelbottom=False)
    axes.yaxis.set_tick_params(labelleft=False)
    
    # Hide X and Y axes tick marks
    axes.set_xticks([])
    axes.set_yticks([])
    plt.savefig(name_fig)
    plt.close()


#my work (Serpent), new giving pure pin power instead of normalizing
def calc_P(npins,pins,P_ass): 
    with open("BL324_1_8_det0.m") as fi:
        data=fi.readlines()
    #This is the neutron reaction rate tallies, not absolute powers in Watts.
    P=[]
    count=0 #pins in the quadrant (halves counted fully)
    total=0 #total pins per quadrant (halves counted as half)
    P_total=0 #keep track of the total P of the quadrant
    raw_rates = []  # store raw Serpent tallies first

    for line in data:
        if "1    1    1 " in line:
            p=float(line.split()[-2])
            raw_rates.append(p) 
            P.append(p)           
        #symmetry line pin (inside or bottom)
            if pins[count][0] == 0 or pins[count][1] == 0:
                P[-1] *= 2
                total += 0.5
        #Symmetry of the diagonal
            elif pins[count][0]==pins[count][1] :
                P[-1] *= 2
                total += 0.5
            else:
                total += 1
            count += 1
    # Normalise so that sum of all pin powers = total assembly power
    raw_sum = sum(raw_rates) #truly raw now 
    P = [p/ raw_sum * P_ass/8 for p in P]  #re normalizing for total assembly power. However here we did include doubling !
    P_total = np.sum([r/ raw_sum * P_ass/4 for r in raw_rates])
    return (P,P_total)

def heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,P_total,plot_yes):
    #To plot the power of the pins 
    #using fixed heat map limits
    #calculating power peaking 
    max=0
    sum=0
    count=0
    for i in range(len(P)):
        p=P[i]
        if p>max:
            max=p
        sum+=p 
        count+=1
    avg=sum/count
    #print("total power", P_total, "difference", 100*(P_total-17.7e6/4)/sum)

    if plot_yes:
        P_plot=[]
        for p in P:
            P_plot.append(p/avg)
        P_plot=np.array(P_plot)
        color_weights=(P_plot-0.75)/(1.2-0.75)
        r = 0.475*f 
        cplot(color_weights,r,p0,pins,gt_x,gt_y,P_plot,"heat map.png",colorbar=True)

    return (max/avg)




