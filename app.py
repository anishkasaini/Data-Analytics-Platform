from flask import Flask, render_template, request
import pandas as pd
import seaborn as sns
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import uuid

app = Flask(__name__)


UPLOAD_FOLDER = "/tmp/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    try:
        file = request.files.get("file")

        if file is None or file.filename == "":
            return "No file selected"

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        # Read file
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(file_path)

        elif file.filename.lower().endswith(".xlsx"):
            df = pd.read_excel(file_path)

        else:
            return "Only CSV and Excel files are allowed"


        total_rows = df.shape[0]
        total_columns = df.shape[1]
        columns = df.columns.tolist()
        preview = df.head().to_dict(orient="records")
        data_types = df.dtypes.astype(str).to_dict()
        missing_values = df.isnull().sum().to_dict()
        duplicate_rows = int(df.duplicated().sum())

        statistics = df.describe(include="all").fillna("").to_html(
            classes="table",
            border=0
        )


        graph_files = []
        numeric = df.select_dtypes(include="number")

        # Histogram
        if len(numeric.columns) > 0:
            plt.figure(figsize=(8,5))
            numeric.hist()
            file1 = "hist_" + str(uuid.uuid4()) + ".png"
            plt.savefig("static/" + file1)
            plt.close()
            graph_files.append(file1)

        # Bar chart
        categorical = df.select_dtypes(include="object").columns

        if len(categorical) > 0:
            col = categorical[0]

            plt.figure(figsize=(8,5))
            df[col].value_counts().head(10).plot(kind="bar")
            file2 = "bar_" + str(uuid.uuid4()) + ".png"
            plt.savefig("static/" + file2)
            plt.close()
            graph_files.append(file2)

        # Heatmap
        if len(numeric.columns) > 1:
            plt.figure(figsize=(8,5))
            sns.heatmap(numeric.corr(), annot=True)
            file3 = "heatmap_" + str(uuid.uuid4()) + ".png"
            plt.savefig("static/" + file3)
            plt.close()
            graph_files.append(file3)

        # Distribution
        if len(numeric.columns) > 0:
            plt.figure(figsize=(8,5))
            sns.kdeplot(data=numeric, warn_singular=False)
            file4 = "dist_" + str(uuid.uuid4()) + ".png"
            plt.savefig("static/" + file4)
            plt.close()
            graph_files.append(file4)

        return render_template(
            "report.html",
            total_rows=total_rows,
            total_columns=total_columns,
            columns=columns,
            preview=preview,
            data_types=data_types,
            missing_values=missing_values,
            duplicate_rows=duplicate_rows,
            statistics=statistics,
            graph_files=graph_files
        )

    except Exception as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)
