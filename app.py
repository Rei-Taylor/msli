from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_migrate import Migrate
import pandas as pd
import io
from waitress import serve
from datetime import datetime
from sqlalchemy import Index

app = Flask(__name__)
app.config['DEBUG'] = True
# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:TotsukaSaika217@localhost:3306/msl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cache configuration
app.config['CACHE_TYPE'] = 'simple'

cache = Cache(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class ColdStoreIn(db.Model):
    __tablename__ = 'cold_store_in'
    ID = db.Column(db.Integer, primary_key=True)
    Sr_No = db.Column(db.String(50), index=True)
    Fi_No = db.Column(db.String(50), index=True)
    Date = db.Column(db.Date, index=True)
    Company = db.Column(db.String(100), index=True)
    Item = db.Column(db.String(100), index=True)
    Type = db.Column(db.String(50), index=True)
    Size = db.Column(db.String(50), index=True)
    Conversion = db.Column(db.String(50), index=True)
    Total_Mc = db.Column(db.Float)
    Total_Kg = db.Column(db.Float)
    Freezing_Type = db.Column(db.String(50), index=True)
    Exported_kg = db.Column(db.Float)
    Balance = db.Column(db.Float)
    Processing_mc = db.Column(db.Float)

    __table_args__ = (
        Index('idx_cold_store_in_company_date', 'Company', 'Date'),
    )

class ExportIn(db.Model):
    __tablename__ = 'export_in'
    ID = db.Column(db.Integer, primary_key=True)
    CSID = db.Column(db.Integer, db.ForeignKey('cold_store_in.ID'))
    Sr_No = db.Column(db.String(50), index=True)
    Fi_No = db.Column(db.String(50), index=True)
    Date = db.Column(db.Date, index=True)
    Ref_Date = db.Column(db.Date, index=True)
    Company = db.Column(db.String(100), index=True)
    Item = db.Column(db.String(100), index=True)
    Type = db.Column(db.String(50), index=True)
    Size = db.Column(db.String(50), index=True)
    Conversion = db.Column(db.Float, index=True)
    Total_Days = db.Column(db.Integer)
    Total_Mc = db.Column(db.Float)
    Total_Kg = db.Column(db.Float)
    Freezing_Type = db.Column(db.String(50), index=True)

class ProcessingIn(db.Model):
    __tablename__ = 'processing_in'
    ID = db.Column(db.Integer, primary_key=True)
    Sr_No = db.Column(db.String(50), index=True)
    Fi_No = db.Column(db.String(50), index=True)
    Date = db.Column(db.Date, index=True)
    Company = db.Column(db.String(100), index=True)
    Item = db.Column(db.String(100), index=True)
    Type = db.Column(db.String(50), index=True)
    Size = db.Column(db.String(50))
    Total_Mc = db.Column(db.Float)
    Conversion = db.Column(db.Float, index=True)
    Total_Kg = db.Column(db.Float)
    Freezing_Type = db.Column(db.String(50), index=True)

def serialize_model(model):
    """Convert SQLAlchemy model instance to dictionary."""
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cold_store')
def cold_store():
    unique_values = {}
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        unique_values[column] = db.session.query(getattr(ColdStoreIn, column)).distinct().all()
        unique_values[column] = [value[0] for value in unique_values[column]]
    return render_template('cold_store.html', unique_values=unique_values)

@app.route('/api/cold_store_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cold_store_in():
    try:
        if request.method == 'GET':
            data = ColdStoreIn.query.all()
            return jsonify([serialize_model(entry) for entry in data])
        
        elif request.method == 'POST':
            data = request.json
            sizes = [(data.get(f'Size_{i}'), data.get(f'Total_Mc_{i}')) for i in range(1, 6) if data.get(f'Size_{i}') and data.get(f'Total_Mc_{i}')]
            
            for size, total_mc in sizes:
                total_kg = float(data['Conversion']) * float(total_mc)
                entry = ColdStoreIn(
                    Sr_No=data['Sr_No'],
                    Fi_No=data['Fi_No'],
                    Date=datetime.strptime(data['Date'], '%Y-%m-%d').date(),
                    Company=data['Company'],
                    Item=data['Item'],
                    Type=data['Type'],
                    Size=size,
                    Conversion=data['Conversion'],
                    Total_Mc=total_mc,
                    Total_Kg=total_kg,
                    Freezing_Type=data['Freezing_Type']
                )
                db.session.add(entry)
            
            db.session.commit()
            return jsonify({"message": "Entries added successfully"}), 201

        elif request.method == 'PUT':
            data = request.json
            entry = db.session.get(ColdStoreIn, data['ID'])
            if entry:
                entry.Sr_No = data['Sr_No']
                entry.Fi_No = data['Fi_No']
                entry.Date = datetime.strptime(data['Date'], '%Y-%m-%d').date()
                entry.Company = data['Company']
                entry.Item = data['Item']
                entry.Type = data['Type']
                entry.Size = data['Size']
                entry.Conversion = data['Conversion']
                entry.Total_Mc = data['Total_Mc']
                entry.Total_Kg = data['Total_Kg']
                entry.Freezing_Type = data['Freezing_Type']
                db.session.commit()
                return jsonify({"message": "Entry updated successfully"}), 200
            return jsonify({"message": "Entry not found"}), 404

        elif request.method == 'DELETE':
            data = request.json
            print(f"Received DELETE request with data: {data}")
            entry = db.session.get(ColdStoreIn, data['ID'])
            if entry:
                db.session.delete(entry)
                db.session.commit()
                response = jsonify({"message": "Entry deleted successfully"})
                print(f"Returning response: {response.get_json()}")
                return response, 200
            response = jsonify({"message": "Entry not found"})
            print(f"Returning response: {response.get_json()}")
            return response, 404

    except Exception as e:
        response = jsonify({"message": str(e)})
        print(f"Returning response: {response.get_json()}")
        return response, 500

@app.route('/api/cold_store_in/<int:id>', methods=['GET'])
def get_cold_store_in_entry(id):
    try:
        entry = db.session.get(ColdStoreIn, id)
        if entry:
            return jsonify(serialize_model(entry))
        return jsonify({"message": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/unique_values', methods=['GET'])
def unique_values():
    try:
        unique_values = {}
        columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
        for column in columns:
            unique_values[column] = db.session.query(getattr(ColdStoreIn, column)).distinct().all()
            unique_values[column] = [value[0] for value in unique_values[column]]
        return jsonify(unique_values)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/processing')
def processing():
    unique_values = {}
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        unique_values[column] = db.session.query(getattr(ColdStoreIn, column)).distinct().all()
        unique_values[column] = [value[0] for value in unique_values[column]]
    return render_template('processing.html', unique_values=unique_values)

@app.route('/api/processing_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def processing_in():
    try:
        if request.method == 'GET':
            data = ProcessingIn.query.all()
            return jsonify([serialize_model(entry) for entry in data])
        
        elif request.method == 'POST':
            data = request.json
            sizes = [(data.get(f'Size_{i}'), data.get(f'Total_Mc_{i}')) for i in range(1, 6) if data.get(f'Size_{i}') and data.get(f'Total_Mc_{i}')]
            
            for size, total_mc in sizes:
                total_kg = float(data['Conversion']) * float(total_mc)
                entry = ProcessingIn(
                    Sr_No=data['Sr_No'],
                    Fi_No=data['Fi_No'],
                    Date=datetime.strptime(data['Date'], '%Y-%m-%d').date(),
                    Company=data['Company'],
                    Item=data['Item'],
                    Type=data['Type'],
                    Size=size,
                    Conversion=data['Conversion'],
                    Total_Mc=total_mc,
                    Total_Kg=total_kg,
                    Freezing_Type=data['Freezing_Type']
                )
                db.session.add(entry)
            
            db.session.commit()
            return jsonify({"message": "Entries added successfully"}), 201

        elif request.method == 'PUT':
            data = request.json
            entry = db.session.get(ProcessingIn, data['ID'])
            if entry:
                entry.Sr_No = data['Sr_No']
                entry.Fi_No = data['Fi_No']
                entry.Date = datetime.strptime(data['Date'], '%Y-%m-%d').date()
                entry.Company = data['Company']
                entry.Item = data['Item']
                entry.Type = data['Type']
                entry.Size = data['Size']
                entry.Conversion = data['Conversion']
                entry.Total_Mc = data['Total_Mc']
                entry.Total_Kg = data['Total_Kg']
                entry.Freezing_Type = data['Freezing_Type']
                db.session.commit()
                return jsonify({"message": "Entry updated successfully"}), 200
            return jsonify({"message": "Entry not found"}), 404

        elif request.method == 'DELETE':
            data = request.json
            print(f"Received DELETE request with data: {data}")
            entry = db.session.get(ProcessingIn, data['ID'])
            if entry:
                db.session.delete(entry)
                db.session.commit()
                response = jsonify({"message": "Entry deleted successfully"})
                print(f"Returning response: {response.get_json()}")
                return response, 200
            response = jsonify({"message": "Entry not found"})
            print(f"Returning response: {response.get_json()}")
            return response, 404

    except Exception as e:
        response = jsonify({"message": str(e)})
        print(f"Returning response: {response.get_json()}")
        return response, 500

@app.route('/api/processing_in/<int:id>', methods=['GET'])
def get_processing_in_entry(id):
    entry = db.session.get(ProcessingIn, id)
    if entry:
        return jsonify(serialize_model(entry))
    return jsonify({"message": "Entry not found"}), 404

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
    unique_values = {}
    columns = ['Sr_No', 'Fi_No', 'Company', 'Item', 'Type', 'Size', 'Conversion', 'Freezing_Type']
    for column in columns:
        unique_values[column] = db.session.query(getattr(ColdStoreIn, column)).distinct().all()
        unique_values[column] = [value[0] for value in unique_values[column]]
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

    query = ColdStoreIn.query.filter(ColdStoreIn.Balance > 0)
    
    if start_date:
        query = query.filter(ColdStoreIn.Date >= start_date)
    
    if end_date:
        query = query.filter(ColdStoreIn.Date <= end_date)
    
    if sr_no:
        query = query.filter(ColdStoreIn.Sr_No == sr_no)
    
    if fi_no:
        query = query.filter(ColdStoreIn.Fi_No == fi_no)
    
    if company:
        query = query.filter(ColdStoreIn.Company == company)
    
    if item:
        query = query.filter(ColdStoreIn.Item == item)
    
    if type_:
        query = query.filter(ColdStoreIn.Type == type_)
    
    if size:
        query = query.filter(ColdStoreIn.Size == size)
    
    if conversion:
        query = query.filter(ColdStoreIn.Conversion == conversion)
    
    if freezing_type:
        query = query.filter(ColdStoreIn.Freezing_Type == freezing_type)
    
    data = query.all()
    return jsonify([serialize_model(entry) for entry in data])

@app.route('/export')
def export():
    return render_template('export.html')

@app.route('/api/export_in', methods=['GET', 'POST', 'PUT', 'DELETE'])
def export_in():
    if request.method == 'GET':
        data = ExportIn.query.all()
        return jsonify([serialize_model(entry) for entry in data])
    
    elif request.method == 'POST':
        try:
            data = request.json
            print("Received POST data:", data)  # Debugging statement
            entry = ExportIn(
                CSID=data['CSID'],
                Sr_No=data['Sr_No'],
                Fi_No=data['Fi_No'],
                Date=datetime.strptime(data['Date'], '%Y-%m-%d').date(),
                Ref_Date=datetime.strptime(data['Ref_Date'], '%d/%m/%Y').date(),  # Ensure date format is correct
                Company=data['Company'],
                Item=data['Item'],
                Type=data['Type'],
                Size=data['Size'],
                Conversion=data['Conversion'],
                Total_Days=data['Total_Days'],
                Total_Mc=data['Total_Mc'],
                Total_Kg=data['Total_Kg'],
                Freezing_Type=data['Freezing_Type']
            )
            db.session.add(entry)
            db.session.commit()

            # Recalculate Exported_kg for the corresponding ColdStoreIn entry
            update_exported_kg_for_csid(data['CSID'])

            return jsonify({"message": "Entry added successfully"}), 201
        except Exception as e:
            print("Error in POST /api/export_in:", str(e))  # Debugging statement
            return jsonify({"message": str(e)}), 500

    elif request.method == 'PUT':
        try:
            data = request.json
            entry = db.session.get(ExportIn, data['ID'])
            if entry:
                entry.CSID = data['CSID']
                entry.Sr_No = data['Sr_No']
                entry.Fi_No = data['Fi_No']
                entry.Date = datetime.strptime(data['Date'], '%Y-%m-%d').date()
                entry.Company = data['Company']
                entry.Item = data['Item']
                entry.Type = data['Type']
                entry.Size = data['Size']
                entry.Conversion = data['Conversion']
                entry.Total_Days = data['Total_Days']
                entry.Total_Mc = data['Total_Mc']
                entry.Total_Kg = data['Total_Kg']
                entry.Freezing_Type = data['Freezing_Type']
                db.session.commit()

                # Recalculate Exported_kg for the corresponding ColdStoreIn entry
                update_exported_kg_for_csid(data['CSID'])

                return jsonify({"message": "Entry updated successfully"}), 200
            return jsonify({"message": "Entry not found"}), 404
        except Exception as e:
            print("Error in PUT /api/export_in:", str(e))  # Debugging statement
            return jsonify({"message": str(e)}), 500

    elif request.method == 'DELETE':
        try:
            data = request.json
            entry = db.session.get(ExportIn, data['ID'])
            if entry:
                csid = entry.CSID
                db.session.delete(entry)
                db.session.commit()

                # Recalculate Exported_kg for the corresponding ColdStoreIn entry
                update_exported_kg_for_csid(csid)

                return jsonify({"message": "Entry deleted successfully"}), 200
            return jsonify({"message": "Entry not found"}), 404
        except Exception as e:
            print("Error in DELETE /api/export_in:", str(e))  # Debugging statement
            return jsonify({"message": str(e)}), 500

def update_exported_kg_for_csid(csid):
    """Recalculate Exported_kg and Balance for a given CSID."""
    total_kg = db.session.query(
        db.func.sum(ExportIn.Total_Kg)
    ).filter(ExportIn.CSID == csid).scalar() or 0

    cold_store_entry = ColdStoreIn.query.get(csid)
    if cold_store_entry:
        cold_store_entry.Exported_kg = total_kg
        cold_store_entry.Balance = (cold_store_entry.Total_Kg or 0) - total_kg
        db.session.commit()

@app.route('/api/export_in/<int:id>', methods=['GET'])
def get_export_in_entry(id):
    entry = ExportIn.query.get(id)
    if entry:
        return jsonify(serialize_model(entry))
    return jsonify({"message": "Entry not found"}), 404

@app.route('/api/download_epexcel', methods=['POST'])
def download_epexcel():
    try:
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
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/update_processing_mc', methods=['POST'])
def update_processing_mc():
    try:
        filters = request.json  # Expecting JSON with filter criteria
        company = filters.get('Company')
        date = filters.get('Date')

        # Fetch processing_in entries based on filters
        query = ProcessingIn.query
        if company:
            query = query.filter_by(Company=company)
        if date:
            query = query.filter_by(Date=datetime.strptime(date, '%Y-%m-%d').date())

        processing_entries = query.all()

        for processing_entry in processing_entries:
            # Find matching cold_store_in entries
            cold_store_entries = ColdStoreIn.query.filter_by(
                Date=processing_entry.Date,
                Company=processing_entry.Company,
                Item=processing_entry.Item,
                Size=processing_entry.Size,
                Conversion=processing_entry.Conversion,
                Freezing_Type=processing_entry.Freezing_Type
            ).all()

            for cold_store_entry in cold_store_entries:
                # Update Processing_mc
                cold_store_entry.Processing_mc = processing_entry.Total_Mc

        db.session.commit()
        return jsonify({"message": "Processing_mc updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/api/update_exported_kg', methods=['POST'])
def update_exported_kg():
    try:
        # Fetch total kg for each CSID from export_in
        total_kg_per_csid = db.session.query(
            ExportIn.CSID,
            db.func.sum(ExportIn.Total_Kg).label('TotalAmount')
        ).group_by(ExportIn.CSID).all()

        # Update Exported_kg in cold_store_in
        for csid, total_amount in total_kg_per_csid:
            ColdStoreIn.query.filter_by(ID=csid).update(
                {ColdStoreIn.Exported_kg: total_amount},
                synchronize_session="fetch"
            )

        # Update Balance in cold_store_in
        db.session.query(ColdStoreIn).update(
            {ColdStoreIn.Balance: ColdStoreIn.Total_kg - ColdStoreIn.Exported_kg},
            synchronize_session="fetch"
        )

        db.session.commit()
        return jsonify({"message": "Exported_kg updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/sync_data', methods=['POST'])
def sync_data():
    try:
        batch_size = 10000  # Adjust the batch size as needed

        # Step 1: Update Exported_kg in cold_store_in
        offset = 0
        while True:
            print(f"Processing batch for Exported_kg with offset {offset}")
            export_data = db.session.query(
                ExportIn.CSID,
                db.func.sum(ExportIn.Total_Kg).label('TotalAmount')
            ).group_by(ExportIn.CSID).offset(offset).limit(batch_size).all()

            if not export_data:
                break

            for data in export_data:
                cold_store_entry = ColdStoreIn.query.get(data.CSID)
                if cold_store_entry:
                    cold_store_entry.Exported_kg = data.TotalAmount

            db.session.commit()
            offset += batch_size

        # Step 2: Update Balance in cold_store_in
        offset = 0
        while True:
            print(f"Processing batch for Balance with offset {offset}")
            cold_store_entries = ColdStoreIn.query.offset(offset).limit(batch_size).all()
            if not cold_store_entries:
                break

            for entry in cold_store_entries:
                entry.Balance = (entry.Total_Kg or 0) - (entry.Exported_kg or 0)

            db.session.commit()
            offset += batch_size

        # Step 3: Update Processing_mc in cold_store_in
        offset = 0
        while True:
            print(f"Processing batch for Processing_mc with offset {offset}")
            processing_entries = ProcessingIn.query.offset(offset).limit(batch_size).all()
            if not processing_entries:
                break

            for processing_entry in processing_entries:
                cold_store_entries = ColdStoreIn.query.filter_by(
                    Date=processing_entry.Date,
                    Company=processing_entry.Company,
                    Item=processing_entry.Item,
                    Size=processing_entry.Size,
                    Conversion=processing_entry.Conversion
                ).all()

                for cold_store_entry in cold_store_entries:
                    cold_store_entry.Processing_mc = processing_entry.Total_Kg

            db.session.commit()
            offset += batch_size

        return jsonify({"message": "Data synchronized successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error during sync_data: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    serve(app, host='192.168.0.88', port=8088, threads=6)