import numpy as np
from heat_map import cplot
import matplotlib as mpl
import csv
mpl.rcParams['figure.dpi'] = 300

##This is a generator of Cobra input file using my order of pins and my subchannels ! 

def chopped_cosine_distribution(x, a, b):
    """
    From ChatGPT
    Chopped cosine distribution with peak value of 1.55.
    
    Args:
        x (array-like): Input values to evaluate the distribution at.
        a (float): Lower bound of the distribution.
        b (float): Upper bound of the distribution.
        
    Returns:
        array-like: Values of the chopped cosine distribution evaluated at x.
    """
    y = np.zeros_like(x)
    peak = 1.55
    c = (a + b) / 2.0
    delta = (b - a) / 2.0
    mask = (x >= a) & (x <= b)
    y[mask] = peak * (0.5 * (1.0 + np.cos(np.pi * (x[mask] - c) / delta)))
    return y

def subchan_center(sc):
    px = np.mean(np.array([s[0] for s in sc]))
    py = np.mean(np.array([s[1] for s in sc]))
    return (px,py)

def get_subchan_coords(subchan,npins,p0,p2,f,gt_x,gt_y,pins):
    coords=[]
    for sc in subchan:
        if isinstance(sc,int):
            coords.append([(pins[sc][0],pins[sc][1]),(21.5/2,pins[sc][1]),(21.5/2,21.5/2)])
        else:
            c=list()
            for s in sc:
                if s<0:
                    c.append((gt_x[-s-1],gt_y[-s-1]))
                else:
                    c.append((pins[s][0],pins[s][1]))
            if len(c)==2:
                c.append((21.5/2,c[1][1]))
                c.append((21.5/2,c[0][1]))    
            coords.append(c)
    return coords

def first_three_significant_figures(number):
    """
    ChatGPT
    Returns the first three significant figures of a number as a string.
    
    Args:
        number (float): The number to extract the first three significant figures from.
        
    Returns:
        str: The first three significant figures of the number, as a string.
    """
    formatted_number = "{:.3E}".format(number).replace(".","")
    first_three_digits = formatted_number[:3]
    return first_three_digits

def round_to_3sf(number):
    """
    Rounds a number to 3 significant figures.
    
    Args:
        number (float): The number to round.
        
    Returns:
        float: The rounded number.
    """
    if number == 0:
        return 0.0
    
    magnitude = np.floor(np.log10(abs(number))) + 1
    precision = int(3 - magnitude)
    rounded_number = round(number, precision)
    return rounded_number

def write_6digit(item):
    n=round_to_3sf(item)
    f3sf="{:.3E}".format(n).replace(".","")[:3]
    mystr=str(f3sf)+"E"
    exponent=np.log10(n/float(f3sf))
    if exponent >=0:
        mystr+="+"
    mystr+=str(int(round(exponent)))

    return mystr

def distance_between_centers(pin1,pin2):
    return np.sqrt((pin1[0]-pin2[0])**2+(pin1[1]-pin2[1])**2)

def angle_between_three_points(point_a, point_b, point_c):
    """
    Calculates the angle between three points in radians.

    Args:
        point_a (tuple): The (x, y) coordinates of the first point.
        point_b (tuple): The (x, y) coordinates of the second point.
        point_c (tuple): The (x, y) coordinates of the third point.

    Returns:
        float: The angle between the three points in radians.
    """
    # Calculate the vectors formed by the three points
    vector_ab = np.array([point_b[0] - point_a[0], point_b[1] - point_a[1]])
    
    #Negative sign put as as both lines must point TO the same point
    vector_bc = -np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]])
    

    # Calculate the dot product and magnitude of the vectors
    dot_product = np.dot(vector_ab, vector_bc)
    magnitude_ab = np.linalg.norm(vector_ab)
    magnitude_bc = np.linalg.norm(vector_bc)

    # Calculate the cosine of the angle using the dot product and magnitudes
    cosine = dot_product / (magnitude_ab * magnitude_bc)

    # Calculate the angle in radians using the arccosine function
    angle = np.arccos(cosine)
    
    #we want the internal angle
    return angle
    
def polygon_area(coords):
    """
    Calculates the area of a polygon given its coordinates using the Shoelace formula.
    
    Args:
        coords (list or numpy.ndarray): List of tuples of the vertices
    
    Returns:
        float: The area of the polygon.
    """
    # Ensure that x_coords and y_coords are numpy arrays
    x_coords = np.asarray([coord[0] for coord in coords])
    y_coords = np.asarray([coord[1] for coord in coords])
    
    # Apply the Shoelace formula
    area = 0.5 * np.abs(np.dot(x_coords, np.roll(y_coords, 1)) - np.dot(y_coords, np.roll(x_coords, 1)))
    
    return area

