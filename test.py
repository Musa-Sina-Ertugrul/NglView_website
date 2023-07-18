from flask import Flask, render_template, request, redirect, url_for, session
import nglview
import os
import subprocess
import asyncio
import threading
import time
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"

@app.route("/", methods=["GET","POST"])
async def index():
    file_path_left = ""
    if "file" in request.files:
        file = request.files["file"]
        file.save(f"uploads/{file.filename}")
        if ".pdb" in file.filename:
            view_pdb = nglview.show_structure_file(f"uploads/{file.filename}")
            view_pdb.background = "black"
            file_path_left=f"templates/mutation_templates/{file.filename[:-4]}.html"

            session["file_path"] = f"{file.filename[:-4]}.html"
            """view_pdb_right = nglview.show_structure_file(f"uploads/{file.filename}")
            file_path_right=f"templates/mutation_no/{file.filename[:-4]}.html"
            nglview.write_html(file_path_right,[view_pdb_right])"""
            await run_maxit(file)
            is_File_generated = True
            while(is_File_generated):
                try:
                    with open(f"uploads/{file.filename[:-4]}.cif","r") as tmp:
                        pass
                    is_File_generated = False
                except:
                    continue
            await run_json(file)
            residue_dict = {}
            residue_list = []
            cleared_list = []
            select_numbers = set([])
            numbers_list = []
            is_File_generated = True
            while(is_File_generated):
                try:
                    with open(f"templates/mutation_templates/{file.filename[:-4]}.json","r") as tmp:
                        pass
                    is_File_generated = False
                except:
                    continue
            
            with open(f"templates/mutation_templates/{file.filename[:-4]}.json","r") as json_file:
                residue_dict = json.load(json_file)
                residue_list = list(residue_dict)
                seq_ids = set([])
                for seq in residue_list:
                    if seq["bgn"]["auth_seq_id"] == 17 or seq["end"]["auth_seq_id"] == 17:
                        cleared_list.append(seq)
                        select_numbers.add((seq["bgn"]["auth_seq_id"],seq["bgn"]["label_comp_id"]))
                        select_numbers.add((seq["end"]["auth_seq_id"],seq["end"]["label_comp_id"]))
                        if 'C' not in seq['bgn']['auth_atom_id'] and 'C' not in seq['end']['auth_atom_id']:
                            view_pdb.add_representation("distance",atomPair=[[f"{seq['bgn']['auth_seq_id']}.{seq['bgn']['auth_atom_id']}"
                                                                          ,f"{seq['end']['auth_seq_id']}.{seq['end']['auth_atom_id']}"]])
                            seq_ids.add((seq['bgn']['auth_seq_id'],seq['end']['auth_seq_id']))
                            seq_ids.add((seq['end']['auth_seq_id'],seq['bgn']['auth_seq_id']))
                            continue

                        """if (seq['bgn']['auth_seq_id'],seq['end']['auth_seq_id']) not in seq_ids and (
                            seq['end']['auth_seq_id'],seq['bgn']['auth_seq_id']) not in seq_ids:
                            view_pdb.add_representation("distance",atomPair=[[f"{seq['bgn']['auth_seq_id']}.{seq['bgn']['auth_atom_id']}"
                                                                          ,f"{seq['end']['auth_seq_id']}.{seq['end']['auth_atom_id']}"]])"""
                        
                numbers_list = list(select_numbers)
                for seq in numbers_list:
                    view_pdb.add_representation("ball+stick",selection=f"{seq[0]}")
                    """if seq_id != seq[0]:
                        view_pdb.add_representation("label",selection=f"{seq[0]}", text = f"{seq[1]}")
                        seq_id = seq[0]"""
                    
            """
            is_File_generated = True
            view_json = ""
            while(is_File_generated):
                try:
                    view_json = nglview.show_file(f"templates/mutation_templates/{file.filename[:-4]}.json")
                    view_json.representations = representations
                    is_File_generated = False
                except:
                    continue
            nglview.write_html(f"templates/mutation_templates/{file.filename[:-4]}.html",[view_json])
            """

            is_File_generated = True
            while(is_File_generated):
                try:
                    os.remove(f"uploads/{file.filename}")
                    is_File_generated = False
                except:
                    continue
            is_File_generated = True
            while(is_File_generated):
                try:
                    os.remove(f"uploads/{file.filename[:-4]}.cif")
                    is_File_generated = False
                except:
                    continue
            is_File_generated = True
            while(is_File_generated):
                try:
                    os.remove(f"templates/mutation_templates/{file.filename[:-4]}.json")
                    is_File_generated = False
                except:
                    continue
            
            nglview.write_html(file_path_left,[view_pdb])
        else:
            return redirect(url_for("base"))
        
        return redirect(url_for("after_upload"))

    return render_template("base.html")

@app.route("/after_upload", methods=["GET","POST"])
def after_upload():
    selected_button = request.form.get('button')
    """if selected_button == "json":
        return redirect(url_for("ngl_view_json"))"""
    if selected_button == "button":
        return redirect(url_for("ngl_view_pdb"))
    return render_template("after_upload.html")

@app.route("/ngl_view_pdb",methods=["GET","POST"])
def ngl_view_pdb():
    if session["file_path"]:
        return render_template(f"mutation_templates/{session['file_path']}")
    return render_template("")

"""@app.route("/ngl_view_pdb",methods=["GET","POST"])
def ngl_view_json():
    if session["json_path"]:
        return render_template(f"mutation_no/{session['json_path']}")
    return render_template("")"""

async def run_maxit(file):
    with open("maxit_run.py","w") as maxit_file:
        tmp_list = [
            "import os\n",
            "os.chdir(f'/home/{os.getlogin()}/maxit-v11.100-prod-src/bin')\n",
            "os.environ['RCSBROOT'] = f'/home/{os.getlogin()}/maxit-v11.100-prod-src'\n",
            "os.environ['PATH'] = '$RCSBROOT/bin:$PATH'\n",
            f"os.popen(f'./maxit -input {os.getcwd()}/{file.filename} -output /home/{os.getlogin()}/Desktop/NglView_website/uploads/{file.filename[:-4]}.cif -o 1')"
        ]
        maxit_file.writelines(tmp_list)
    os.system("python maxit_run.py")
    os.remove("maxit_run.py")

async def run_json(file):
    mutation_name = file.filename[:-4].split("_")[-1]
    mutation_name = mutation_name[1:-1]
    protein_name = mutation_name[0]
    residue_number = mutation_name[1:]
    with open("json_run.py","w") as json_file:
        tmp_list = [
            "import os\n",
            f"os.popen(f'pdbe-arpeggio -s /{protein_name}/{residue_number}/ -o templates/mutation_templates/ uploads/{file.filename[:-4]}.cif')"
        ]
        json_file.writelines(tmp_list)
    os.system("python json_run.py")
    os.remove("json_run.py")

app.run(debug=True)
