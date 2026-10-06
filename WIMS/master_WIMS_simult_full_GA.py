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
import pygad

#With a genetic algorithm 

asm_pitch = 21.5
xmax=asm_pitch/2
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

def decode_solution(coords, moving_set, is_on_diagonal):
    """Convert flat gene array → (l_x, l_y) lists, one per moving pin."""
    l_x, l_y = [], []
    j = 0
    for m in moving_set:
        if is_on_diagonal(m):
            l_x.append(coords[j]);  l_y.append(coords[j]);  j += 1
        else:
            l_x.append(coords[j]);  l_y.append(coords[j+1]); j += 2
    return l_x, l_y

def is_valid(coords, moving_set, pins_original, gt_x, gt_y,
             r, r_g, xmax, is_on_diagonal):
    """
    Return True if this solution has no overlaps and all pins are in bounds.
    Mirrors the collision checks in fitness_func exactly.
    """
    l_x, l_y = decode_solution(coords, moving_set, is_on_diagonal)
    min_dist = 2*r + 0.2

    # 1. Bounds check — all moving pins inside octant
    for xi, yi in zip(l_x, l_y):
        if xi < 0 or yi < 0 or xi > xmax or yi > xmax:
            return False
        if yi > xi + 1e-6:          # outside upper triangle (y > x)
            return False

    # 2. Moving pins among themselves
    for i in range(len(moving_set)):
        for j in range(i+1, len(moving_set)):
            d = ((l_x[i]-l_x[j])**2 + (l_y[i]-l_y[j])**2)**0.5
            if d < min_dist:
                return False

    # 3. Moving pins vs fixed pins
    for xi, yi in zip(l_x, l_y):
        for p in pins_original:
            if p[0] == 0 and p[1] == 0:
                continue        # placeholder for a moving pin — skip
            d = ((xi-p[0])**2 + (yi-p[1])**2)**0.5
            if d < min_dist:
                return False

    # 4. Moving pins vs guide tubes
    for xi, yi in zip(l_x, l_y):
        for gx, gy in zip(gt_x, gt_y):
            d = ((xi-gx)**2 + (yi-gy)**2)**0.5
            if d < min_dist:
                return False

    return True


def fitness_func(ga_instance, solution, solution_idx):
#will be maximized 
    #lists of x and y for all pins moving 
    (l_x,l_y)=decode_solution(solution, moving_set, is_on_diagonal)

    #Test distances (pins among each other, all with other pins, all with guide tubes) and bounds 
    if not is_valid(solution, moving_set, pins_original, gt_x, gt_y,r, r_g, xmax, is_on_diagonal):
        F=-100
        return F

    pins=pins_original.copy()
    for i in range(len(moving_set)):
        pins[moving_set[i]]=(l_x[i],l_y[i],f)
    position_list.append(solution)
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
    F=-peaking

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
    #     F=-100 
    return F


#moving the pins
moving_set=[]
for i in range (5,22):
    if i%2==0:
        moving_set.append(i)
moving_set=moving_set+list(range(23,47))
pins_original=get_pins_1_8(p0,p2,f,npins)

pins_original=get_pins_1_8(p0,p2,f,npins)

# file_res = open('Optimized assembly simult.txt', mode ='w')

origin=[]
for m in moving_set:
    if is_on_diagonal(m):
        origin.append(pins_original[m][0])
    else:
        origin.append(pins_original[m][0])
        origin.append(pins_original[m][1])
for m in moving_set:
    pins_original[m]=(0,0,f) #we keep the spot open (and it won't cause overlapping)

#Genetic Algorithm
#MODIFY PARAMETERS ! 
num_generations = 100 # Number of generations.
num_parents_mating = 10 # Number of solutions to be selected as parents in the mating pool.

#sol_per_pop = 20 # Number of solutions in the population.
num_genes = len(origin)


