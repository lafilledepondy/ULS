import os
import csv
import time
import highspy as hp

# ======= READ DATA FILE =======
def read_data(datafileName):
    """Reads data from a single instance file."""
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
    # ------ DONNÉES ------
    # print(f"Nombre de périodes (n) : {nbPeriodes}") 
    # print(f"Demande à satisfaire (d_i) : {demandes}")
    # print(f"Coûts de production (c_i) : {couts}")
    # print(f"Coûts fixes (f_i) : {cfixes}")
    # print(f"Coût de stockage (h) : {cstock}")        
    
    return nbPeriodes, demandes, couts, cfixes, cstock

# ====== PRINT SOLUTION =======
def printSolution_model1(model, nbPeriodes, model_status, demandes=None):
    """
    Print the solution 
    """
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


def printSolution_model2(model, nbPeriodes, model_status, demandes=None):
    """
    Print the solution 
    """
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

# ======= LOOP TO PROCESS ALL FILES =======
def process_all_files_in_directory(directory_path, solve_model, tex_output_path, caption_text, label_tab):
    """Processes all instance files in the specified directory and writes a LaTeX table report."""
    results = []
    
    # Boucle sur les fichiers d'instances
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".txt"):
            datafileName = os.path.join(directory_path, filename)
            print(f"\nPROCESSING FILE {datafileName}")
            nbPeriodes, demandes, couts, cfixes, cstock = read_data(datafileName)

            # --- SOLVE (PLNE) ---
            start_time = time.time()
            model, model_status = solve_model(nbPeriodes, demandes, couts, cfixes, cstock)
            end_time = time.time()
            runtime = end_time - start_time

            info = model.getInfo()
            obj_val = model.getObjectiveValue()
            # best_dual_bound = info.mip_dual_bound
            # gap = info.mip_gap
            node_count = info.mip_node_count
            status_str = model.modelStatusToString(model_status)

            # --- SOLVE (RL) ---
            model_rl, model_status_rl = solve_model(nbPeriodes, demandes, couts, cfixes, cstock, 
                                                     type_vars=hp.HighsVarType.kContinuous)
            rl_obj_val = model_rl.getObjectiveValue()

            gap = ((obj_val - rl_obj_val) / obj_val) * 100

            results.append({
                'filename': filename,
                'status': status_str,
                'obj_val': obj_val,
                'rl_obj_val': rl_obj_val,
                # 'best_dual_bound': best_dual_bound,
                'gap': gap,
                'node_count': node_count,
                'runtime': runtime
            })

    # Write results to LaTeX file
    with open(tex_output_path, mode="w") as texfile:
        texfile.write("\\begin{table}[H] \n")
        texfile.write("\\centering \n")
        texfile.write("\\begin{tabular}{l S[table-format=6.2] c S[table-format=6.2] S[table-format=1.2] r S[table-format=1.3]}\n")
        texfile.write("\\toprule \n")
        texfile.write("{Instance} & {RL} & {Status} & {Best Sol} & {Gap \\%} & {Noeuds} & {Temps (s)} \\\ \n")
        texfile.write("\\midrule \n")
        
        # Data rows
        prev_group = None
        for res in results:
            filename = res['filename']
            if filename.startswith('Instance') and filename.endswith('.txt'):
                formatted_filename = filename[8:-4]
            else:
                formatted_filename = filename.replace('.txt', '')

            filename_escaped = formatted_filename.replace('_', '\\_')

            # Group separator: dashed line when moving to a new prefix (e.g., 60.* -> 90.*)
            if '.' in formatted_filename:
                group_key = formatted_filename.split('.')[0]
            else:
                group_key = formatted_filename
            if prev_group is not None and group_key != prev_group:
                texfile.write("\\hdashline\n")
            prev_group = group_key

            # Format status: abbreviate "Time limit reached" to "TLR"
            status_display = 'Rélisable (TLR)' if res['status'] == 'Time limit reached' else res['status']

            texfile.write(f"{filename_escaped} & {res['rl_obj_val']:.1f} & {status_display} & {res['obj_val']:.1f} & "
                         f"{res['gap']:.2f} & {int(res['node_count'])} & {res['runtime']:.3f} \\\ \n")
        
        # Calculate averages
        avg_obj = sum(r['obj_val'] for r in results) / len(results) if results else 0
        avg_rl = sum(r['rl_obj_val'] for r in results) / len(results) if results else 0
        # avg_bound = sum(r['best_dual_bound'] for r in results) / len(results) if results else 0
        avg_gap = sum(r['gap'] for r in results) / len(results) if results else 0
        avg_nodes = sum(r['node_count'] for r in results) / len(results) if results else 0
        avg_runtime = sum(r['runtime'] for r in results) / len(results) if results else 0
        
        texfile.write("\\midrule \n")
        texfile.write(f"Average & {avg_rl:.2f} & {{}} & {avg_obj:.2f} & {avg_gap:.2f} & {avg_nodes:.2f} & {avg_runtime:.3f} \\\\ \n")
        texfile.write("\\bottomrule\n")
        texfile.write("\\end{tabular}\n")
        texfile.write(f"\\caption{{{caption_text}}}\n")
        texfile.write(f"\\label{{{label_tab}}}\n")
        texfile.write("\\end{table}\n\n")

    print(f"\nRésultats enregistrés dans le fichier LaTeX : {tex_output_path}")
