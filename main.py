import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit, QFormLayout, QTabWidget, QTextEdit, QComboBox, QDateEdit, QHeaderView, QListWidget, QSlider, QListWidgetItem, QTabBar
)
from PyQt6.QtCore import Qt, QDate, QTimer, QPoint
from database import db, app as flask_app
from modules.vehicle_management import Vehicle, MaintenanceRecord, SparePart, FuelRecord, OwnershipHistory, User
from modules.dispatch import Driver, Route
from modules.monitoring import TrackingData
from modules.analytics import Analytics
from datetime import datetime
from PyQt6.QtWebEngineWidgets import QWebEngineView
import json
import random
import requests
import bcrypt
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

CITY_COORDS = {
    "Москва": (55.7558, 37.6176),
    "Санкт-Петербург": (59.9343, 30.3351),
    "Казань": (55.7963, 49.1088),
    "Новосибирск": (55.0084, 82.9357),
    "Екатеринбург": (56.8389, 60.6057),
    "Нижний Новгород": (56.2965, 43.9361),
    "Тула": (54.1931, 37.6177),
    "Воронеж": (51.6615, 39.2003),
    "Самара": (53.1959, 50.1008),
    "Ростов-на-Дону": (47.2357, 39.7015),
}

def autofill_route_coords(data):
    for prefix, city_field in [("start", "start_location"), ("end", "end_location")]:
        city = data.get(city_field, "")
        lat_field = f"{prefix}_lat"
        lon_field = f"{prefix}_lon"
        if not data.get(lat_field) or not data.get(lon_field):
            coords = CITY_COORDS.get(city)
            if coords:
                data[lat_field], data[lon_field] = coords
            else:
                data[lat_field], data[lon_field] = 55.0, 37.0
    return data