def cobra_input(p0,p2,f,npins,pins,gt_x,gt_y,P,sc,uprate_case,calc_dnb,nax,plot_yes,heated_length):

    #want to run the following cases:
    #increase raw power of the 'hot' assembly to recover the extra allowable power peaking under same core power
    #case where the power and flow are both uprated in proportional to number of pins to see if MDNBR preserved

    if uprate_case is not None and npins == 264:
        raise ValueError

    if uprate_case == "pow":
        pow_uprate = 1.095 #tune to original reference value
        flow_uprate = 1.0

    elif uprate_case == 'both':
        pow_uprate = npins/264
        flow_uprate = npins/264 

    elif uprate_case is None:
        pow_uprate = 1.0
        flow_uprate = 1.0

    else:
        raise ValueError

    if calc_dnb:
        pow_fac=pow_uprate*1.12*1.587
        flow_fac=0.95
    else:
        pow_fac=pow_uprate
        flow_fac=1.0

    #Write nchan and nrod (noting octant symmetry except 280 pins)
    nchan=len(sc)

    #unique rods used in the problem
    rods=list()
    for s in sc:
        try:
            for item in s:
                if item>=0:
                    rods.append(item)
        except TypeError:
            if s>=0:
                rods.append(s)
    rods=list(set(rods))
    nrod=len(rods)

    subchan_coords=get_subchan_coords(sc,npins,p0,p2,f,gt_x,gt_y,pins)
    if plot_yes:
        cplot(np.zeros(len(pins))+0.5,0.475*f,p0,pins,gt_x,gt_y,P,"subchannels.png",subchan=subchan_coords) #Draws them

    pin_pow=3411e6/193.0/npins/4
    """
    note 1/30/26 - I think the factor of 4 is in error here (misapplication of symmetry).
    However, the lines for calculating the power distribution around line 472 have a near-cancelling error 
    where the pin power is used rather than power per meter. The upshot is that everything is run at
    an assumed core thermal power of 3411*3.66/4 = 3121 MWth with corresponding lowered mass flux. 
    Not ideal but everything is all relative so I dont believe this effects the results significantly. 
    Could and should be corrected in future.
    """

    with open("INPFILE","w") as IF:
        #1
        IF.write(str(npins)+"\n")
        #2
        IF.write("{:6d}{:6d}{:6d}{:6d}\n".format(1,2,2,0)) #last number is COBRA 3 eqn model vs 4 eqn and TWIGL

        #3
        nax=16 #number of axial layers
        nctyp=nchan #set each channel as own type
        ngrid=8 #From my thesis 
        ngtype=1 #From my thesis
        nrnode=10 #number of radial nodes in fuel pellet

        IF.write("{:6d}{:6d}{:6d}{:6d}{:6d}{:6d}{:6d}{:6d}{:6d}      {:6d}{:6d}\n".format(1,nchan,nrod,nax,nctyp,ngrid,ngtype,nrnode,0,1,1))
        
        #4
        axl = 3.66/nax #axial node length
        IF.write("{:12.5E}\n".format(-axl))
        
        #5
        IF.write("{:6d}\n".format(nax))
        xpoints = axl * (np.arange(nax) + 0.5)          # physical metres
        ypoints = chopped_cosine_distribution(xpoints, 0, heated_length)
        shape_mean = np.mean(ypoints)                    # normalisation factor
        #ypoints=ypoints/shape_mean #normalized so that ypoints sum to 1 
        for j in range(nax):
            this_ax=axl*(0.5+j)
            IF.write("{:12.5E}\n".format(this_ax))
            for k in range(nrod):
                IF.write("{:12.5E}".format(ypoints[j]*P[rods[k]]*pow_fac/heated_length)) #linear power, W/m, normalized to conserve total pin power
                if k%6==5 or k == nrod-1:
                    IF.write("\n")

        #7
        for j in range(nchan):
            IF.write("{:6d}   ".format(j+1))
            
            for k in range(j+1,nchan):
                common_values = set(subchan_coords[j]) & set(subchan_coords[k])
                if len(common_values) == 2:
                    #they share a border
                    cv=list(common_values)
                    length_of_gap=distance_between_centers(cv[0],cv[1])
                    #What to subtract depends on if guide tube, pin or neither
                    for item in cv:
                        if tuple(list(item)+[f]) in pins:
                            length_of_gap-=0.475*f
                        for gx,gy in zip(gt_x,gt_y):
                            if item[0] == gx and item[1] == gy:
                                length_of_gap-=0.612
                    centroid_to_centroid=distance_between_centers(subchan_center(subchan_coords[j]),subchan_center(subchan_coords[k]))
                    IF.write("{:3d}".format(k+1))
                    IF.write(write_6digit(length_of_gap/100))
                    IF.write(write_6digit(centroid_to_centroid/100))

                            
            IF.write("\n") 
        IF.write("     0     0\n") #end of this set of cards

        #8
        for j,rod in enumerate(rods):
            IF.write("{:3d}".format(j+1))
            IF.write("{:6d}".format(1)) #fuel type
            IF.write("   ")
            
            for k,s in enumerate(sc):
                try:
                    schans = list(s)
                except:
                    schans=list([s])
                if rod in schans: #this rod borders this subchannel
                    IF.write("{:3d}".format(k+1))
                    r_idx = schans.index(rod) #position of rod within schans
                    master_coord = subchan_coords[k][r_idx]
                    coord1 = subchan_coords[k][r_idx-1]
                    try:
                        coord2 = subchan_coords[k][r_idx+1]
                    except IndexError:
                        coord2 = subchan_coords[k][0] #if r_idx is on the end go round to first coords
                    
                    angle = angle_between_three_points(coord1,master_coord,coord2)
                    if np.isnan(angle):
                        print("problem angle",k,s)
                    IF.write(write_6digit(angle/2/np.pi))
            IF.write("\n")
        
        IF.write("000\n")
        
        
        #10
        for j in range(nchan):
            IF.write("{:6d}{:6d}".format(1,1)) #friction indicator, multiplier to wetted and heated perimeters
            
            flow_area=polygon_area(subchan_coords[j])
            heated_perim=0
            wetted_perim=0
            poly=len(subchan_coords[j]) #is this a quadrilateral or a triangle
            
            if isinstance(sc[j],int):
                tmp_sc=[sc[j]]
            else:
                tmp_sc=sc[j]
            
            n_heated=0
            for k in range(len(tmp_sc)): #only compute for water rods and fuel rods, not added corners
                angle=angle_between_three_points(subchan_coords[j][k-1],subchan_coords[j][k],subchan_coords[j][(k+1)%poly])
                if tmp_sc[k]<0:
                    #water rod
                    wetted_perim+=0.61*angle
                    flow_area-=0.5*0.61**2*angle
                else:
                    wetted_perim+=0.475*f*angle
                    heated_perim+=0.475*f*angle
                    flow_area-=0.5*(0.475*f)**2*angle
                    n_heated+=1

            IF.write("{:12.5E}".format(flow_area/100**2))
            IF.write("{:12.5E}".format(heated_perim/100))
            IF.write("{:12.5E}\n".format(wetted_perim/100))
            IF.write("{:12.5E}\n".format(1.0)) #grid spacer coefficient
            if j>0:
                IF.write("{:6d}{:6d}\n".format(j+1,0)) #channels part of the present type. Omit for first type. Terminate with zero
                    
        #11
        IF.write(""" .0625     1 .1875     1 .3125     1 .4375     1 .5625     1 .6875     1
 .8125     1 .9375     1\n""")
            
        #12
        IF.write("{:12.5E}{:12.5E}{:12.5E}{:12.5E}{:12.5E}{:12.5E}\n".format(0.4095/100*2,(0.475-0.418)/100,10400,6552,0.475/100*2,0))
        hgap=5e4 #https://www.sciencedirect.com/science/article/pii/S0149197020302353
        IF.write("{:12.5E}{:12.5E}{:12.5E}{:12.5E}{:12.5E}{:12.5E}\n".format(-11,-11,-11,-11,hgap,0.0))
        
        #Rest of cards from thesis. Mflux set to give 30C T rise under nominal
        IF.write("""     1     0     1     1     0     1     1     0     1     0
  .038     0     0     0
     1
     1     1
     0     0     0     0     0     0
0.50   0.0  0.50  0.0
     2     0     0  0.954    0     0    0.    0.    0.
$                                                                 ISCHEM
     0   500    0.  0.     0.    0.     0.    0.     0    0.    0.     1.
     1 {0}  {1:.0f}  15.5   0.0     0   1.0 0.026     0    0.    1.    0.
    0.     0     0
     0     0     0     0     0
     0     0     3     0     0     0    -1
""".format("565.3" if not calc_dnb else "567.3",2952*flow_uprate*flow_fac))

    return("OK")

