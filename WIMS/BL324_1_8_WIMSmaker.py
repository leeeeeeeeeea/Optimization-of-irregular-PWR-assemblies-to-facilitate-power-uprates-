import numpy as np
import math

def fmt(v, nd=6):
    return f"{v:.{nd}f}"

AZIMUTHAL_ANGLES = 32 
AZIMUTHAL_SEPARATION = 0.01
POLAR_ANGLES = 8
enrich = 4.8907  # wt% U235 — converted from Serpent's 4.95 at% U235

# Annuli per rod type — must match ROD_DEFS
N_ANNULI = {1: 3, 2: 2}   # fuel: pellet/gap/clad; GT: inner-coolant/clad
FISSILE_ANNULUS = 1        # 1-based index of fuel annulus within rodtype 1


def _on_symmetry(xc, yc):
    """True if the pin centre lies on y=0 or y=x (the two symmetry lines)."""
    return yc==0 or yc==xc

def _mesh_of_annulus(pin_index_in_sequence, annulus_1based, rod_type,
                     split_fuel, split_gt, insert_fuel, insert_gt):
    """
    Return the CACTUS interface mesh number for a given annulus of a given pin.

    CACTUS mesh ordering (DIAG/GEOMIN, background element first):
      mesh 1               : background element
      meshes 2 …           : SPLIT fuel pins    (N_ANNULI[1] meshes each)
      continuing …         : SPLIT guide tubes  (N_ANNULI[2] meshes each)
      continuing …         : INSERT fuel pins   (N_ANNULI[1] meshes each)
      continuing …         : INSERT guide tubes (N_ANNULI[2] meshes each)

    pin_index_in_sequence  : 0-based position of this pin within its group (group ex : split fuel pins)
    annulus_1based         : 1-based annulus index (1 = innermost)
    rod_type               : 1 (fuel) or 2 (guide tube)
    split_fuel / split_gt / insert_fuel / insert_gt : lengths of each group
    """
    # Starting mesh of each block (1-based, after the background mesh at 1)
    start_split_fuel   = 2
    start_split_gt     = start_split_fuel  + split_fuel  * N_ANNULI[1]
    start_insert_fuel  = start_split_gt    + split_gt    * N_ANNULI[2]
    start_insert_gt    = start_insert_fuel + insert_fuel * N_ANNULI[1]

    # Which block does this pin belong to?  Determined by call context,
    # not computed here — the caller passes the right index and block sizes.
    # We receive the absolute 0-based index within the whole sequence:
    #   split_fuel:   index 0 .. split_fuel-1
    #   split_gt:     index split_fuel .. split_fuel+split_gt-1
    #   insert_fuel:  index split_fuel+split_gt .. +insert_fuel-1
    #   insert_gt:    last block
    n_sf = split_fuel
    n_sg = split_gt
    n_if = insert_fuel

    if rod_type == 1 and pin_index_in_sequence < n_sf:
        # split fuel
        base = start_split_fuel + pin_index_in_sequence * N_ANNULI[1]
    elif rod_type == 2 and pin_index_in_sequence < n_sg:
        # split guide tube
        base = start_split_gt   + pin_index_in_sequence * N_ANNULI[2]
    elif rod_type == 1:
        # insert fuel  (index offset by split_fuel count)
        idx = pin_index_in_sequence - n_sf
        base = start_insert_fuel + idx * N_ANNULI[1]
    else:
        # insert guide tube (index offset by split_gt count)
        idx = pin_index_in_sequence - n_sg
        base = start_insert_gt   + idx * N_ANNULI[2]

    return base + (annulus_1based - 1)

