import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib as mpl
from BL324_1_8_WIMSmaker import build_powermap_triplets, _on_symmetry
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

# def calc_P(pins, x_g, y_g):
#     ##x and y positions just like in the output
#     x=[]
#     y=[]
#     for p in pins:
#         x.append(p[0])
#         y.append(p[1])

#     # Order pins in the order of WIMS : the order of pins but with the split pins before the others. Only fuel !  
#     sf_xy = [(x[i], y[i])     for i in range(len(x))   if     x[i]==y[i] or y[i]==0]
#     if_xy = [(x[i], y[i])     for i in range(len(x))   if not (x[i]==y[i] or y[i]==0)]
 
#     all_xy = sf_xy + sg_xy + if_xy + ig_xy #This is the order of the pins in WIMS
 
#     # xs_sorted = sorted(set(round(p[0], 2) for p in all_xy))
#     # ys_sorted = sorted(set(round(p[1], 2) for p in all_xy))
 
#     # ix_max = len(xs_sorted)
#     # iy_max = len(ys_sorted)
 
#     # # reverse maps: integer grid index -> real coordinate
#     # ix_to_x = {i + 1: v for i, v in enumerate(xs_sorted)}
#     # iy_to_y = {i + 1: v for i, v in enumerate(ys_sorted)}
 
#     # ------------------------------------------------------------------
#     # 2. Read the flat array from the file.
#     # ------------------------------------------------------------------
#     values = []
#     with open("powermap.txt") as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith('*'):
#                 continue
#             for tok in line.split():
#                 values.append(float(tok))
#     print("values",values)
#     # ------------------------------------------------------------------
#     # 3. Index into the flat array.
#     #    Storage order: ix varies fastest (Fortran column-major).
#     #    flat index for (ix, iy) = (ix-1) + (iy-1)*ix_max
#     # ------------------------------------------------------------------
#     pin_powers = []
#     #for i in range(len(values))
#     return pin_powers

def calc_P(pins, x_g, y_g, P_ass, powermap_path="powermap.txt"):
    x = [p[0] for p in pins]
    y = [p[1] for p in pins]

    values = []
    with open(powermap_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('*'):
                values.extend(float(v) for v in line.split())

    sf_xy = [(x[i], y[i])     for i in range(len(x))   if     _on_symmetry(x[i],   y[i])]
    sg_xy = [(x_g[i], y_g[i]) for i in range(len(x_g)) if     _on_symmetry(x_g[i], y_g[i])]
    if_xy = [(x[i], y[i])     for i in range(len(x))   if not _on_symmetry(x[i],   y[i])]
    ig_xy = [(x_g[i], y_g[i]) for i in range(len(x_g)) if not _on_symmetry(x_g[i], y_g[i])]

    all_xy  = sf_xy + sg_xy + if_xy + ig_xy
    ys_sorted = sorted(set(round(p[1], 2) for p in all_xy))
    iy_max = len(ys_sorted)
    N = len(values) // iy_max

    triplets, _, _ = build_powermap_triplets(x, y, x_g, y_g)
    n_sf = len(sf_xy)

    # Read all pins that fit in the file
    power_dict = {}
    overflow_keys = []

    for k, (ix, iy, _mesh) in enumerate(triplets):
        xc, yc = sf_xy[k] if k < n_sf else if_xy[k - n_sf]
        key = (round(xc, 4), round(yc, 4))
        flat_idx = (ix - 1) + (iy - 1) * N

        if flat_idx >= len(values):
            # Structural overflow: (ix_max, iy_max) is always one past the end.
            # Defer: will be filled by conservation below.
            overflow_keys.append(key)
        else:
            power_dict[key] = values[flat_idx]

    # Recover overflowed pin(s) by power conservation:
    # WIMS NORM guarantees sum of all pin powers = P_ass exactly.
    if overflow_keys:
        p_known = sum(power_dict.values())
        p_overflow = (P_ass - p_known) / len(overflow_keys)
        for key in overflow_keys:
            power_dict[key] = p_overflow

    # ── Double boundary pin powers ──────────────────────────────
    # Pins on y=0 or y=x are modelled as half-pins in CACTUS.
    # NORM scales by volume, so their reported power is half the true
    # full-pin value. Multiply by 2, exactly as in Serpent calc_P.
    for k, (ix, iy, _mesh) in enumerate(triplets):
        xc, yc = sf_xy[k] if k < n_sf else if_xy[k - n_sf]
        key = (round(xc, 4), round(yc, 4))
        if _on_symmetry(xc, yc) and key in power_dict:
            power_dict[key] *= 2
    # ─────────────────────────────────────────────────────────────────

    # Build output list in pins order
    P = []
    P_total = 0.0
    for p in pins:
        key = (round(p[0], 4), round(p[1], 4))
        pw = power_dict.get(key, 0.0)
        P.append(pw)
        P_total += pw
    #print(P)
    return P, P_total

def heat_map(p0,p2,f,npins,pins,gt_x,gt_y,P,P_total,plot_yes):
    #To plot the power of the pins 
    #using fixed heat map limits
    #calculating power peaking 
    max=0
    sum=0
    count=0
    min=1000000
    for i in range(len(P)):
        p=P[i]
        if p>max:
            max=p
        if p<min:
            min=p
        sum+=p 
        count+=1
    avg=sum/count
    #print("total power", P_total, "difference", 100*(P_total-17.7e6/4)/sum)
    if plot_yes:
        P_plot=[]
        for p in P:
            P_plot.append(p/avg)
        P_plot=np.array(P_plot)
        
        color_weights=(P_plot-(min/avg-0.025))/((max/avg+0.025)-(min/avg-0.025))
        #color_weights=(P_plot-(min/avg))/((max/avg)-(min/avg))
        r = 0.475*f 
        cplot(color_weights,r,p0,pins,gt_x,gt_y,P_plot,"heat map.png",colorbar=True)

    return (max/avg)




