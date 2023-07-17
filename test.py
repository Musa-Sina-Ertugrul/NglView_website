from flask import Flask, render_template, request, redirect, url_for, session
import nglview
import os
import subprocess
import asyncio
import threading
import time
app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
representations = [
    {"type": "cartoon", "params": {
        "sele": "protein", "color": "residueindex"
    }}
]
@app.route("/", methods=["GET","POST"])
async def index():
    file_path_left = ""
    if "file" in request.files:
        file = request.files["file"]
        file.save(f"uploads/{file.filename}")
        if ".pdb" in file.filename:
            view_pdb_left = nglview.show_structure_file(f"uploads/{file.filename}")
            view_pdb_left.representations = representations
            view_pdb_left.background = "black"
            view_pdb_left.add_representation("ball+stick",selection="10-20")
            view_pdb_left.add_representation("label",selection="10-20",labelType="residue name",antialias=True)
            view_pdb_left.add_representation("line",selection="10-20")
            file_path_left=f"templates/mutation_templates/{file.filename[:-4]}.html"
            nglview.write_html(file_path_left,[view_pdb_left])
            """view_pdb_right = nglview.show_structure_file(f"uploads/{file.filename}")
            file_path_right=f"templates/mutation_no/{file.filename[:-4]}.html"
            nglview.write_html(file_path_right,[view_pdb_right])"""
            """session["file_path"] = f"{file.filename[:-4]}.html"
            await run_maxit(file)
            time.sleep(2)
            await run_json(file)
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
            """
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
                    continue"""
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
"""
async def run_maxit(file):
    with open("maxit_run.py","w") as maxit_file:
        tmp_list = [
            "import os\n",
            "os.chdir(f'/home/{os.getlogin()}/maxit-v11.100-prod-src/bin')\n",
            "os.environ['RCSBROOT'] = f'/home/{os.getlogin()}/maxit-v11.100-prod-src'\n",
            "os.environ['PATH'] = '$RCSBROOT/bin:$PATH'\n",
            f"os.popen(f'./maxit -input {os.getcwd()}/{file.filename} -output /home/{os.getlogin()}/Desktop/NglView_website//uploads/{file.filename[:-4]}.cif -o 1')"
        ]
        maxit_file.writelines(tmp_list)
    os.system("python maxit_run.py")
    os.remove("maxit_run.py")

async def run_json(file):
    with open("json_run.py","w") as json_file:
        tmp_list = [
            "import os\n",
            f"os.popen(f'pdbe-arpeggio -o templates/mutation_templates/ uploads/{file.filename[:-4]}.cif')"
        ]
        json_file.writelines(tmp_list)
    os.system("python json_run.py")
    os.remove("json_run.py")
"""
app.run(debug=True)