def build_powermap_triplets(x, y, x_g, y_g):
    #recreate order of pins as given to CACTUS
    sf_xy = [(x[i], y[i])     for i in range(len(x))   if     _on_symmetry(x[i],   y[i])]
    sg_xy = [(x_g[i], y_g[i]) for i in range(len(x_g)) if     _on_symmetry(x_g[i], y_g[i])]
    if_xy = [(x[i], y[i])     for i in range(len(x))   if not _on_symmetry(x[i],   y[i])]
    ig_xy = [(x_g[i], y_g[i]) for i in range(len(x_g)) if not _on_symmetry(x_g[i], y_g[i])]

    n_sf = len(sf_xy)
    n_sg = len(sg_xy)
    n_if = len(if_xy)
    n_ig = len(ig_xy)

    # Use ALL pins for both axes — must match what was written to the WIMS input
    all_xy = sf_xy + sg_xy + if_xy + ig_xy
    #ordering pins based on actual physical positions (???)
    xs_sorted = sorted(set(round(p[0], 2) for p in all_xy))  #  all pins, not fuel-only
    ys_sorted = sorted(set(round(p[1], 2) for p in all_xy))

    x_to_ix = {v: i + 1 for i, v in enumerate(xs_sorted)} #gets the number of the pin in the ordered list 
    y_to_iy = {v: i + 1 for i, v in enumerate(ys_sorted)}

    triplets = []
    #only for fuel pins
    for seq_idx, (xc, yc) in enumerate(sf_xy):
        mesh = _mesh_of_annulus(seq_idx, FISSILE_ANNULUS, 1, n_sf, n_sg, n_if, n_ig)
        triplets.append((x_to_ix[round(xc, 2)], y_to_iy[round(yc, 2)], mesh))
    for seq_idx, (xc, yc) in enumerate(if_xy):
        mesh = _mesh_of_annulus(seq_idx + n_sf, FISSILE_ANNULUS, 1, n_sf, n_sg, n_if, n_ig)
        triplets.append((x_to_ix[round(xc, 2)], y_to_iy[round(yc, 2)], mesh))

    ix_max = max(t[0] for t in triplets) if triplets else 1
    iy_max = max(t[1] for t in triplets) if triplets else 1
    return triplets, ix_max, iy_max

def UO2_composition(enrich, pellet_density=10.295):
    """
    Given enrichment in wt% U235 (of uranium) and pellet density (g/cm³),
    return (wt_U235, wt_U238, wt_O, density) for use in MATE_DEFS and HEAD.
    
    Default density = 10.295 g/cm³ matches Serpent's 'mat fuel -10.295'.
    Theoretical UO2 density = 10.96 g/cm³; typical fabricated pellet = 10.3-10.5.
    """
    M_U235 = 235.044
    M_U238 = 238.051
    M_O    = 15.9994

    wf_U235 = enrich / 100
    wf_U238 = 1 - wf_U235

    # atom fractions in uranium
    at_U235 = (wf_U235/M_U235) / (wf_U235/M_U235 + wf_U238/M_U238)
    at_U238 = 1 - at_U235

    # molar mass of UO2
    M_UO2 = at_U235*M_U235 + at_U238*M_U238 + 2*M_O

    wt_U235 = at_U235 * M_U235 / M_UO2 * 100
    wt_U238 = at_U238 * M_U238 / M_UO2 * 100
    wt_O    = 2 * M_O  / M_UO2 * 100

    return wt_U235, wt_U238, wt_O, pellet_density

