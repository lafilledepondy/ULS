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
# print(f"Nombre de périodes (n) : {nbPeriodes}") 
# print(f"Demande à satisfaire (d_i) : {demandes}")
# print(f"Coûts de production (c_i) : {couts}")
# print(f"Coûts fixes (f_i) : {cfixes}")
# print(f"Coût de stockage (h) : {cstock}")


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
# y_i binary: 0 or 1
y = model.addVariables(nbPeriodes, type=hp.HighsVarType.kInteger, lb=0, ub=1, name_prefix="y")
# y = model.addVariables(nbPeriodes, type=hp.HighsVarType.kContinuous, lb=0, ub=1, name_prefix="y")

# x_i quantity produced in period i
x = model.addVariables(nbPeriodes, type=hp.HighsVarType.kInteger, lb=0, name_prefix="x")
# x = model.addVariables(nbPeriodes, type=hp.HighsVarType.kContinuous, lb=0, name_prefix="x")

# s_i stock in period at the end of i
s = model.addVariables(nbPeriodes, type=hp.HighsVarType.kInteger, lb=0, name_prefix="s")
# s = model.addVariables(nbPeriodes, type=hp.HighsVarType.kContinuous, lb=0, name_prefix="s")

# ======= OBJECTIVE =======
model.setObjective(
    sum(cfixes[i] * y[i] for i in range(nbPeriodes)) +
    sum(couts[i] * x[i] for i in range(nbPeriodes)) +
    sum(cstock * s[i] for i in range(nbPeriodes)),
    sense=hp.ObjSense.kMinimize
)

# ======= CONSTRAINTS =======
# 1. Demand satisfaction and stock balance
for i in range(nbPeriodes):
    if i == 0:
        model.addConstr(
            s[i] == x[i] - demandes[i], 
            name=f"demand_balance_{i}"
        )
    else:
        model.addConstr(
            s[i] == x[i] + s[i-1] - demandes[i], 
            name=f"demand_balance_{i}"
        ) 

# 2. Production only if setup
M = sum(demandes)  # Big M

for i in range(nbPeriodes):
    model.addConstr(
        x[i] <= M * y[i], 
        name=f"setup_production_{i}"
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

    # x variables are the next nbPeriodes (from index nbPeriodes to 2*nbPeriodes - 1)
    x_values = all_col_values[nbPeriodes : 2 * nbPeriodes]

    # s variables are the last nbPeriodes (from index 2*nbPeriodes to 3*nbPeriodes - 1)
    s_values = all_col_values[2 * nbPeriodes : 3 * nbPeriodes]

    print("\n \t Solution trouvée:")
    print(f"| {'Mois':<5} | {'y_i (Setup)':<12} | {'x_i (Prod.)':<12} | {'s_i (Stock)':<12} |")
    print("-" * 51)

    for i in range(nbPeriodes):
        print(f"| {i+1:<5} | {y_values[i]:<12.0f} | {x_values[i]:<12.2f} | {s_values[i]:<12.2f} |")
elif model_status == hp.HighsModelStatus.kTimeLimit:
    print("\n \t Limite de temps atteinte : solution non affichée.")
else:
    print("\n \t Aucune solution réalisable trouvée.")