class GenericDialog(QDialog):
    def __init__(self, fields, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Данные')
        self.layout = QFormLayout(self)
        self.inputs = {}
        for field in fields:
            label = QLabel(field)
            edit = QLineEdit()
            self.layout.addRow(label, edit)
            self.inputs[field] = edit
        if data:
            for k, v in data.items():
                if k in self.inputs:
                    self.inputs[k].setText(str(v) if v is not None else "")
        self.btn_ok = QPushButton('OK')
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addRow(self.btn_ok)
    def get_data(self):
        return {k: v.text() for k, v in self.inputs.items()}


class TableWidget(QWidget):
    def __init__(self, model, fields, headers, pk='id', parent=None):
        super().__init__(parent)
        self.model = model
        self.fields = fields
        self.headers = headers
        self.pk = pk
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)
 
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton('Добавить')
        self.btn_edit = QPushButton('Изменить')
        self.btn_delete = QPushButton('Удалить')
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        self.layout.addLayout(btn_layout)
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_delete.clicked.connect(self.delete_item)
        self.refresh_table()
    def refresh_table(self):

        selected_row = self.table.currentRow()
        selected_pk = None
        if selected_row >= 0:
            selected_pk = self.table.item(selected_row, 0).text()
        with flask_app.app_context():
            items = self.model.query.order_by(getattr(self.model, self.pk)).all()
            self.table.setRowCount(len(items))
            self.table.setColumnCount(len(self.fields))
            self.table.setHorizontalHeaderLabels(self.headers)
            for row, item in enumerate(items):
                for col, field in enumerate(self.fields):
                    value = getattr(item, field, "")
                    self.table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))

        if selected_pk is not None:
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == selected_pk:
                    self.table.selectRow(row)
                    break
    def add_item(self):
        dialog = GenericDialog(self.fields, parent=self)
        if dialog.exec():
            data = dialog.get_data()
  
            if self.model.__name__ == "Route":
                data = autofill_route_coords(data)
            with flask_app.app_context():
                obj = self.model(**self._convert_types(data))
                db.session.add(obj)
                db.session.commit()
            self.refresh_table()
    def edit_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для редактирования')
            return
        pk_value = self.table.item(row, 0).text()
        with flask_app.app_context():
            obj = self.model.query.filter(getattr(self.model, self.pk)==pk_value).first()
            data = {f: getattr(obj, f, "") for f in self.fields}
            dialog = GenericDialog(self.fields, data, self)
            if dialog.exec():
                new_data = dialog.get_data()
   
                if self.model.__name__ == "Route":
                    new_data = autofill_route_coords(new_data)
                for k, v in self._convert_types(new_data).items():
                    setattr(obj, k, v)
                db.session.commit()
            self.refresh_table()
    def delete_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите запись для удаления')
            return
        pk_value = self.table.item(row, 0).text()
        with flask_app.app_context():
            obj = self.model.query.filter(getattr(self.model, self.pk)==pk_value).first()
            if obj:
                db.session.delete(obj)
                db.session.commit()
        self.refresh_table()
    def _convert_types(self, data):

        result = {}
        for k, v in data.items():
            if v == "":
                result[k] = None
                continue
            attr = getattr(self.model, k, None)
            if attr is not None and hasattr(attr.type, 'python_type'):
                typ = attr.type.python_type
                try:
                    result[k] = typ(v)
                except Exception:
                    result[k] = v
            else:
                result[k] = v
        return result

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
    
        self.vehicle_box = QComboBox()
        self.refresh_vehicles()
        layout.addWidget(QLabel('Выберите ТС:'))
        layout.addWidget(self.vehicle_box)
    
        date_layout = QHBoxLayout()
        date_layout.setSpacing(16)  
        date_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter) 

        label_from = QLabel('C:')
        label_from.setMinimumWidth(20)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setFixedWidth(130)

        label_to = QLabel('По:')
        label_to.setMinimumWidth(25)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedWidth(130)

        date_layout.addWidget(label_from)
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(label_to)
        date_layout.addWidget(self.end_date)
        layout.addLayout(date_layout)
     
        btn_layout = QHBoxLayout()
        self.btn_cost = QPushButton('Себестоимость перевозок')
        self.btn_eff = QPushButton('Эффективность использования')
        self.btn_report = QPushButton('Отчет по топливу')
        self.btn_forecast = QPushButton('Прогноз ТО')
        self.btn_fuel_avg = QPushButton('Средний расход топлива (л/100км)')
        self.btn_failure_prob = QPushButton('Вероятность поломки (30 дней)')
        self.btn_fuel_plot = QPushButton('График расхода топлива')
        btn_layout.addWidget(self.btn_cost)
        btn_layout.addWidget(self.btn_eff)
        btn_layout.addWidget(self.btn_report)
        btn_layout.addWidget(self.btn_forecast)
        btn_layout.addWidget(self.btn_fuel_avg)
        btn_layout.addWidget(self.btn_failure_prob)
        btn_layout.addWidget(self.btn_fuel_plot)
        layout.addLayout(btn_layout)
       
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
     
        self.btn_cost.clicked.connect(self.show_cost)
        self.btn_eff.clicked.connect(self.show_efficiency)
        self.btn_report.clicked.connect(self.show_report)
        self.btn_forecast.clicked.connect(self.show_forecast)
        self.btn_fuel_avg.clicked.connect(self.show_fuel_avg)
        self.btn_failure_prob.clicked.connect(self.show_failure_prob)
        self.btn_fuel_plot.clicked.connect(self.show_fuel_plot)

    def refresh_vehicles(self):
        self.vehicle_box.clear()
        with flask_app.app_context():
            vehicles = Vehicle.query.all()
            for v in vehicles:
                self.vehicle_box.addItem(f"{v.id}: {v.registration_number}", v.id)

    def get_selected_vehicle_id(self):
        return self.vehicle_box.currentData()

    def get_dates(self):
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        return start, end

    def show_cost(self):
        vid = self.get_selected_vehicle_id()
        start, end = self.get_dates()
        with flask_app.app_context():
            res = Analytics.calculate_transportation_cost(vid, start, end)
        self.result.setText(f"Себестоимость перевозок (ТС {vid}):\nТопливо: {res['fuel_cost']}\nОбслуживание: {res['maintenance_cost']}\nИтого: {res['total_cost']}")

    def show_efficiency(self):
        vid = self.get_selected_vehicle_id()
        start, end = self.get_dates()
        with flask_app.app_context():
            res = Analytics.analyze_vehicle_efficiency(vid, start, end)
        self.result.setText(f"Эффективность использования (ТС {vid}):\nПробег: {res['total_distance']} км\nВремя: {res['total_time']} мин\nСредний расход: {res['average_fuel_consumption']} л/100км\nВыполнено задач: {res['tasks_completed']}")

    def show_report(self):
        start, end = self.get_dates()
        with flask_app.app_context():
            rows = Analytics.generate_regulatory_report('fuel', start, end)
        text = 'Отчет по топливу:\n'
        for row in rows:
            text += f"ТС: {row[0]}, Всего топлива: {row[1]}, Сумма: {row[2]}\n"
        self.result.setText(text)

    def show_forecast(self):
        vid = self.get_selected_vehicle_id()
        with flask_app.app_context():
            res = Analytics.predict_maintenance_needs(vid)
        if res:
            self.result.setText(f"Последнее ТО: {res['last_maintenance']}\nСледующее ТО: {res['predicted_next_maintenance']}\nДней до ТО: {res['days_until_maintenance']}")
        else:
            self.result.setText("Нет данных для прогноза.")

    def show_fuel_avg(self):
        vid = self.get_selected_vehicle_id()
        start, end = self.get_dates()
        with flask_app.app_context():
            res = Analytics.calculate_fuel_consumption_per_100km(vid, start, end)
        if res:
            self.result.setText(f"Средний расход топлива: {res['avg_consumption_per_100km']:.2f} л/100км\nОбщий пробег: {res['total_distance']:.1f} км\nИзрасходовано топлива: {res['total_fuel']:.1f} л")
        else:
            self.result.setText('Недостаточно данных для расчёта расхода топлива!')

    def show_failure_prob(self):
        vid = self.get_selected_vehicle_id()
        with flask_app.app_context():
            prob = Analytics.failure_probability(vid, horizon_days=30)
        if prob is not None:
            self.result.setText(f"Вероятность поломки в ближайшие 30 дней: {prob*100:.1f}%")
        else:
            self.result.setText('Недостаточно данных для оценки вероятности поломки!')

    def show_fuel_plot(self):
        vid = self.get_selected_vehicle_id()
        with flask_app.app_context():
            records = FuelRecord.query.filter(
                FuelRecord.vehicle_id == vid
            ).order_by(FuelRecord.date).all()
        if len(records) < 2:
            self.result.setText('Недостаточно данных для построения графика!')
            return
        dates = []
        consumptions = []
        prev_mileage = None
        prev_date = None
        prev_amount = None
        for rec in records:
            if rec.mileage is not None and rec.amount is not None:
                if prev_mileage is not None and rec.mileage > prev_mileage:
                    distance = rec.mileage - prev_mileage
                    if distance > 0:
                        consumption = (prev_amount / distance) * 100
                        dates.append(rec.date)
                        consumptions.append(consumption)
                prev_mileage = rec.mileage
                prev_date = rec.date
                prev_amount = rec.amount
        if not dates:
            self.result.setText('Недостаточно данных для построения графика!')
            return
        fig, ax = plt.subplots()
        ax.plot(dates, consumptions, marker='o', linestyle='-')
        ax.set_title('Расход топлива (л/100км)')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Расход (л/100км)')
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.show()

