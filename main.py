from helperFunctions import *
from modelisations import *
import pandas as pd

def main():
    print("Résolution des instances du problème ULS\n")
    
    ######## Modèle 1 #########
    # process_all_files_in_directory(
    #     directory_path='./Instances_ULS',
    #     solve_model=solve_model_1,
    #     tex_output_path='./model1_results.tex',
    #     caption_text="Résultats du modèle 1 pour les instances ULS",
    #     label_tab="tab:model1_results"
    # )

    ##### ADD for the best sol add the .0 

    ######### Modèle 2 #########
    process_all_files_in_directory(
        directory_path='./Instances_ULS',
        solve_model=solve_model_2,
        tex_output_path='./model2_results.tex',
        caption_text="Résultats du modèle 2 pour les instances ULS",
        label_tab="tab:model2_results"
    )

    ######### Test: instance spécifique #########

    # datafileName = './Instances_ULS/Instance60.1.txt'
    # nbPeriodes, demandes, couts, cfixes, cstock = read_data(datafileName)

    # model, model_status = solve_model_1(nbPeriodes, demandes, couts, cfixes, cstock)
    # printSolution_model1(model, nbPeriodes, model_status, demandes)

    # model, model_status = solve_model_2(nbPeriodes, demandes, couts, cfixes, cstock)
    # printSolution_model2(model, nbPeriodes, model_status, demandes)    

if __name__ == "__main__":
    main()    