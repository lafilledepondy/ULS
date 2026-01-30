# ======= READ DATA FILE =======
datafileName = './Instances_ULS/Toy_Instance.txt'

with open(datafileName, "r") as file:
    line = file.readline()  
    lineTab = line.split()    
    nbPeriodes = int(lineTab[0])
    
    line = file.readline()  
    lineTab = line.split()
    demandes = []
    for i in range(nbPeriodes):
        demandes.append(int(lineTab[i]))
        
    line = file.readline()  
    lineTab = line.split()
    couts = []
    for i in range(nbPeriodes):
        couts.append(int(lineTab[i]))

    line = file.readline()  
    lineTab = line.split()
    cfixes = []
    for i in range(nbPeriodes):
        cfixes.append(int(lineTab[i]))
    
    line = file.readline()  
    lineTab = line.split()    
    cstock = int(lineTab[0])

# ======= DONNÉES =======
#print(nbPeriodes)
#print(demandes)
#print(couts)
#print(cfixes)
#print(cstock)


# Import du paquet highspy et de toutes ses fonctionnalités
from typing_extensions import runtime
import highspy as hp
import time # pour le temps de résolution

# ======= MODEL =======
model = hp.Highs()
model.setOptionValue('time_limit', 60)
model.setOptionValue('mip_rel_gap', 1e-10)
model.setOptionValue('mip_abs_gap', 1)
model.setOptionValue('output_flag', True)

# ======= VARIABLES =======
# x_ij quantity produced in period i to satisfy demand in period j
x = model.addVariables(nbPeriodes, nbPeriodes, type=hp.HighsVarType.kInteger, lb=0, ub=1, name_prefix="x")
# x = model.addVariables(nbPeriodes, nbPeriodes, type=hp.HighsVarType.kContinuous, lb=0, ub=1, name_prefix="x")

# y_i binary: 0 or 1
y = model.addVariables(nbPeriodes, type=hp.HighsVarType.kInteger, lb=0, ub=1, name_prefix="y")
# y = model.addVariables(nbPeriodes, type=hp.HighsVarType.kContinuous, lb=0, ub=1, name_prefix="y")

# ======= OBJECTIVE =======
obj = 0
for i in range(nbPeriodes):
    # coût de setup
    obj += cfixes[i] * y[i]
    # coûts de production + stockage pour les demandes j >= i
    for j in range(i, nbPeriodes):
        unit_cost = couts[i] + cstock * (j - i)  # c_i + h (j-i)
        obj += unit_cost * demandes[j] * x[i, j]

model.setObjective(obj, sense=hp.ObjSense.kMinimize)

# ======= CONSTRAINTS =======
# 1. Affectation unique de la demande de chaque période : sum_i x_ij = 1
for j in range(nbPeriodes):
    expr = 0
    for i in range(j + 1):  # i <= j
        expr += x[i, j]
    model.addConstr(
        expr == 1, 
        name=f"unique_demand_assignment_{j}"
    )

# 2. Production only if setup : x_ij <= y_i
for i in range(nbPeriodes):
    for j in range(i, nbPeriodes): # i <= j
        model.addConstr(
            x[i, j] <= y[i], 
            name=f"setup_production_{i}_{j}"
        )

# ======= SOLVE =======
#model.write("test.lp")

start_time = time.time()
status = model.optimize()
end_time = time.time()
runtime = end_time - start_time

print("\n----------------------------------")
info = model.getInfo()
model_status = model.getModelStatus()
print('Status de la résolution par le solveur = ', model.modelStatusToString(model_status))
print("Valeur de la fonction objectif = ", model.getObjectiveValue())
print("Meilleure borne inférieure sur la valeur de la fonction objectif: ", info.mip_dual_bound)
print("Gap: ", info.mip_gap)
print("# de noeuds explorés: ", info.mip_node_count)
print("Temps de résolution (en secondes) = ", runtime)
print("----------------------------------")


# ====== PRINT SOLUTION =======
if model_status == hp.HighsModelStatus.kOptimal:
    solution = model.getSolution()
    all_col_values = solution.col_value
    
    # y variables are the first nbPeriodes
    y_values = all_col_values[0 : nbPeriodes]
    
    # x variables are the next nbPeriodes * nbPeriodes
    x_values = all_col_values[nbPeriodes : nbPeriodes + nbPeriodes * nbPeriodes]
    
    print("\n \t Solution trouvée:")
    print(f"| {'Mois':<5} | {'y_i (Setup)':<12} | ", end="")
    for j in range(nbPeriodes):
        print(f"j={j+1}".ljust(2), end=" | ")
    print()
    print("-" * (17 + (nbPeriodes * 7)))
    
    for i in range(nbPeriodes):
        print(f"| {i+1:<5} | {y_values[i]:<12.0f} | ", end="")
        for j in range(nbPeriodes):
            x_ij_value = x_values[i * nbPeriodes + j]
            print(f"{abs(x_ij_value)}", end=" | ")
        print()
elif model_status == hp.HighsModelStatus.kTimeLimit:
    print("\n \t Limite de temps atteinte : solution non affichée.")
else:
    print("\n \t Aucune solution réalisable trouvée.") 