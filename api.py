from flask import Flask, jsonify, request, abort
from database import db, app
from modules.vehicle_management import Vehicle, MaintenanceRecord, SparePart, FuelRecord, OwnershipHistory
from modules.dispatch import Driver, Route
from modules.monitoring import TrackingData

def model_to_dict(obj, fields):
    return {f: getattr(obj, f) for f in fields}

# --- VEHICLES ---
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([model_to_dict(v, ['id','registration_number','brand','model','year','technical_specs','current_status','created_at','updated_at']) for v in vehicles])

@app.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(model_to_dict(v, ['id','registration_number','brand','model','year','technical_specs','current_status','created_at','updated_at']))

@app.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    data = request.json
    v = Vehicle(**data)
    db.session.add(v)
    db.session.commit()
    return jsonify(model_to_dict(v, ['id','registration_number','brand','model','year','technical_specs','current_status','created_at','updated_at'])), 201

@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    data = request.json
    for k, val in data.items():
        setattr(v, k, val)
    db.session.commit()
    return jsonify(model_to_dict(v, ['id','registration_number','brand','model','year','technical_specs','current_status','created_at','updated_at']))

@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    v = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(v)
    db.session.commit()
    return '', 204

# --- Аналогично для других сущностей ---
# DRIVERS
@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([model_to_dict(d, ['id','name','license_number','license_expiry','contact_info','status']) for d in drivers])

