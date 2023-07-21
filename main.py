from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_geolocation import GeoManager, current_geo
from flask_socketio import SocketIO
import nglview
import os
import subprocess
import asyncio
import threading
import time
import json
import ipaddress
import requests
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
socketio = SocketIO(app)
enterance_key = set([])
@app.route("/", methods=["GET","POST"])
async def index():
    dt = datetime.now()
    if request.remote_addr not in enterance_key:
        req = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey=c2a0dbe5081b47118d9e059b72aa708d'+'&ip=' + request.remote_addr)
        print(req.json()["country_name"])
        enterance_key.add(request.remote_addr)
    file_path_left = ""
    session["possible_mutations_list"] = os.listdir("possible_mutations")
    os.system("rm -rf templates/mutation_templates")
    os.system("rm -rf uploads")
    if "file" in request.files or request.form.get("possible_mutations"):
        
        os.mkdir("templates/mutation_templates")
        os.mkdir("uploads")
        file_name = ""
        if request.form.get("possible_mutations"):
            file_name = request.form.get("possible_mutations")
            os.system(f"cp ./possible_mutations/{file_name} ./uploads/")
        else:
            file = request.files["file"]
            file.save(f"uploads/{file.filename}")
            file_name = file.filename

        if ".pdb" in file_name:
            is_File_generated = True
            #print(file_name)
            while(is_File_generated):
                is_File_generated  = not (os.path.exists(f"uploads/{file_name}"))

            view_pdb = nglview.show_structure_file(f"uploads/{file_name}")
            #print(file_name)
            background = request.form.get("Background")
            if background == "Background":
                view_pdb.background = "black"
            file_path_left=f"templates/mutation_templates/{file_name[:-4]}.html"
            session["file_path"] = f"{file_name[:-4]}.html"
            session['file_name'] = f"{file_name[:-4]}"
            mutation_name = file_name[:-4].split("_")[-1]
            mutation_name = mutation_name[1:-1]
            protein_name = mutation_name[0]
            residue_number = mutation_name[1:]
            residue_number = int(residue_number)
            """view_pdb_right = nglview.show_structure_file(f"uploads/{file.filename}")
            file_path_right=f"templates/mutation_no/{file.filename[:-4]}.html"
            nglview.write_html(file_path_right,[view_pdb_right])"""

            await run_maxit(file_name)
            #print("1")
            is_File_generated = True
            while(is_File_generated):
                is_File_generated = not (os.path.exists(f"uploads/{file_name[:-4]}.cif"))
            await run_json(file_name)
            #print("2")
            residue_dict = {}
            residue_list = []
            cleared_list = []
            select_numbers = set([])
            numbers_list = []
            
            is_File_generated = True
            while(is_File_generated):
                #print("2")
                try:
                    with open(f"templates/mutation_templates/{file_name[:-4]}.json","r") as json_file:
                        residue_dict = json.load(json_file)
                        residue_list = list(residue_dict)
                        seq_ids_set = set([])
                        atom_representation = request.form.get("atom_representation")
                        names = request.form.get('Names')
                        spin = request.form.get('Spin')
                        bonds_without_Carbon = request.form.get("Bonds_without_Carbon")
                        bonds_with_Carbon = request.form.get("Bonds_with_Carbon")
                        pro_representation = request.form.get("pro_representation")
                        width = request.form.get("Width")
                        height = request.form.get("Height")
                        
                        #label_comp_id = ""
                        for seq in residue_list:
                            if seq["bgn"]["auth_seq_id"] == residue_number or seq["end"]["auth_seq_id"] == residue_number:

                                if seq["bgn"]["auth_seq_id"] == residue_number:
                                    label_comp_id = seq["bgn"]["label_comp_id"]
                                else:
                                    label_comp_id = seq["end"]["label_comp_id"]

                                cleared_list.append(seq)
                                select_numbers.add((seq["bgn"]["auth_seq_id"],seq["bgn"]["label_comp_id"]))
                                select_numbers.add((seq["end"]["auth_seq_id"],seq["end"]["label_comp_id"]))
                                if bonds_without_Carbon == "Bonds_without_Carbon":
                                    if 'C' not in seq['bgn']['auth_atom_id'] and 'C' not in seq['end']['auth_atom_id']:
                                        view_pdb.add_representation("distance",atomPair=[[f"{seq['bgn']['auth_seq_id']}.{seq['bgn']['auth_atom_id']}"
                                                                                    ,f"{seq['end']['auth_seq_id']}.{seq['end']['auth_atom_id']}"]])
                                        seq_ids_set.add((seq['bgn']['auth_seq_id'],seq['end']['auth_seq_id']))
                                        seq_ids_set.add((seq['end']['auth_seq_id'],seq['bgn']['auth_seq_id']))
                                        continue

                                if bonds_with_Carbon == "Bonds_with_Carbon":
                                    if (seq['bgn']['auth_seq_id'],seq['end']['auth_seq_id']) not in seq_ids_set and (
                                        seq['end']['auth_seq_id'],seq['bgn']['auth_seq_id']) not in seq_ids_set and (
                                        seq['end']['auth_seq_id'] == residue_number or seq['bgn']['auth_seq_id'] == residue_number):
                                        view_pdb.add_representation("distance",atomPair=[[f"{seq['bgn']['auth_seq_id']}.{seq['bgn']['auth_atom_id']}"
                                                                                    ,f"{seq['end']['auth_seq_id']}.{seq['end']['auth_atom_id']}"]])
                                        seq_ids_set.add((seq['bgn']['auth_seq_id'],seq['end']['auth_seq_id']))
                                        seq_ids_set.add((seq['end']['auth_seq_id'],seq['bgn']['auth_seq_id']))

                        if width and height:
                            view_pdb._set_size(width,height)
                        elif width:
                            view_pdb._set_size(width,"1000px")
                        elif height:
                            view_pdb._set_size("1000px",height)
                        else:
                            view_pdb._set_size("1000px","1000px")
                        

                        if bool(spin):
                            view_pdb._set_spin(bool(spin),180)

                        numbers_list = list(select_numbers)
                        seq_id = 0
                        view_pdb.remove_class(className="text")
                        for seq in numbers_list:
                            view_pdb.add_representation(atom_representation,selection=f"{seq[0]}")
                            if names == "Names":
                                if seq_id != seq[0]:
                                    view_pdb.add_representation("label",selection=f"{seq[0]}.C",labelType = "residue name")
                                    seq_id = seq[0]
                        view_pdb.add_representation(pro_representation)
                    is_File_generated = False
                except:
                    continue
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
            """
            is_File_generated = True
            while(is_File_generated):
                is_File_generated = (os.path.exists(f"uploads/{file.filename}"))
                try:
                    os.remove(f"uploads/{file.filename}")
                    is_File_generated = (os.path.exists(f"uploads/{file.filename}"))
                except:
                    continue
            is_File_generated = True
            while(is_File_generated):
                is_File_generated = (os.path.exists(f"uploads/{session['file_name']}.cif"))
                try:
                    os.remove(f"uploads/{file.filename[:-4]}.cif")
                    is_File_generated = (os.path.exists(f"uploads/{file.filename[:-4]}.cif"))
                except:
                    continue
            is_File_generated = True
            while(is_File_generated):
                is_File_generated = (os.path.exists(f"templates/mutation_templates/{file.filename[:-4]}.json"))
                try:
                    os.remove(f"templates/mutation_templates/{file.filename[:-4]}.json")
                    is_File_generated = (os.path.exists(f"templates/mutation_templates/{file.filename[:-4]}.json"))
                except:
                    continue
            """
            nglview.write_html(file_path_left,[view_pdb])
        else:
            return redirect(url_for("base"))
        
        return redirect(url_for("ngl_view_pdb"))

    return render_template("base.html")