def generate_initial_population(origin, moving_set, pins_original,
                                gt_x, gt_y, r, r_g, xmax,
                                is_on_diagonal,
                                pop_size=20,
                                delta_start=0.3,
                                max_attempts=5000):
    """
    Build an initial population by perturbing the known-valid `origin`.
    Each individual is generated by adding random noise ±delta to each gene of `origin`, then checking validity.  If acceptance rate is low, delta is automatically reduced.

    Parameters
    ----------
    origin      : list — the original (valid) pin positions as a flat gene array
    pop_size    : number of individuals to generate
    delta_start : initial perturbation magnitude (cm)
    max_attempts: maximum tries before giving up and returning what we have
    """
    population = [list(origin)]   # always include the original as individual 0
    origin_arr = np.array(origin, dtype=float)
    delta = delta_start
    attempts = 0

    while len(population) < pop_size and attempts < max_attempts:
        # Perturb: each gene gets independent noise in [-delta, +delta]
        noise = np.random.uniform(-delta, delta, size=len(origin_arr))
        candidate = list(origin_arr + noise)

        if is_valid(candidate, moving_set, pins_original, gt_x, gt_y, r, r_g, xmax, is_on_diagonal):
            population.append(candidate)
        else:
            attempts += 1
            # If struggling, reduce delta to increase acceptance rate
            if attempts % 500 == 0:
                delta *= 0.8
                print(f"  Reducing delta to {delta:.3f} cm after {attempts} attempts "
                      f"({len(population)}/{pop_size} individuals found)")

    if len(population) < pop_size:
        print(f"WARNING: only generated {len(population)}/{pop_size} valid individuals. "
              f"Duplicating existing ones to fill population.")
        while len(population) < pop_size:
            # Duplicate a random valid individual with tiny noise
            base = population[np.random.randint(len(population))]
            noise = np.random.uniform(-0.05, 0.05, size=len(base))
            population.append(list(np.array(base) + noise))

    print(f"Initial population: {len(population)} individuals, "
          f"final delta={delta:.3f} cm")
    return population

initial_pop=generate_initial_population(origin, moving_set, pins_original,gt_x, gt_y, r, r_g, xmax,is_on_diagonal,pop_size=100,delta_start=0.3)

# Gene space: each gene bounded to [0, xmax]
gene_space = []
for m in moving_set:
    if is_on_diagonal(m):
        gene_space.append({'low': 0.0, 'high': xmax})      # 1 gene
    else:
        gene_space.append({'low': 0.0, 'high': xmax})      # x gene
        gene_space.append({'low': 0.0, 'high': xmax})      # y gene


last_fitness = -200
def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]

ga_instance = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    num_genes=num_genes,
    fitness_func=fitness_func,
    initial_population=initial_pop,    # ← use our valid population
    gene_space=gene_space,             # ← bounds per gene
    mutation_type="random",
    mutation_percent_genes=20,         # mutate 20% of genes per offspring
    mutation_by_replacement=False,
    random_mutation_min_val=-0.5,      # mutation step ±0.5 cm
    random_mutation_max_val=+0.5,
    crossover_type="single_point",
    on_generation=on_generation,
)

# Running the GA to optimize the parameters of the function.
ga_instance.run()

ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution(ga_instance.last_generation_fitness)
print(f"Parameters of the best solution : {solution}")
print(f"Fitness value of the best solution = {solution_fitness}")
print(f"Index of the best solution : {solution_idx}")

if ga_instance.best_solution_generation != -1:
    print(f"Best fitness value reached after {ga_instance.best_solution_generation} generations.")

#HOW TO TAKE INTO ACCOUNT BOUNDS ? Add to objective function?
# bounds=[]
# for m in moving_set:
#     if is_on_diagonal(m):
#         bounds.append((0,asm_pitch/2))
#     else:
#         bounds.append((0,asm_pitch/2))
#         bounds.append((0,asm_pitch/2))

# file_res.write("Final optimized assembly \n")
# file_res.write(str(moving_set)+'\n')
# file_res.write(str(res))
# file_res.write("\n")
# file_res.write(str(res.x))
# file_res.close()

# plt.plot(range(iter),peaking_list,marker='x')
# plt.xlabel("iteration")
# plt.ylabel("Power peaking")
# plt.title("Power peaking for iterations simultaneous optimisation")
# plt.savefig("Peaking for iterations simult opti.png")
# plt.close()

# plt.plot(range(iter),MDNBR_list,marker='x')
# plt.xlabel("iteration")
# plt.ylabel("MDNBR")
# plt.title("MDNBR for iterations simultaneous optimisation")
# plt.savefig("MDNBR for iterations simult opti.png")
# plt.close()
