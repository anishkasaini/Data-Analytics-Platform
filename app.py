from flask import Flask, render_template, request
import pandas as pd
import seaborn as sns
import os
import matplotlib.pyplot as plt
import uuid



app = Flask(__name__)




                    # Upload Folder Configuration


UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


if not os.path.exists("static"):
    os.makedirs("static")



                      # Home Page


@app.route("/")
def home():
    return render_template("index.html")




                      # Upload Route


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("file")


    if file is None:
        return "No file uploaded."


    if file.filename == "":
        return "Please select a file."



    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )


    file.save(file_path)



                        # Read Dataset
 

    if file.filename.lower().endswith(".csv"):

        df = pd.read_csv(file_path)


    elif file.filename.lower().endswith(".xlsx"):

        df = pd.read_excel(file_path)


    else:

        return "Only CSV and Excel files are supported."




  
                  # Dataset Information
    

    total_rows = df.shape[0]

    total_columns = df.shape[1]


    columns = df.columns.tolist()


    preview = df.head().to_dict(
        orient="records"
    )


    data_types = df.dtypes.astype(str).to_dict()


    missing_values = df.isnull().sum().to_dict()


    duplicate_rows = int(
        df.duplicated().sum()
    )



    statistics = (
        df.describe(include="all")
        .fillna("")
        .to_html(
            classes="table",
            border=0
        )
    )


                  # Create Graphs


    graph_files = []


    # Histogram

    numeric = df.select_dtypes(
        include="number"
    )


    if len(numeric.columns) > 0:


        plt.figure(figsize=(8,5))


        numeric.hist()


        plt.title(
            "Histogram of Numerical Columns"
        )


        plt.tight_layout()



        file1 = "histogram_" + str(uuid.uuid4()) + ".png"


        plt.savefig(
            "static/" + file1,
            dpi=300
        )


        plt.close()


        graph_files.append(file1)


    # Bar Graph


    categorical = df.select_dtypes(
        include="object"
    ).columns



    if len(categorical) > 0:


        column = categorical[0]


        plt.figure(figsize=(8,5))


        df[column].value_counts().head(10).plot(
            kind="bar"
        )


        plt.title(
            "Bar Chart - " + column
        )


        plt.tight_layout()



        file2 = "bar_" + str(uuid.uuid4()) + ".png"


        plt.savefig(
            "static/" + file2,
            dpi=300
        )


        plt.close()


        graph_files.append(file2)



    # Correlation Heatmap


    if len(numeric.columns) > 1:


        plt.figure(figsize=(8,5))


        sns.heatmap(
            numeric.corr(),
            annot=True
        )


        plt.title(
            "Correlation Heatmap"
        )


        plt.tight_layout()



        file3 = "correlation_" + str(uuid.uuid4()) + ".png"


        plt.savefig(
            "static/" + file3,
            dpi=300
        )


        plt.close()


        graph_files.append(file3)


    # Distribution Graph


    if len(numeric.columns) > 0:


        plt.figure(figsize=(8,5))


        sns.kdeplot(
            data=numeric
        )


        plt.title(
            "Distribution Plot"
        )


        plt.tight_layout()



        file4 = "distribution_" + str(uuid.uuid4()) + ".png"


        plt.savefig(
            "static/" + file4,
            dpi=300
        )


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