@socketio.on('disconnect')
def disconnect_delete_files():
    enterance_key.remove(request.remote_addr)

"""
@app.route("/after_upload", methods=["GET","POST"])
def after_upload():
    selected_button = request.form.get('button')
    if selected_button == "json":
        return redirect(url_for("ngl_view_json"))
    if selected_button == "button":
        return redirect(url_for("ngl_view_pdb"))
    return render_template("after_upload.html")
    """
@app.route("/ngl_view_pdb",methods=["GET","POST"])
def ngl_view_pdb():
    """
    is_File_generated = True
    while(is_File_generated):
        is_File_generated = (os.path.exists(f"uploads/{session['file_name']}.cif"))
        try:
            os.remove(f"uploads/{session['file_name']}.cif")
            is_File_generated = (os.path.exists(f"uploads/{session['file_name']}.cif"))
        except:
            continue
        """
    if session["file_path"]:
        return render_template(f"mutation_templates/{session['file_path']}")
    return render_template("")

"""@app.route("/ngl_view_pdb",methods=["GET","POST"])
def ngl_view_json():
    if session["json_path"]:
        return render_template(f"mutation_no/{session['json_path']}")
    return render_template("")"""

async def run_maxit(file_name):
    with open("maxit_run.py","w") as maxit_file:
        tmp_list = [
            "import os\n",
            "os.chdir(f'/home/{os.getlogin()}/maxit-v11.100-prod-src/bin')\n",
            "os.environ['RCSBROOT'] = f'/home/{os.getlogin()}/maxit-v11.100-prod-src'\n",
            "os.environ['PATH'] = '$RCSBROOT/bin:$PATH'\n",
            f"os.popen(f'./maxit -input {os.getcwd()}/uploads/{file_name} -output /home/{os.getlogin()}/Desktop/NglView_website/uploads/{file_name[:-4]}.cif -o 1')"
        ]
        #print(file_name)
        maxit_file.writelines(tmp_list)
    os.system("python maxit_run.py")
    os.remove("maxit_run.py")

async def run_json(file_name):
    mutation_name = file_name[:-4].split("_")[-1]
    mutation_name = mutation_name[1:-1]
    protein_name = mutation_name[0]
    residue_number = mutation_name[1:]
    with open("json_run.py","w") as json_file:
        tmp_list = [
            "import os\n",
            f"os.popen(f'pdbe-arpeggio -s /{protein_name}/{residue_number}/ -o templates/mutation_templates/ uploads/{file_name[:-4]}.cif')"
        ]
        json_file.writelines(tmp_list)
    os.system("python json_run.py")
    os.remove("json_run.py")

app.run(debug=True)