def WIMS_input(p0,p2,pins,x_g,y_g,asm_pitch,P_ass,npins) :

    ##x and y positions just like in the output
    x=[]
    y=[]
    for p in pins:
        x.append(p[0])
        y.append(p[1])

    #Now we want to add them to the BL324_1_8 input file
    f = open('input','w')
    f.write('SETVAL temp = 293.0 \n')
    f.write('SETVAL xmax = '+str(asm_pitch/2)+' \n')

    wt_U235, wt_U238, wt_O, fuel_density = UO2_composition(enrich)

    MATE_DEFS = [
        (1, fuel_density, [("U235", wt_U235), ("U238", wt_U238), ("O", wt_O)]),
        (2, 6.511,        [("Zr", 100.0)]),
        (3, 0.757,        [("H", 11.19), ("O", 88.81)]),
        (4, 0.00328,      [("He4", 100.0)]),
    ]
    #the gap will be created later from reusing the H2O cross sections

    ROD_DEFS = {
        1: [
            (0.3696, 1),  # fuel
            (0.3773, 4),  # gap
            (0.4287, 2),  # clad (mat 2)
        ],
        2: [
            (0.56, 3),    # inner coolant (mat 6 — NOT mat 3)
            (0.61, 2),    # clad (mat 5 — NOT mat 2)
        ],
    }
    PIP_ROD_DEFS = { #we fake a new type of fuel rod 
        1: [
            (0.3773, 1),  # fuel + gap homogenised into fuel region for PIP stability
            (0.4287, 2),  # clad
            (0.0,    3),  # coolant
        ],
    }

    # HEAD/PERSEUS build the collision-probability cell used by PIP. Only fuel pins ! In p2 size cell
    def write_head_perseus_geometry(lines):
        #Here I only have 1 type of pin (the fuel)
        lines.append(f"    xgrid 1  {fmt(p2)}  \n")
        lines.append(f"    ygrid 1  {fmt(p2)}  \n")
        lines.append("    map 1001  1 1  1 1\n")
        for j, (radius, matno) in enumerate(PIP_ROD_DEFS[1], start=1):
            lines.append(f"    rodsub 1 {j}  {fmt(radius)}  {matno} \n")
    
    #WRITING
    lines=[]
    lines.append("HEAD 1 \n")
    lines.append(f"  uranium u235 {enrich} \n")
    lines.append(f"material 1 density {fuel_density} temp $temp class   1 \n")
    lines.append(f"u235 {wt_U235:.6f} \n")
    lines.append(f"u238 {wt_U238:.6f} \n")
    lines.append(f"o    {wt_O:.6f} \n")
    lines.append("material 2 density 6.44 temp $temp class   2 \n")
    lines.append("zr 97.91 sn 1.59 fe 0.5 \n")
    lines.append("material 3 density 0.757 temp $temp class   3 \n")
    lines.append("h 11.19 o 88.81  \n")
    write_head_perseus_geometry(lines)
    lines.append("    begin \n")
    lines.append(" \n")
    f.writelines(lines)

    lines=[]
    lines.append("PERSEUS 1 \n")
    write_head_perseus_geometry(lines)
    lines.append("    square \n")
    lines.append("    begin \n")
    lines.append(" \n")
 
    lines.append("PIP 1 \n")
    lines.append("    niter 10 \n")
    lines.append("    begin \n")
    lines.append(" \n")
 
    lines.append("COND 1 2 \n")
    lines.append("    partition 22 45 92 135 152 172 \n")
    lines.append("    cond 1 1 material 1 \n")  # output mat 1 = input mat 1 (fuel),   spectrum from fuel meshes
    lines.append("    cond 2 2 material 2 \n")  # output mat 2 = input mat 2 (clad),   spectrum from clad meshes
    lines.append("    cond 3 3 material 3 \n")  # output mat 3 = input mat 3 (coolant), spectrum from coolant meshes
    lines.append("    cond 4 3 material 3 \n")  # create gap mat from coolant XS
    lines.append("    begin \n")
    lines.append(" \n")
    f.writelines(lines)

    #CACTUS (the geometry)
    f.write('CACTUS 2  * reads condensed 6-group XS from interface 2 (written by COND) \n')
    #making the 1/8th assembly shape
    f.write('  geomin \n')
    f.write('  DIAG \n')
    f.write('  dimension   $xmax  $xmax \n')
    f.write('  nodes \n')
    f.write('         0.0     0.0 \n')
    f.write('         $xmax    0.0\n')
    f.write('         $xmax    $xmax\n')
    f.write('    edges \n')
    f.write('1  2 \n')
    f.write('2  3 \n')
    f.write('3  1 \n')
    f.write('    elements \n')
    f.write('1  2  3 \n')
    f.write('\n')

