from flask import Flask, render_template, request, redirect, url_for, session
import nglview
import os
app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key"
@app.route("/", methods=["GET","POST"])
def index():
    file_path = ""
    if "file" in request.files:
        file = request.files["file"]
        file.save(f"uploads/{file.filename}")
        view = nglview.show_structure_file(f"uploads/{file.filename}")
        file_path=f"templates/mutation_templates/{file.filename[:-4]}.html"
        nglview.write_html(file_path,[view])
        session["file_path"] = f"{file.filename[:-4]}.html"
        os.remove(f"uploads/{file.filename}")
        return redirect(url_for("after_upload"))

    return render_template("base.html")

@app.route("/after_upload", methods=["GET","POST"])
def after_upload():
    if request.method == "POST":
        return render_template(f"mutation_templates/{session['file_path']}")
    return render_template("after_upload.html")

@app.route("/ngl_view",methods=["GET","POST"])
def ngl_view():
    if session["file_path"]:
        return render_template(f"mutation_templates/{session['file_path']}")
    return render_template("")
app.run(debug=True)