class MapSimulationWidget(QWidget):
    def refresh_vehicles_and_routes(self):
        for _, label, combo in self.vehicle_route_widgets:
            label.deleteLater()
            combo.deleteLater()
        self.vehicle_route_widgets.clear()
        self.vehicle_route_map.clear()
        self.vehicles = []
        self.routes = []
        with flask_app.app_context():
            self.vehicles = Vehicle.query.all()
            self.routes = Route.query.all()
        for v in self.vehicles:
            hbox = QHBoxLayout()
            icon = "🚗" if (v.vehicle_type or '').lower() in ["легковой", "car"] else ("🚌" if (v.vehicle_type or '').lower() in ["автобус", "bus"] else "🚚")
            label = QLabel(f"{icon} <b>{v.registration_number}</b>")
            label.setStyleSheet('font-size: 16px; min-width: 120px;')
            combo = QComboBox()
            for r in self.routes:
                combo.addItem(f"{r.id}: {r.start_location} → {r.end_location}", r.id)
            if self.routes:
                self.vehicle_route_map[v.id] = self.routes[0].id
            combo.currentIndexChanged.connect(lambda idx, vid=v.id, c=combo: self.on_route_selected(vid, c))
            combo.setStyleSheet('min-width: 220px;')
            hbox.addWidget(label)
            hbox.addWidget(combo)
            hbox.addStretch(1)
            self.vehicle_route_layout.addLayout(hbox)
            self.vehicle_route_widgets.append((v.id, label, combo))
        for v in self.vehicles:
            if v.id not in self.vehicle_route_map and self.routes:
                self.vehicle_route_map[v.id] = self.routes[0].id

    def load_empty_map(self):
        html = self.generate_map_html({}, {}, 5)
        self.webview.setHtml(html)

    def get_vehicle_route_pairs(self):
        return [(vid, self.vehicle_route_map[vid]) for vid, _, _ in self.vehicle_route_widgets]

    def on_route_selected(self, vehicle_id, combo):
        route_id = combo.currentData()
        self.vehicle_route_map[vehicle_id] = route_id

    def update_legend(self):
        colors = ['#e53935', '#1e88e5', '#43a047', '#fbc02d', '#8e24aa', '#00897b', '#6d4c41', '#3949ab', '#d81b60', '#00acc1']
        legend_html = '<b>Маршрут:</b> '
        for idx, (vid, _, _) in enumerate(self.vehicle_route_widgets):
            v = next((v for v in self.vehicles if v.id == vid), None)
            if not v: continue
            icon = "🚗" if (v.vehicle_type or '').lower() in ["легковой", "car"] else ("🚌" if (v.vehicle_type or '').lower() in ["автобус", "bus"] else "🚚")
            legend_html += f'<span style="color:{colors[idx%len(colors)]}; font-size:18px; margin-right:12px;">{icon} {v.registration_number}</span>'
        self.legend.setText(legend_html)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.osrm_cache = {}  
        
        self.vehicle_route_widgets = []  
        self.vehicle_route_map = {}    
        self.vehicles = []
        self.routes = []
        self.vehicle_route_layout = QVBoxLayout()
        scroll_btn_layout = QHBoxLayout()
        self.btn_scroll_up = QPushButton('▲')
        self.btn_scroll_down = QPushButton('▼')
        scroll_btn_layout.addWidget(self.btn_scroll_up)
        scroll_btn_layout.addWidget(self.btn_scroll_down)
        layout.addLayout(scroll_btn_layout)
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(60)
        self._scroll_direction = 0
        self.btn_scroll_up.pressed.connect(lambda: self._start_scroll(-1))
        self.btn_scroll_down.pressed.connect(lambda: self._start_scroll(1))
        self.btn_scroll_up.released.connect(self._stop_scroll)
        self.btn_scroll_down.released.connect(self._stop_scroll)
        self._scroll_timer.timeout.connect(self._do_scroll)
        self.refresh_vehicles_and_routes()
        group_box = QWidget()
        group_box.setLayout(self.vehicle_route_layout)
        group_box.setStyleSheet('background: #232323; border-radius: 8px; padding: 12px;')
        layout.addWidget(QLabel('<b>Выберите маршрут для каждого ТС:</b>'))
        layout.addWidget(group_box)

        btn_layout = QHBoxLayout()
        self.btn_generate = QPushButton('Сгенерировать треки')
        self.btn_start = QPushButton('Старт симуляции')
        self.btn_pause = QPushButton('Пауза/Продолжить')
        self.btn_clear = QPushButton('Очистить треки')
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_clear)
        layout.addLayout(btn_layout)
   
        self.legend = QLabel()
        self.legend.setStyleSheet('background: #232323; color: #fff; border-radius: 8px; padding: 8px; font-size: 13px;')
        layout.addWidget(self.legend)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel('Скорость анимации:'))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)
        layout.addLayout(speed_layout)
        self.webview = QWebEngineView()
        layout.addWidget(self.webview, stretch=1)
        self.btn_start.clicked.connect(self.start_simulation)
        self.btn_generate.clicked.connect(self.generate_tracks)
        self.btn_clear.clicked.connect(self.clear_tracks)
        self.btn_pause.clicked.connect(self.pause_resume_simulation)
        self.setMinimumHeight(500)
        self.setMinimumWidth(900)
        self.load_empty_map()

    def clear_tracks(self):
        with flask_app.app_context():
            TrackingData.query.delete()
            db.session.commit()
        self.load_empty_map()

    def get_osrm_route_points(self, start, end):
        key = (round(start[0], 5), round(start[1], 5), round(end[0], 5), round(end[1], 5))
        if key in self.osrm_cache:
            return self.osrm_cache[key]
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get('routes') and data['routes'][0]['geometry']['coordinates']:
                points = [(lat, lon) for lon, lat in data['routes'][0]['geometry']['coordinates']]
                self.osrm_cache[key] = points
                return points
            else:
                QMessageBox.warning(self, 'Ошибка OSRM', 'Не удалось построить маршрут по дорогам. Будет использована прямая линия.')
        except Exception as e:
            print(f"OSRM error: {e}")
            QMessageBox.warning(self, 'Ошибка OSRM', f'Ошибка при обращении к OSRM: {e}\nБудет использована прямая линия.')
        return None

    def generate_tracks(self):
        print('=== НАЧАЛО ГЕНЕРАЦИИ ТРЕКОВ ===')
   
        self.refresh_vehicles_and_routes()
        route_ids = [r.id for r in self.routes]
        num_routes = len(route_ids)
        for idx, (vid, label, combo) in enumerate(self.vehicle_route_widgets):
            if combo.count() > 0 and num_routes > 0:
                route_idx = idx % num_routes
                combo.setCurrentIndex(route_idx)
                self.vehicle_route_map[vid] = combo.itemData(route_idx)
        pairs = self.get_vehicle_route_pairs()
        if not pairs:
            print("Нет доступных пар ТС-маршрут!")
            QMessageBox.warning(self, 'Нет данных', 'Нет доступных пар ТС и маршрутов!')
            return
        success_count = 0
        fail_count = 0
        with flask_app.app_context():
            for vid, route_id in pairs:
                try:
                    route = Route.query.filter_by(id=route_id).first()
                    if not route:
                        print(f"Маршрут с id={route_id} не найден!")
                        fail_count += 1
                        continue
                    start = [route.start_lat, route.start_lon] if route.start_lat and route.start_lon else [55.7558, 37.6176]
                    end = [route.end_lat, route.end_lon] if route.end_lat and route.end_lon else [59.9343, 30.3351]
                    points = self.get_osrm_route_points(start, end)
                    if points and len(points) >= 2:
         
                        if len(points) > 100:
                            step = max(1, len(points)//100)
                            points = points[::step]
                        status = f'OSRM: {len(points)} точек.'
                    else:
                        steps = 40
                        points = [(
                            start[0] + (end[0] - start[0]) * i / steps,
                            start[1] + (end[1] - start[1]) * i / steps
                        ) for i in range(steps+1)]
                        if len(points) < 2:
                            status = 'Ошибка: не удалось сгенерировать маршрут.'
                            fail_count += 1
                            print(f'[FAIL] ТС {vid}, маршрут {route_id}: {status}')
                            continue
                        else:
                            status = f'Fallback: {len(points)} точек.'
                    TrackingData.query.filter_by(vehicle_id=vid, route_id=route_id).delete()
                    for lat, lon in points:
                        td = TrackingData(vehicle_id=vid, route_id=route_id, latitude=lat, longitude=lon, timestamp=datetime.now())
                        db.session.add(td)
                    success_count += 1
                    print(f'[OK] ТС {vid}, маршрут {route_id}: {status}')
                except Exception as e:
                    print(f'[ERROR] ТС {vid}, маршрут {route_id}: {e}')
                    fail_count += 1
            db.session.commit()
        with flask_app.app_context():
            total_tracks = TrackingData.query.count()
            print(f'=== КОНЕЦ ГЕНЕРАЦИИ ТРЕКОВ ===\nВсего треков в базе: {total_tracks}')
        self.update_legend()
        self.load_empty_map()
        if success_count == 0 or total_tracks == 0:
            print('Не удалось сгенерировать ни одного трека!')
            QMessageBox.critical(self, 'Ошибка генерации', 'Не удалось сгенерировать ни одного маршрута. Проверьте соединение с OSRM и попробуйте снова.')
        else:
            QMessageBox.information(self, 'Генерация треков', f'Успешно сгенерировано: {success_count}, ошибок: {fail_count}. В базе треков: {total_tracks}')

    def start_simulation(self):
        pairs = self.get_vehicle_route_pairs()
        if not pairs:
            QMessageBox.warning(self, 'Нет данных', 'Выберите хотя бы одну пару ТС и маршрут!')
            self.load_empty_map()
            return
        with flask_app.app_context():
   
            need_generate = False
            for vid, route_id in pairs:
                count = TrackingData.query.filter_by(vehicle_id=vid, route_id=route_id).count()
                if count < 2:
                    need_generate = True
                    break
            if need_generate:
                self.generate_tracks()
       
                for vid, route_id in pairs:
                    count = TrackingData.query.filter_by(vehicle_id=vid, route_id=route_id).count()
                    if count < 2:
                        QMessageBox.critical(self, 'Ошибка симуляции', f'Не удалось сгенерировать маршрут для ТС {vid}, маршрут {route_id}. Симуляция не будет запущена.')
                        self.load_empty_map()
                        return

        tracks = {}
        meta = {}
        bounds = []
        with flask_app.app_context():
            vehicles_dict = {v.id: (v.registration_number, v.vehicle_type) for v in self.vehicles}
            for vid, route_id in pairs:
                points = TrackingData.query.filter_by(vehicle_id=vid, route_id=route_id).order_by(TrackingData.timestamp).all()
                filtered_points = [p for p in points if p.latitude and p.longitude]
                if filtered_points and len(filtered_points) > 1:
                    key = f"{vid}_{route_id}"
                    tracks[key] = [[p.latitude, p.longitude] for p in filtered_points]
                    regnum, vtype = vehicles_dict.get(vid, (str(vid), ''))
                    emoji = "🚗" if (vtype or '').lower() in ["легковой", "car"] else ("🚌" if (vtype or '').lower() in ["автобус", "bus"] else "🚚")
                    meta[key] = [{
                        'lat': p.latitude,
                        'lon': p.longitude,
                        'speed': p.speed,
                        'timestamp': p.timestamp.strftime('%Y-%m-%d %H:%M:%S') if p.timestamp else '',
                        'fuel': p.fuel_level,
                        'regnum': regnum,
                        'emoji': emoji,
                        'route_id': route_id
                    } for p in filtered_points]
                    bounds += tracks[key]
        if not tracks:
            QMessageBox.critical(self, 'Ошибка симуляции', 'Нет сгенерированных треков для выбранных пар. Симуляция не будет запущена!')
            self.load_empty_map()
            return
        html = self.generate_map_html(tracks, meta, self.speed_slider.value(), bounds)
        self.webview.setHtml(html)
        QMessageBox.information(self, 'Симуляция', f'Симуляция успешно запущена! Активных маршрутов: {len(tracks)}')

    def generate_map_html(self, tracks, meta, speed=5, bounds=None):
        import os
        colors = ['#e53935', '#1e88e5', '#43a047', '#fbc02d', '#8e24aa', '#00897b', '#6d4c41', '#3949ab', '#d81b60', '#00acc1']
        js_tracks = json.dumps(tracks)
        js_colors = json.dumps(colors)
        js_meta = json.dumps(meta)
        js_bounds = json.dumps(bounds) if bounds else 'null'
    
        base_path = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
  
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <base href="file:///{base_path}/">
            <title>Карта маршрута</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://api-maps.yandex.ru/2.1/?apikey=e794f57e-44c6-4dc7-be6c-2be3b174868f&lang=ru_RU" type="text/javascript"></script>
            <style>
                #map {{ height: 100vh; width: 100%; }}
                #error {{ color: red; font-weight: bold; position: absolute; top: 10px; left: 10px; background: #fff; z-index: 9999; padding: 8px; border-radius: 6px; }}
                .ymaps-2-1-79-balloon__content {{ font-size: 15px; }}
                .legend-box {{ position: absolute; top: 10px; right: 10px; background: #232323cc; color: #fff; border-radius: 8px; padding: 10px 18px; font-size: 15px; z-index: 9999; }}
            </style>
        </head>
        <body>
        <div id="error"></div>
        <div id="map"></div>
        <div class="legend-box" id="legend"></div>
        <script>
            window.onerror = function(msg, url, line, col, error) {{
                document.getElementById('error').innerText = 'JS ERROR: ' + msg + ' (line ' + line + ')';
            }};
            var tracks = {js_tracks};
            var colors = {js_colors};
            var meta = {js_meta};
            var bounds = {js_bounds};
            var map, keys, polylines, markers, maxLens, i = 0, animationTimer = null, SPEED = {int(600/speed)};
            var paused = false;
            window.togglePause = function() {{
                paused = !paused;
                if (!paused && animationTimer === null) animate();
            }};
            ymaps.ready(function() {{
                map = new ymaps.Map('map', {{center: [56.5, 34.5], zoom: 5}});
                if (bounds && bounds.length > 0) {{
                    var lats = bounds.map(function(pt) {{return pt[0];}});
                    var lons = bounds.map(function(pt) {{return pt[1];}});
                    var minLat = Math.min.apply(null, lats);
                    var maxLat = Math.max.apply(null, lats);
                    var minLon = Math.min.apply(null, lons);
                    var maxLon = Math.max.apply(null, lons);
                    map.setBounds([[minLat, minLon], [maxLat, maxLon]], {{checkZoomRange:true, zoomMargin:40}});
                }}
                keys = Object.keys(tracks);
                document.getElementById('error').innerText = 'ТС-маршрутов: ' + keys.length;

                var legendHtml = '<b>Маршрут:</b> ';
                if (keys.length > 0) {{
                    for (var k=0; k<keys.length; k++) {{
                        var info = meta[keys[k]][0];
                        legendHtml += '<span style="color:' + colors[k%colors.length] + '; font-size:20px; margin-right:12px;">' + info.emoji + ' ' + info.regnum + '</span>';
                    }}
                }} else {{
                    legendHtml += '<span style="color:#aaa;">Нет активных маршрутов</span>';
                }}
                document.getElementById('legend').innerHTML = legendHtml;
                polylines = [];
                markers = [];
                maxLens = [];
                // Старт/финиш маркеры
                for (var k=0; k<keys.length; k++) {{
                    var key = keys[k];
                    var color = colors[k % colors.length];
                    var coords = tracks[key].map(function(pt) {{ return [pt[0], pt[1]]; }});
                    if (!coords || coords.length < 2) continue;
                    var poly = new ymaps.Polyline(coords, {{}}, {{strokeColor: color, strokeWidth: 5, opacity: 0.7}});
                    map.geoObjects.add(poly);
                    polylines.push(poly);
                    var info = meta[key][0];
      
                    var startMark = new ymaps.Placemark(coords[0], {{hintContent: 'Старт', balloonContent: 'Старт'}}, {{preset: 'islands#greenDotIcon'}});
                    map.geoObjects.add(startMark);
  
                    var endMark = new ymaps.Placemark(coords[coords.length-1], {{hintContent: 'Финиш', balloonContent: 'Финиш'}}, {{preset: 'islands#redDotIcon'}});
                    map.geoObjects.add(endMark);
                    // Маркер ТС (emoji в стандартном маркере)
                    var marker = new ymaps.Placemark(coords[0], {{
                        balloonContent: getTooltipHtml(info),
                        hintContent: info.emoji + ' ' + info.regnum,
                        iconContent: info.emoji
                    }}, {{
                        preset: 'islands#blueCircleIcon',
                        iconColor: color
                    }});
                    map.geoObjects.add(marker);
                    markers.push(marker);
   
                    maxLens.push(coords.length);
                }}
                function getTooltipHtml(info) {{
                    return `<b>ТС:</b> ${{info.emoji}} <b>${{info.regnum}}</b><br>` +
                           `<b>Координаты:</b> ${{info.lat.toFixed(5)}}, ${{info.lon.toFixed(5)}}<br>` +
                           (info.speed !== null && info.speed !== undefined ? `<b>Скорость:</b> ${{info.speed}} км/ч<br>` : '') +
                           (info.fuel !== null && info.fuel !== undefined ? `<b>Топливо:</b> ${{info.fuel}} л<br>` : '') +
                           (info.timestamp ? `<b>Время:</b> ${{info.timestamp}}` : '');
                }}
                // Глобальная анимация
                i = 0;
                if (animationTimer) clearTimeout(animationTimer);
                function animate() {{
                    if (paused) {{
                        animationTimer = null;
                        return;
                    }}
                    for (var k=0; k<markers.length; k++) {{
                        var coords = tracks[keys[k]];
                        var infos = meta[keys[k]];
                        if (coords && i < coords.length && infos && i < infos.length) {{
                            markers[k].geometry.setCoordinates([coords[i][0], coords[i][1]]);
                            var info = infos[i];
                            markers[k].properties.set('balloonContent', getTooltipHtml(info));
                            markers[k].properties.set('hintContent', info.emoji + ' ' + info.regnum);
                        }}
                    }}
                    i++;
                    if (i < Math.max.apply(null, maxLens)) {{
                        animationTimer = setTimeout(animate, SPEED);
                    }}
                    else {{
                        animationTimer = null;
                    }}
                }}
       
                map.events.add('boundschange', function (e) {{
   
                }});
                map.events.add('actionend', function (e) {{
 
                }});
                animate();
                window.animate = animate;
            }});
        </script>
        </body>
        </html>
        '''

    def pause_resume_simulation(self):

        self.webview.page().runJavaScript('window.togglePause && window.togglePause();')

    def _start_scroll(self, direction):
        self._scroll_direction = direction
        self._scroll_timer.start()

    def _stop_scroll(self):
        self._scroll_timer.stop()

    def _do_scroll(self):
   
        parent = self.vehicle_route_layout.parentWidget()
        scroll_area = None
  
        for child in parent.children():
            if hasattr(child, 'verticalScrollBar'):
                scroll_area = child
                break
        if scroll_area:
            bar = scroll_area.verticalScrollBar()
            bar.setValue(bar.value() + self._scroll_direction * 20)
        else:
  
            pass


class DraggableTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._last_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._last_pos is not None:
            delta = event.globalPosition().toPoint() - self._last_pos
            self._last_pos = event.globalPosition().toPoint()
      
            scroll = self.horizontalScrollBar() if hasattr(self, 'horizontalScrollBar') else None
            if scroll:
                scroll.setValue(scroll.value() - delta.x())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._last_pos = None
        super().mouseReleaseEvent(event)

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Авторизация')
        self.setFixedSize(300, 150)
        layout = QFormLayout(self)
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow('Логин:', self.username_edit)
        layout.addRow('Пароль:', self.password_edit)
        self.btn_login = QPushButton('Войти')
        self.btn_login.clicked.connect(self.accept)
        layout.addRow(self.btn_login)
    def get_credentials(self):
        return self.username_edit.text(), self.password_edit.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Автотранспорт - программный комплекс')
        self.setGeometry(100, 100, 1200, 700)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # Вкладки
        self.tabs.addTab(TableWidget(Vehicle, ['id','registration_number','brand','model','year','technical_specs','current_status','created_at','updated_at','vehicle_type'],
            ['ID','Рег. номер','Марка','Модель','Год','Тех. характеристики','Статус','Создан','Обновлен','Тип ТС']), "ТС")
        self.tabs.addTab(TableWidget(Driver, ['id','name','license_number','license_expiry','contact_info','status'],
            ['ID','Имя','Вод. удостоверение','Срок действия','Контакты','Статус']), "Водители")
        self.tabs.addTab(TableWidget(Route, ['id','vehicle_id','driver_id','start_location','end_location','distance','estimated_time','status','created_at','updated_at','start_lat','start_lon','end_lat','end_lon'],
            ['ID','ТС','Водитель','Откуда','Куда','Дистанция','Время','Статус','Создан','Обновлен','Широта нач.','Долгота нач.','Широта кон.','Долгота кон.']), "Маршруты")
        self.tabs.addTab(TableWidget(MaintenanceRecord, ['id','vehicle_id','maintenance_type','description','cost','date','next_maintenance_date','parts_used','created_at'],
            ['ID','ТС','Тип ТО','Описание','Стоимость','Дата','След. ТО','Запчасти','Создано']), "ТО")
        self.tabs.addTab(TableWidget(SparePart, ['id','name','part_number','quantity','min_quantity','cost','supplier','last_order_date'],
            ['ID','Название','Артикул','Кол-во','Мин. кол-во','Стоимость','Поставщик','Последний заказ']), "Запчасти")
        self.tabs.addTab(TableWidget(FuelRecord, ['id','vehicle_id','fuel_type','amount','cost','date','mileage'],
            ['ID','ТС','Тип топлива','Объем','Стоимость','Дата','Пробег']), "Заправки")
        self.tabs.addTab(TableWidget(OwnershipHistory, ['id','vehicle_id','owner_name','start_date','end_date','documents'],
            ['ID','ТС','Владелец','Начало','Конец','Документы']), "Владение ТС")
        self.tabs.addTab(TableWidget(TrackingData, ['id','vehicle_id','route_id','latitude','longitude','speed','fuel_level','timestamp','additional_data'],
            ['ID','ТС','Маршрут','Широта','Долгота','Скорость','Топливо','Время','Доп. данные']), "Мониторинг")
        self.tabs.addTab(AnalyticsWidget(), "Аналитика")
        self.tabs.addTab(MapSimulationWidget(), "Карта/Симуляция")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginDialog()
    while True:
        if login.exec() == QDialog.DialogCode.Accepted:
            username, password = login.get_credentials()
            with flask_app.app_context():
                user = User.query.filter_by(username=username).first()
                if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                    break
                else:
                    QMessageBox.warning(None, 'Ошибка', 'Неверный логин или пароль!')
        else:
            sys.exit()
            
    app.setStyleSheet('''
        QMainWindow {
            background: #1e1e1e;
        }
        QTabWidget::pane {
            border: none;
            background: #1e1e1e;
            border-radius: 8px;
        }
        QTabBar::tab {
            background: #2d2d2d;
            color: #b0b0b0;
            border-radius: 8px 8px 0 0;
            padding: 12px 24px;
            margin-right: 4px;
            font-size: 14px;
            min-width: 120px;
            border: none;
        }
        QTabBar::tab:selected {
            background: #3d3d3d;
            color: #ffffff;
            border-bottom: 2px solid #007acc;
        }
        QTabBar::tab:hover {
            background: #3d3d3d;
            color: #ffffff;
        }
        QWidget {
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 14px;
            color: #ffffff;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007acc, stop:1 #005999);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            margin: 4px 2px;
            min-width: 100px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0088e6, stop:1 #0066b3);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #005999, stop:1 #004080);
        }
        QTableWidget {
            background: #2d2d2d;
            border: 1px solid #3d3d3d;
            border-radius: 8px;
            gridline-color: #3d3d3d;
            color: #ffffff;
            selection-background-color: #007acc;
            selection-color: #ffffff;
        }
        QTableView {
            background: #2d2d2d;
            alternate-background-color: #232323;
        }
        QTableCornerButton::section {
            background: #2d2d2d;
            border: none;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #3d3d3d;
        }
        QTableWidget::item:selected {
            background: #007acc;
        }
        QHeaderView::section {
            background: #2d2d2d;
            color: #ffffff;
            border: none;
            border-bottom: 2px solid #3d3d3d;
            padding: 10px;
            font-weight: bold;
        }
        QHeaderView::section:vertical {
            background: #2d2d2d;
            color: #fff;
            border: none;
        }
        QLineEdit, QComboBox, QDateEdit, QTextEdit {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #007acc;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
            border: 1px solid #007acc;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        QDialog {
            background: #2d2d2d;
            border-radius: 12px;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        QScrollBar:vertical {
            border: none;
            background: #2d2d2d;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #3d3d3d;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #4d4d4d;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            border: none;
            background: #2d2d2d;
            height: 10px;
            margin: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #3d3d3d;
            min-width: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #4d4d4d;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QMessageBox {
            background: #2d2d2d;
        }
        QMessageBox QLabel {
            color: #ffffff;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
        QComboBox QAbstractItemView {
            background: #232323;
            color: #fff;
            selection-background-color: #007acc;
            selection-color: #fff;
            border: 1px solid #3d3d3d;
            outline: none;
        }
        QComboBox {
            background: #2d2d2d;
            color: #fff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            padding: 8px 12px;
        }
        QComboBox:focus {
            border: 1px solid #007acc;
        }
        QListWidget {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
            border-radius: 6px;
            selection-background-color: #007acc;
            selection-color: #ffffff;
        }
        QListWidget::item:selected {
            background: #007acc;
            color: #ffffff;
        }
    ''')
    # --- Запуск основного окна ---
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec()) 