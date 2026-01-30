from typing_extensions import runtime
import highspy as hp
import time # pour le temps de résolution

# ======= MODEL 1 =======
def solve_model_1(nbPeriodes, demandes, 
                  couts, cfixes, cstock, 
                  output_flag=True, 
                  type_vars=hp.HighsVarType.kInteger):
    """Builds and solves Model 1, returning the required metrics."""
    
    model = hp.Highs()
    model.setOptionValue('time_limit', 180)
    model.setOptionValue('mip_rel_gap', 1e-10)
    model.setOptionValue('mip_abs_gap', 1)
    model.setOptionValue('output_flag', True)

    # ------ VARIABLES ------
    # y_i binary: 0 or 1
    y = model.addVariables(nbPeriodes, type=type_vars, lb=0, ub=1, name_prefix="y")

    # x_i quantity produced in period i
    x = model.addVariables(nbPeriodes, type=type_vars, lb=0, name_prefix="x")

    # s_i stock in period at the end of i
    s = model.addVariables(nbPeriodes, type=type_vars, lb=0, name_prefix="s")

    # ------ OBJECTIVE ------
    model.setObjective(
        sum(cfixes[i] * y[i] for i in range(nbPeriodes)) +
        sum(couts[i] * x[i] for i in range(nbPeriodes)) +
        sum(cstock * s[i] for i in range(nbPeriodes)),
        sense=hp.ObjSense.kMinimize
    )

    # --- CONSTRAINTS ---
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

    # --- SOLVE ---
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
    
    return model, model_status

# ======= MODEL 2 =======
def solve_model_2(nbPeriodes, demandes, 
                  couts, cfixes, cstock, 
                  output_flag=True, 
                  type_vars=hp.HighsVarType.kInteger):
    """Builds and solves Model 1, returning the required metrics."""
    
    model = hp.Highs()
    model.setOptionValue('time_limit', 180)
    model.setOptionValue('mip_rel_gap', 1e-10)
    model.setOptionValue('mip_abs_gap', 1)
    model.setOptionValue('output_flag', True)

    # ------ VARIABLES ------
    # x_ij binary: 0 or 1
    x = model.addVariables(nbPeriodes, nbPeriodes, type=type_vars, lb=0, ub=1, name_prefix="x")

    # y_i binary: 0 or 1
    y = model.addVariables(nbPeriodes, type=type_vars, lb=0, ub=1, name_prefix="y")

    # ------ OBJECTIVE ------
    obj = 0
    for i in range(nbPeriodes):
        # coût de setup
        obj += cfixes[i] * y[i]
        # coûts de production + stockage pour les demandes j >= i
        for j in range(i, nbPeriodes):
            unit_cost = couts[i] + cstock * (j - i)  # c_i + h (j-i)
            obj += unit_cost * demandes[j] * x[i, j]

    model.setObjective(obj, sense=hp.ObjSense.kMinimize)

    # --- CONSTRAINTS ---
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

    # --- SOLVE ---
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
    
    return model, model_status