@app.route('/api/drivers/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    d = Driver.query.get_or_404(driver_id)
    return jsonify(model_to_dict(d, ['id','name','license_number','license_expiry','contact_info','status']))

@app.route('/api/drivers', methods=['POST'])
def create_driver():
    data = request.json
    d = Driver(**data)
    db.session.add(d)
    db.session.commit()
    return jsonify(model_to_dict(d, ['id','name','license_number','license_expiry','contact_info','status'])), 201

@app.route('/api/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    d = Driver.query.get_or_404(driver_id)
    data = request.json
    for k, val in data.items():
        setattr(d, k, val)
    db.session.commit()
    return jsonify(model_to_dict(d, ['id','name','license_number','license_expiry','contact_info','status']))

@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    d = Driver.query.get_or_404(driver_id)
    db.session.delete(d)
    db.session.commit()
    return '', 204

# --- Корневая страница ---
@app.route('/')
def index():
    return '<h2>Справка по API: <a href="/api">/api</a></h2>'

# --- ROUTES ---
@app.route('/api/routes', methods=['GET'])
def get_routes():
    routes = Route.query.all()
    return jsonify([model_to_dict(r, ['id','vehicle_id','driver_id','start_location','end_location','distance','estimated_time','status','created_at','updated_at','start_lat','start_lon','end_lat','end_lon']) for r in routes])

@app.route('/api/routes/<int:route_id>', methods=['GET'])
def get_route(route_id):
    r = Route.query.get_or_404(route_id)
    return jsonify(model_to_dict(r, ['id','vehicle_id','driver_id','start_location','end_location','distance','estimated_time','status','created_at','updated_at','start_lat','start_lon','end_lat','end_lon']))

@app.route('/api/routes', methods=['POST'])
def create_route():
    data = request.json
    r = Route(**data)
    db.session.add(r)
    db.session.commit()
    return jsonify(model_to_dict(r, ['id','vehicle_id','driver_id','start_location','end_location','distance','estimated_time','status','created_at','updated_at','start_lat','start_lon','end_lat','end_lon'])), 201

@app.route('/api/routes/<int:route_id>', methods=['PUT'])
def update_route(route_id):
    r = Route.query.get_or_404(route_id)
    data = request.json
    for k, val in data.items():
        setattr(r, k, val)
    db.session.commit()
    return jsonify(model_to_dict(r, ['id','vehicle_id','driver_id','start_location','end_location','distance','estimated_time','status','created_at','updated_at','start_lat','start_lon','end_lat','end_lon']))

@app.route('/api/routes/<int:route_id>', methods=['DELETE'])
def delete_route(route_id):
    r = Route.query.get_or_404(route_id)
    db.session.delete(r)
    db.session.commit()
    return '', 204

# --- MAINTENANCE ---
@app.route('/api/maintenance', methods=['GET'])
def get_maintenance():
    records = MaintenanceRecord.query.all()
    return jsonify([model_to_dict(m, ['id','vehicle_id','maintenance_type','description','cost','date','next_maintenance_date','parts_used','created_at']) for m in records])

@app.route('/api/maintenance/<int:rec_id>', methods=['GET'])
def get_maintenance_rec(rec_id):
    m = MaintenanceRecord.query.get_or_404(rec_id)
    return jsonify(model_to_dict(m, ['id','vehicle_id','maintenance_type','description','cost','date','next_maintenance_date','parts_used','created_at']))

@app.route('/api/maintenance', methods=['POST'])
def create_maintenance():
    data = request.json
    m = MaintenanceRecord(**data)
    db.session.add(m)
    db.session.commit()
    return jsonify(model_to_dict(m, ['id','vehicle_id','maintenance_type','description','cost','date','next_maintenance_date','parts_used','created_at'])), 201

@app.route('/api/maintenance/<int:rec_id>', methods=['PUT'])
def update_maintenance(rec_id):
    m = MaintenanceRecord.query.get_or_404(rec_id)
    data = request.json
    for k, val in data.items():
        setattr(m, k, val)
    db.session.commit()
    return jsonify(model_to_dict(m, ['id','vehicle_id','maintenance_type','description','cost','date','next_maintenance_date','parts_used','created_at']))

@app.route('/api/maintenance/<int:rec_id>', methods=['DELETE'])
def delete_maintenance(rec_id):
    m = MaintenanceRecord.query.get_or_404(rec_id)
    db.session.delete(m)
    db.session.commit()
    return '', 204

# --- SPARE PARTS ---
@app.route('/api/spare_parts', methods=['GET'])
def get_spare_parts():
    parts = SparePart.query.all()
    return jsonify([model_to_dict(p, ['id','name','part_number','quantity','min_quantity','cost','supplier','last_order_date']) for p in parts])

@app.route('/api/spare_parts/<int:part_id>', methods=['GET'])
def get_spare_part(part_id):
    p = SparePart.query.get_or_404(part_id)
    return jsonify(model_to_dict(p, ['id','name','part_number','quantity','min_quantity','cost','supplier','last_order_date']))

@app.route('/api/spare_parts', methods=['POST'])
def create_spare_part():
    data = request.json
    p = SparePart(**data)
    db.session.add(p)
    db.session.commit()
    return jsonify(model_to_dict(p, ['id','name','part_number','quantity','min_quantity','cost','supplier','last_order_date'])), 201

@app.route('/api/spare_parts/<int:part_id>', methods=['PUT'])
def update_spare_part(part_id):
    p = SparePart.query.get_or_404(part_id)
    data = request.json
    for k, val in data.items():
        setattr(p, k, val)
    db.session.commit()
    return jsonify(model_to_dict(p, ['id','name','part_number','quantity','min_quantity','cost','supplier','last_order_date']))

@app.route('/api/spare_parts/<int:part_id>', methods=['DELETE'])
def delete_spare_part(part_id):
    p = SparePart.query.get_or_404(part_id)
    db.session.delete(p)
    db.session.commit()
    return '', 204

# --- FUEL RECORDS ---
@app.route('/api/fuel_records', methods=['GET'])
def get_fuel_records():
    records = FuelRecord.query.all()
    return jsonify([model_to_dict(f, ['id','vehicle_id','fuel_type','amount','cost','date','mileage']) for f in records])

@app.route('/api/fuel_records/<int:rec_id>', methods=['GET'])
def get_fuel_record(rec_id):
    f = FuelRecord.query.get_or_404(rec_id)
    return jsonify(model_to_dict(f, ['id','vehicle_id','fuel_type','amount','cost','date','mileage']))

@app.route('/api/fuel_records', methods=['POST'])
def create_fuel_record():
    data = request.json
    f = FuelRecord(**data)
    db.session.add(f)
    db.session.commit()
    return jsonify(model_to_dict(f, ['id','vehicle_id','fuel_type','amount','cost','date','mileage'])), 201

@app.route('/api/fuel_records/<int:rec_id>', methods=['PUT'])
def update_fuel_record(rec_id):
    f = FuelRecord.query.get_or_404(rec_id)
    data = request.json
    for k, val in data.items():
        setattr(f, k, val)
    db.session.commit()
    return jsonify(model_to_dict(f, ['id','vehicle_id','fuel_type','amount','cost','date','mileage']))

@app.route('/api/fuel_records/<int:rec_id>', methods=['DELETE'])
def delete_fuel_record(rec_id):
    f = FuelRecord.query.get_or_404(rec_id)
    db.session.delete(f)
    db.session.commit()
    return '', 204

# --- OWNERSHIP HISTORY ---
@app.route('/api/ownership_history', methods=['GET'])
def get_ownership_history():
    records = OwnershipHistory.query.all()
    return jsonify([model_to_dict(o, ['id','vehicle_id','owner_name','start_date','end_date','documents']) for o in records])

@app.route('/api/ownership_history/<int:rec_id>', methods=['GET'])
def get_ownership_record(rec_id):
    o = OwnershipHistory.query.get_or_404(rec_id)
    return jsonify(model_to_dict(o, ['id','vehicle_id','owner_name','start_date','end_date','documents']))

@app.route('/api/ownership_history', methods=['POST'])
def create_ownership_record():
    data = request.json
    o = OwnershipHistory(**data)
    db.session.add(o)
    db.session.commit()
    return jsonify(model_to_dict(o, ['id','vehicle_id','owner_name','start_date','end_date','documents'])), 201

@app.route('/api/ownership_history/<int:rec_id>', methods=['PUT'])
def update_ownership_record(rec_id):
    o = OwnershipHistory.query.get_or_404(rec_id)
    data = request.json
    for k, val in data.items():
        setattr(o, k, val)
    db.session.commit()
    return jsonify(model_to_dict(o, ['id','vehicle_id','owner_name','start_date','end_date','documents']))

@app.route('/api/ownership_history/<int:rec_id>', methods=['DELETE'])
def delete_ownership_record(rec_id):
    o = OwnershipHistory.query.get_or_404(rec_id)
    db.session.delete(o)
    db.session.commit()
    return '', 204

# --- TRACKING DATA ---
@app.route('/api/tracking_data', methods=['GET'])
def get_tracking_data():
    records = TrackingData.query.all()
    return jsonify([model_to_dict(t, ['id','vehicle_id','route_id','latitude','longitude','speed','fuel_level','timestamp','additional_data']) for t in records])

@app.route('/api/tracking_data/<int:rec_id>', methods=['GET'])
def get_tracking_record(rec_id):
    t = TrackingData.query.get_or_404(rec_id)
    return jsonify(model_to_dict(t, ['id','vehicle_id','route_id','latitude','longitude','speed','fuel_level','timestamp','additional_data']))

@app.route('/api/tracking_data', methods=['POST'])
def create_tracking_record():
    data = request.json
    t = TrackingData(**data)
    db.session.add(t)
    db.session.commit()
    return jsonify(model_to_dict(t, ['id','vehicle_id','route_id','latitude','longitude','speed','fuel_level','timestamp','additional_data'])), 201

@app.route('/api/tracking_data/<int:rec_id>', methods=['PUT'])
def update_tracking_record(rec_id):
    t = TrackingData.query.get_or_404(rec_id)
    data = request.json
    for k, val in data.items():
        setattr(t, k, val)
    db.session.commit()
    return jsonify(model_to_dict(t, ['id','vehicle_id','route_id','latitude','longitude','speed','fuel_level','timestamp','additional_data']))

@app.route('/api/tracking_data/<int:rec_id>', methods=['DELETE'])
def delete_tracking_record(rec_id):
    t = TrackingData.query.get_or_404(rec_id)
    db.session.delete(t)
    db.session.commit()
    return '', 204

@app.route('/api')
def api_help():
    return '''
    <html>
    <head><title>API автотранспорта — справка</title><style>
    body { background: #181818; color: #eee; font-family: Segoe UI, Arial, sans-serif; padding: 32px; }
    h1, h2 { color: #4fc3f7; }
    code, pre { background: #232323; color: #fff; border-radius: 6px; padding: 2px 6px; }
    .block { background: #232323; border-radius: 8px; padding: 16px; margin-bottom: 18px; }
    </style></head>
    <body>
    <h1>API автотранспорта — справка</h1>
    <div class="block">
    <b>Базовый адрес:</b> <code>http://localhost:5000/api/</code><br>
    <b>Доступные сущности:</b> vehicles, drivers<br>
    (можно добавить: routes, maintenance, spare_parts, fuel_records, vehicle_ownership, tracking_data)
    </div>
    <div class="block">
    <h2>Примеры запросов</h2>
    <b>Получить все ТС:</b><br>
    <code>GET /api/vehicles</code><br><br>
    <b>Получить ТС по id:</b><br>
    <code>GET /api/vehicles/1</code><br><br>
    <b>Добавить ТС:</b><br>
    <code>POST /api/vehicles</code><br>
    <pre>{
  "registration_number": "A123BC77",
  "brand": "ГАЗ",
  "model": "3302",
  "year": 2020,
  "technical_specs": "2.7 л, бензин",
  "current_status": "В эксплуатации"
}</pre>
    <b>Изменить ТС:</b><br>
    <code>PUT /api/vehicles/1</code><br>
    <pre>{ "brand": "ГАЗель Next", "year": 2021 }</pre>
    <b>Удалить ТС:</b><br>
    <code>DELETE /api/vehicles/1</code>
    </div>
    <div class="block">
    <h2>Водители</h2>
    <b>Получить всех:</b> <code>GET /api/drivers</code><br>
    <b>Добавить:</b> <code>POST /api/drivers</code><br>
    <pre>{
  "name": "Иван Иванов",
  "license_number": "77AA123456",
  "license_expiry": "2025-12-31T00:00:00",
  "contact_info": "+7 900 000 0011",
  "status": "Активен"
}</pre>
    <b>Изменить:</b> <code>PUT /api/drivers/1</code><br>
    <pre>{ "status": "Уволен" }</pre>
    <b>Удалить:</b> <code>DELETE /api/drivers/1</code>
    </div>
    <div class="block">
    <b>Ответы всегда в формате JSON.<br>
    Если объект не найден — 404.<br>
    Если успешно создан — 201, удалён — 204.<br>
    Для тестирования удобно использовать Postman, curl, httpie.</b>
    </div>
    </body></html>
    '''

if __name__ == '__main__':
    app.run(debug=True) 