from flask import Flask, request, jsonify
# import psycopg2
import pymysql
import bcrypt
import os
from dotenv import load_dotenv
from flask_cors import CORS
import pandas as pd
import re
import os
# pip install psycopg2-binary bcrypt python-dotenv flask-cors


load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)  # Allow all origins



def get_db_connection():
    connection = pymysql.connect(
        user=os.getenv("DB_USER",""),
        password=os.getenv("DB_PASSWORD", ""),
        host="localhost",
        port=3306,
        database=os.getenv("DB_NAME", "markovkaryawandb")
    )
    return connection

def preprocess_text(text, type):
    if type == 'name':
        match = re.search(r'Nama[\xa0]*:?\s*(.*)', text)
    elif type == 'job_title':
        match = re.search(r'Job Title[\xa0]*:?\s*(.*)', text)
    else:
        match = re.search(r'Job Level[\xa0]*:?\s*(.*)', text)
    if match:
        return match.group(1).strip()  # Return the name, stripping any leading/trailing spaces
    return None


# Route to add a new user
@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_password),
        )
        conn.commit()

        # Close connection
        cursor.close()
        conn.close()

        return jsonify({"message": f"User {username} successfully registered!"}), 201
    except pymysql.IntegrityError:
        # Handle unique constraint violation
        conn.rollback()
        return jsonify({"message": "Username already exists"}), 400
    except Exception as e:
        # Handle other exceptions
        return jsonify({"message": str(e)}), 500

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    # print(username)
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        # print(user[1])
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "Invalid credentials"}), 400

        # Compare password with the hashed one in the database
        stored_password = user[2]  # Assuming password is in the 3rd column (index 2)
        if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "wrong password"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/kpi", methods=["POST"])
def kpi():
    # Define the file path
    file_path = "HCCA 2023 MM.xlsx"
    file_name = os.path.basename(file_path)

    # Extract the division and year from the file name using regex
    match = re.match(r"([A-Za-z]+)\s(\d{4})", file_name)
    division = ''
    year = ''
    if match:
        division = match.group(1)  # HCCA (Division)
        year = match.group(2)      # 2023 (Year)
        print(f"Division: {division}")
        print(f"Year: {year}")
    else:
        print("File name doesn't match expected format")

    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path, header=None)

    # Split the data based on blank rows
    blank_rows = df[df.isnull().all(axis=1)].index
    tables = []
    prev_idx = 0
    for idx in blank_rows:
        table = df.iloc[prev_idx:idx].reset_index(drop=True)
        tables.append(table)
        prev_idx = idx + 1
    table = df.iloc[prev_idx:].reset_index(drop=True)
    tables.append(table)

    # Extract the relevant columns for each table
    names, job_titles, job_levels, objectives, kpi_names, UOMs, THs, targets = [], [], [], [], [], [], [], []
    max_values, methods, weights, jan, feb, mar, apr, may, jun, jul, aug, sep = [], [], [], [], [], [], [], [], [], [], [], []
    oct, nov, dec, scores = [], [], [], []

    for i in range(len(tables)):
        names.append(preprocess_text(tables[i][0][0], 'name'))
        job_titles.append(preprocess_text(tables[i][0][1], 'job_title'))
        job_levels.append(preprocess_text(tables[i][0][2], 'job_level'))
        objectives.append(tables[i][5:-2][0].tolist())
        kpi_names.append(tables[i][5:-2][1].tolist())
        UOMs.append(tables[i][5:-2][2].tolist())
        THs.append(tables[i][5:-2][3].tolist())
        targets.append(tables[i][5:-2][4].tolist())
        max_values.append(tables[i][5:-2][5].tolist())
        methods.append(tables[i][5:-2][6].tolist())
        weights.append(tables[i][5:-2][7].tolist())
        jan.append(tables[i][5:-2][8].tolist())
        feb.append(tables[i][5:-2][9].tolist())
        mar.append(tables[i][5:-2][10].tolist())
        apr.append(tables[i][5:-2][11].tolist())
        may.append(tables[i][5:-2][12].tolist())
        jun.append(tables[i][5:-2][13].tolist())
        jul.append(tables[i][5:-2][14].tolist())
        aug.append(tables[i][5:-2][15].tolist())
        sep.append(tables[i][5:-2][16].tolist())
        oct.append(tables[i][5:-2][17].tolist())
        nov.append(tables[i][5:-2][18].tolist())
        dec.append(tables[i][5:-2][19].tolist())
        scores.append(tables[i][5:-2][20].tolist())

    # Create a dictionary to structure the data
    data = {
        'Name': names,
        'Division': division,
        'Job Title': job_titles,
        'Job Level': job_levels,
        'Objective': objectives,
        'KPI Name': kpi_names,
        'UOM': UOMs,
        'TH': THs,
        'Target': targets,
        'Max Value': max_values,
        'Method': methods,
        'Weight': weights,
        'Year': year,
        'JAN': jan,
        'FEB': feb,
        'MAR': mar,
        'APR': apr,
        'MAY': may,
        'JUN': jun,
        'JUL': jul,
        'AUG': aug,
        'SEP': sep,
        'OCT': oct,
        'NOV': nov,
        'DEC': dec,
        'Score': scores
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Calculate the maximum length of any list in the columns
    max_len = max(
        df['Objective'].apply(len).max(), 
        df['KPI Name'].apply(len).max(),
        df['UOM'].apply(len).max(),
        df['TH'].apply(len).max(),
        df['Target'].apply(len).max(),
        df['Max Value'].apply(len).max(),
        df['Method'].apply(len).max(),
        df['Weight'].apply(len).max(),
        df['JAN'].apply(len).max(),
        df['FEB'].apply(len).max(),
        df['MAR'].apply(len).max(),
        df['APR'].apply(len).max(),
        df['MAY'].apply(len).max(),
        df['JUN'].apply(len).max(),
        df['JUL'].apply(len).max(),
        df['AUG'].apply(len).max(),
        df['SEP'].apply(len).max(),
        df['OCT'].apply(len).max(),
        df['NOV'].apply(len).max(),
        df['DEC'].apply(len).max(),
        df['Score'].apply(len).max()
    )

    # Repeat rows for Name, Job Title, and Job Level according to max_len
    df_repeated = df.loc[df.index.repeat(max_len)].reset_index(drop=True)

    # For each list column, truncate or expand them to match max_len
    list_columns = ['Objective', 'KPI Name', 'UOM', 'TH', 'Target', 'Max Value', 'Method', 'Weight', 'JAN', 'FEB', 
                    'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC', 'Score']

    for col in list_columns:
        df_repeated[col] = df_repeated[col].apply(lambda x: x[:max_len] if isinstance(x, list) else [x] * max_len)

    # Reset the index and explode the lists
    df_final = df_repeated.explode(list_columns).reset_index(drop=True)
    json_result = df_final.to_dict(orient="records")
    return jsonify({'data': json_result})
    
@app.route("/admin/Table")
def table():
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, position, department FROM employee")
        user = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify(user)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/admin/employee-detail/<int:id>", methods=["GET"])
def detail_employee(id):
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Gunakan parameter binding untuk menghindari SQL Injection
        cursor.execute("SELECT id, full_name, position, department FROM employee WHERE id = %s", (id,))
        user = cursor.fetchone()  # Mengambil satu baris data

        cursor.close()
        conn.close()

        # Jika user tidak ditemukan
        if user is None:
            return jsonify({"message": "Employee not found"}), 404

        # Mengembalikan hasil dalam bentuk JSON
        return jsonify(user)

    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