#writing down our pins
    fuel_radii = "  0.369600  0.377300  0.428700"
    gt_radii   = " 0.560000  0.610000"

    lines_mat=[]
    #Split pins first (the ones on the symmetry lines)
    f.write('split \n')
    for i in range(len(x)):
        if x[i] == y[i] or y[i] == 0:
            f.write(f"        0   {fmt(x[i])}   {fmt(y[i])}   {fuel_radii}\n")
            mats = " ".join(str(m) for _r, m in ROD_DEFS[1])
            lines_mat.append(f"        {mats} \n") 
    for i in range(len(x_g)):
        if x_g[i] == y_g[i] or y_g[i] == 0:
            f.write(f"        0   {fmt(x_g[i])}   {fmt(y_g[i])}   {gt_radii}\n")
            mats = " ".join(str(m) for _r, m in ROD_DEFS[2])
            lines_mat.append(f"        {mats} \n")

    #full pins now 
    f.write('inserts \n')
    for i in range(len(x)):
        if not (x[i] == y[i] or y[i] == 0):
            f.write(f"        0   {fmt(x[i])}   {fmt(y[i])}   {fuel_radii}\n")
            mats = " ".join(str(m) for _r, m in ROD_DEFS[1])
            lines_mat.append(f"        {mats} \n")  
    for i in range(len(x_g)):
        if not (x_g[i] == y_g[i] or y_g[i] == 0):
            f.write(f"        0   {fmt(x_g[i])}   {fmt(y_g[i])}   {gt_radii}\n")            
            mats = " ".join(str(m) for _r, m in ROD_DEFS[2])
            lines_mat.append(f"        {mats} \n")

    # MATERIAL list: background element, then SPLIT pins in order,
    # then INSERTS pins in order -- each pin contributes one material number per annulus, in the order declared in ROD_DEFS.
    f.write("    material \n")
    f.write(f"        3   * background/element material \n")
    f.writelines(lines_mat)
    lines=[]
    lines.append("")

    lines.append("    picture \n")
    lines.append("    endgeom \n")
    lines.append(f"    azimuthal {AZIMUTHAL_ANGLES} {AZIMUTHAL_SEPARATION} 2 2 \n"
                 "   * kh=2 kv=2 -> reflective, required for diagonal symmetry \n")
    lines.append(f"    polar {POLAR_ANGLES} \n")
    lines.append("    begin \n")
    lines.append(" \n")
    f.writelines(lines)
 
    #normalizes power 
    lines=[]
    lines.append(f"POWER 2 \n")
    lines.append(f"    POWER {P_ass:.6e}   * 1/8th assembly power (W) \n")
    lines.append("    FISSION          * deposit all energy at point of fission \n")
    #lines.append("    MESH_OUTPUT      * print per-mesh power densities \n")
    lines.append("    BEGIN \n")
    lines.append("")

    #To get pin powers
    lines.append("EDIT 2 \n")
    lines.append(f"    NORM  {P_ass:.6e}  POWER   * normalise to 1/8th assembly power (W) \n")
    lines.append("    POWERMAP \n")
    lines.append("    TOFILE powermap.txt \n")

    triplets, ix_max, iy_max = build_powermap_triplets(x, y, x_g, y_g)
    # Emit triplets: ix  iy  mesh_number, 4 per line for readability
    triplet_strs = [f"{ix} {iy} {mn} \n" for ix, iy, mn in triplets]
    for i in range(0, len(triplet_strs), 4):
        lines.append("        " + "   ".join(triplet_strs[i:i+4]))
    lines.append("    BEGIN \n")
    lines.append(" \n")

    lines.append("STOP")
    f.writelines(lines)
    f.close()
    return "WIMS input generated"
