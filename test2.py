import os
import json

with open(f"templates/mutation_templates/1ycr_Repair_Model_EB17A.json","r") as file:

    residue_dict = json.load(file)
    residue_list = list(residue_dict)
    for seq in residue_list:
        if seq["bgn"]["auth_seq_id"] == 17 or seq["end"]["auth_seq_id"] == 17:
            print(seq)