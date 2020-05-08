import numpy as np
from datetime import datetime, timedelta
from .models import MoistureModel, PumpModel


def build_xlabels(start, end):
    result = []
    delta = timedelta(minutes=5)

    while (start < end):
        result.append(start.strftime('%H%M'))
        start = start + delta

    print(result)
    return result
    # return result[::-1]


def get_pump_data(start_time, end_time, interval_minutes=5):
    pump_on = PumpModel.query.filter(PumpModel.timestamp > start_time).filter(PumpModel.state == True).all()
    pump_off = PumpModel.query.filter(PumpModel.timestamp > start_time).filter(PumpModel.state == False).all()

    result = []

    delta = timedelta(minutes=5)
    pump_graph_val = 0

    on_idx = 0
    off_idx = 0
    while (start_time < end_time):
        if (len(pump_on) and pump_on[on_idx].timestamp <= start_time):
            on_idx = on_idx + 1
            pump_graph_val = 100
        elif (len(pump_off) and pump_off[off_idx].timestamp < start_time):
            off_idx = off_idx + 1
            pump_graph_val = 0
        
        result.append(pump_graph_val)
        start_time = start_time + delta

    print(result)
    return result


def get_moisture_data(start, end):
    result = []
    delta = timedelta(minutes=5)

    m_idx = 0
    moistures = MoistureModel.query.filter(MoistureModel.timestamp > start).all()
    while start < end:
        if len(moistures) and moistures[m_idx].timestamp < start:
            result.append(moistures[m_idx].moisture/1024*100)
            m_idx = m_idx + 1
        else:
            result.append(0)
        start = start + delta

    print(result)
    return result


def fetch_chart_data(hours):
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)

    moisture_data = get_moisture_data(start, end)
    pump_data = get_pump_data(start, end)
    xLabels = build_xlabels(start, end)
    print(xLabels)

    return {
        "pump": {
            "legend": "Water Pump On",
            "data": pump_data
        },
        "moisture": {
            "legend": "Moisture Level",
            "data": moisture_data
        },
        "xLabels": xLabels,
        "xAxisLabel": "24 hour time",
        "yAxisLabel": "Moisture Percentage"
    }
