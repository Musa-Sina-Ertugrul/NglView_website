from flask import Flask, render_template, request
import nglview
import os
app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    file_path = ""
    if "file" in request.files:
        file = request.files["file"]
        file.save(f"uploads/{file.filename}")
        view = nglview.show_structure_file(f"uploads/{file.filename}")
        file_path=f"mutations_html/{file.filename[:-4]}.html"
        nglview.write_html(file_path,[view])
        return render_template("after_upload.html",file_path=file_path)

    return render_template("base.html")

app.run(debug=True)