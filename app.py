from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_mysqldb import MySQL
import pandas as pd
import io
from waitress import serve
import MySQLdb.cursors

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'mysql-6051097-chitsanwin-fcc2.a.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = 'AVNS_lHse-6jdl-kbb4dFsv0'
app.config['MYSQL_DB'] = 'defaultdb'
app.config['MYSQL_PORT'] = 15227

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cold_store')
def cold_store():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    unique_values = {}
    
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        cursor.execute(f'SELECT DISTINCT {column} FROM cold_store_in')
        unique_values[column] = [row[column] for row in cursor.fetchall()]
    
    return render_template('cold_store.html', unique_values=unique_values)

@app.route('/api/cold_store_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cold_store_in():
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cold_store_in')
        data = cursor.fetchall()
        return jsonify(data)
    
    elif request.method == 'POST':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO cold_store_in (Sr_No, Fi_No, Date, Company, Item, Type, Size, Conversion, Total_Mc, Total_Kg, Freezing_Type) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                          (data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type']))
        mysql.connection.commit()
        return jsonify({"message": "Entry added successfully"}), 201

    elif request.method == 'PUT':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE cold_store_in SET Sr_No=%s, Fi_No=%s, Date=%s, Company=%s, Item=%s, Type=%s, Size=%s, Conversion=%s, Total_Mc=%s, Total_Kg=%s, Freezing_Type=%s 
                          WHERE ID=%s''', 
                          (data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type'], data['ID']))
        mysql.connection.commit()
        return jsonify({"message": "Entry updated successfully"}), 200

    elif request.method == 'DELETE':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM cold_store_in WHERE ID = %s', [data['ID']])
        mysql.connection.commit()
        return jsonify({"message": "Entry deleted successfully"}), 200
    
@app.route('/api/cold_store_in/<int:id>', methods=['GET'])
def get_cold_store_in_entry(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM cold_store_in WHERE ID = %s', [id])
    data = cursor.fetchone()
    return jsonify(data)

@app.route('/api/unique_values', methods=['GET'])
def unique_values():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    unique_values = {}
    
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        cursor.execute(f'SELECT DISTINCT {column} FROM cold_store_in')
        unique_values[column] = [row[column] for row in cursor.fetchall()]
    
    return jsonify(unique_values)

@app.route('/processing')
def processing():
    return render_template('processing.html')

@app.route('/api/processing_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def processing_in():
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM processing_in')
        data = cursor.fetchall()
        return jsonify(data)
    
    elif request.method == 'POST':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO processing_in (Sr_No, Fi_No, Date, Company, Item, Type, Size, Conversion, Total_Mc, Total_Kg, Freezing_Type) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                          (data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type']))
        mysql.connection.commit()
        return jsonify({"message": "Entry added successfully"}), 201

    elif request.method == 'PUT':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE processing_in SET Sr_No=%s, Fi_No=%s, Date=%s, Company=%s, Item=%s, Type=%s, Size=%s, Conversion=%s, Total_Mc=%s, Total_Kg=%s, Freezing_Type=%s 
                          WHERE ID=%s''', 
                          (data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type'], data['ID']))
        mysql.connection.commit()
        return jsonify({"message": "Entry updated successfully"}), 200

    elif request.method == 'DELETE':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM processing_in WHERE ID = %s', [data['ID']])
        mysql.connection.commit()
        return jsonify({"message": "Entry deleted successfully"}), 200

@app.route('/api/processing_in/<int:id>', methods=['GET'])
def get_processing_in_entry(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM processing_in WHERE ID = %s', [id])
    data = cursor.fetchone()
    return jsonify(data)

@app.route('/api/download_excel', methods=['POST'])
def download_excel():
    data = request.json
    
    # Define the desired column order
    column_order = ['ID', 'Sr_No', 'Fi_No', 'Date', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Total_Mc', 'Total_Kg', 'Freezing_Type']
    
    # Create DataFrame with specified column order
    df = pd.DataFrame(data, columns=column_order)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')

    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='filtered_data.xlsx',
        as_attachment=True
    )

@app.route('/calc')
def calc():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    unique_values = {}
    
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        cursor.execute(f'SELECT DISTINCT {column} FROM cold_store_in')
        unique_values[column] = [row[column] for row in cursor.fetchall()]
    
    return render_template('calc.html', unique_values=unique_values)

@app.route('/api/balance_in', methods=['GET'])
def balance_in():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sr_no = request.args.get('Sr_No')
    fi_no = request.args.get('Fi_No')
    company = request.args.get('Company')
    item = request.args.get('Item')
    type_ = request.args.get('Type')
    size = request.args.get('Size')
    conversion = request.args.get('Conversion')
    freezing_type = request.args.get('Freezing_Type')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query = 'SELECT * FROM cold_store_in WHERE Balance > 0'
    params = []
    
    if start_date:
        query += ' AND Date >= %s'
        params.append(start_date)
    
    if end_date:
        query += ' AND Date <= %s'
        params.append(end_date)
    
    if sr_no:
        query += ' AND Sr_No = %s'
        params.append(sr_no)
    
    if fi_no:
        query += ' AND Fi_No = %s'
        params.append(fi_no)
    
    if company:
        query += ' AND Company = %s'
        params.append(company)
    
    if item:
        query += ' AND Item = %s'
        params.append(item)
    
    if type_:
        query += ' AND Type = %s'
        params.append(type_)
    
    if size:
        query += ' AND Size = %s'
        params.append(size)
    
    if conversion:
        query += ' AND Conversion = %s'
        params.append(conversion)
    
    if freezing_type:
        query += ' AND Freezing_Type = %s'
        params.append(freezing_type)
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    return jsonify(data)

@app.route('/export')
def export():
    return render_template('export.html')

@app.route('/api/export_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def export_in():
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM export_in')
        data = cursor.fetchall()
        return jsonify(data)
    
    elif request.method == 'POST':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''INSERT INTO export_in (CSID, Sr_No, Fi_No, Date, Company, Item, Type, Size, Conversion, Total_Days, Total_Mc, Total_Kg, Freezing_Type) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                          (data['CSID'], data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Days'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type']))
        mysql.connection.commit()
        return jsonify({"message": "Entry added successfully"}), 201

    elif request.method == 'PUT':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('''UPDATE export_in SET CSID=%s, Sr_No=%s, Fi_No=%s, Date=%s, Company=%s, Item=%s, Type=%s, Size=%s, Conversion=%s,Total_Days=%s, Total_Mc=%s, Total_Kg=%s, Freezing_Type=%s 
                          WHERE ID=%s''', 
                          (data['CSID'], data['Sr_No'], data['Fi_No'], data['Date'], data['Company'], data['Item'], data['Type'], data['Size'], data['Conversion'], data['Total_Days'], data['Total_Mc'], data['Total_Kg'], data['Freezing_Type'], data['ID']))
        mysql.connection.commit()
        return jsonify({"message": "Entry updated successfully"}), 200

    elif request.method == 'DELETE':
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM export_in WHERE ID = %s', [data['ID']])
        mysql.connection.commit()
        return jsonify({"message": "Entry deleted successfully"}), 200

@app.route('/api/export_in/<int:id>', methods=['GET'])
def get_export_in_entry(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM export_in WHERE ID = %s', [id])
    data = cursor.fetchone()
    return jsonify(data)

@app.route('/api/download_epexcel', methods=['POST'])
def download_epexcel():
    data = request.json
    
    # Define the desired column order
    column_order = ['ID', 'Sr_No', 'Fi_No', 'Date', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Total_Mc', 'Total_Kg', 'Freezing_Type', 'Total_Days', 'CSID']
    
    # Create DataFrame with specified column order
    df = pd.DataFrame(data, columns=column_order)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')

    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        download_name='filtered_data.xlsx',
        as_attachment=True
    )

@app.route('/api/update_processing_mc', methods=['POST'])
def update_processing_mc():
    cursor = mysql.connection.cursor()
    query = '''UPDATE cold_store_in t1
               INNER JOIN processing_in t2 
               ON t1.Company = t2.Company
               AND t1.Item = t2.Item
               AND t1.Size = t2.Size
               AND t1.Conversion = t2.Conversion
               
               SET t1.Processing_mc = t2.Total_Kg'''
    cursor.execute(query)
    mysql.connection.commit()
    return jsonify({"message": "Processing_mc updated successfully"}), 200

@app.route('/api/update_exported_kg', methods=['POST'])
def update_exported_kg():
    try:
        cursor = mysql.connection.cursor()
        query1 = """
            UPDATE cold_store_in t1
            INNER JOIN (
                SELECT CSID, SUM(Total_kg) AS TotalAmount
                FROM export_in
                GROUP BY CSID
            ) AS t2 ON t1.ID = t2.CSID
              SET t1.Exported_kg = COALESCE(t2.TotalAmount, 0);
        """
        query2 = """
            UPDATE cold_store_in
            SET Balance = Total_kg - coalesce(Exported_kg, 0);
        """
        cursor.execute(query1)
        cursor.execute(query2)
        mysql.connection.commit()
        return jsonify({"message": "Exported_kg updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@app.route('/sync_data', methods=['POST'])
def sync_data():
    try:
        cursor = mysql.connection.cursor()
        # Add your queries here
        query1 = """
            UPDATE cold_store_in t1
            INNER JOIN (
                SELECT CSID, SUM(Total_kg) AS TotalAmount
                FROM export_in
                GROUP BY CSID
            ) AS t2 ON t1.ID = t2.CSID
              SET t1.Exported_kg = COALESCE(t2.TotalAmount, 0);
        """
        query2 = """
            UPDATE cold_store_in
            SET Balance = Total_kg - coalesce(Exported_kg, 0);
        """
        query3 = """
               UPDATE cold_store_in t1
               INNER JOIN processing_in t2 
               ON t1.Company = t2.Company
               AND t1.Item = t2.Item
               AND t1.Size = t2.Size
               AND t1.Conversion = t2.Conversion
               
               SET t1.Processing_mc = t2.Total_Kg"""
        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3)
        mysql.connection.commit()
        return jsonify({"message": "Data synchronized successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500    



if __name__ == '__main__':
    serve(app, host='192.168.0.88', port=8088, threads= 6)
