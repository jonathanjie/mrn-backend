from datetime import timezone
import json
import requests

from dateutil.parser import parse

from core.enums import FuelType
from dcsreporting.models import DCSUploadedFile, DCSVoyage


KR_DCS_INGESTOR_LAMBDA = "https://5dsdmq7ckdifhehzjobr6bh7ru0remid.lambda-url.ap-southeast-1.on.aws/"

KR_DCS_FUEL_STRING_MAP = {
    FuelType.HFO: "HFO",
    FuelType.LSFO: "LFO",
    FuelType.MDO: "MDO",
    FuelType.MGO: "MGO",
    FuelType.LPG_PROPANE: "LPG (Propane)",
    FuelType.LPG_BUTANE: "LPG (Butane)",
    FuelType.METHANOL: "Methanol",
    FuelType.ETHANOL: "Ethanol",
    FuelType.LNG: "LNG",
}

KR_DCS_FUEL_COLUMN_MAP = {
    "rob_at_departure": "{fuel_oil} ROB at departure (MT)",
    "rob_at_arrival": "{fuel_oil} ROB at arrival (MT)",
    "at_berth_consumption": "At Berth {fuel_oil} Consumption (MT)",
    "net_consumption": "{fuel_oil} Consumption (MT)",
    "bunkering_before_arrival": "Bunkering before Arrival - Received Quantity: {fuel_oil}",
    "bunkering_after_arrival": "Bunkering after Arrival - Received Quantity: {fuel_oil}",
    "debunkering_before_arrival": "De-bunkering before Arrival - De-bunkered Quantity: {fuel_oil}",
    "debunkering_after_arrival": "De-bunkering after Arrival - De-bunkered Quantity: {fuel_oil}",
    "correction_consumption": "Fuel consumption: {fuel_oil}",
}

KR_DCS_FUEL_COLUMN_NO_SPACE = [
    "bunkering_before_arrival", "bunkering_after_arrival"]

def process_dcs_type_1_excel(
    dcs_file: DCSUploadedFile,
):
    fuel_options = dcs_file.ship.shipspecs.fuel_options

    filepath = {
        'filepath': dcs_file.s3_file_path,
    }
    response = requests.post(
        KR_DCS_INGESTOR_LAMBDA,
        json=filepath,
    )
    json_response = response.json()
    data = json_response['data']
    rows = json.loads(data)

    dcs_voyage_list = []
    for row in rows:
        voyage_num = row.pop('Voyage No.')
        departure_port = row.pop('Port code (DEPARTURE)')
        departure_date_string = row.pop('Departure Date (UTC)') + 'T' + row.pop('Departure time (UTC)')
        departure_date = parse(departure_date_string)
        departure_date = departure_date.replace(tzinfo=timezone.utc)
        dep_cargo_op_string = row.pop('Departure Cargo operation (YES/NO)')
        if dep_cargo_op_string.upper() == "YES":
            departure_cargo_operation = True
        else:
            departure_cargo_operation = False
        arrival_port = row.pop('Port code (ARRIVAL)')
        arrival_date_string = row.pop('Arrival Date (UTC)') + 'T' + row.pop('Arrival time (UTC)')
        arrival_date = parse(arrival_date_string)
        arrival_date = arrival_date.replace(tzinfo=timezone.utc)
        time_at_sea = row.pop('Time spent at sea (hours)')
        distance_travelled = row.pop('Distance travelled (nm)')
        time_idle_at_anchorage = row.pop(
            'Total idle spent time at anchorage (hours)')
        cargo_carried_passenger = row.pop('Cargo carried: Passenger')
        cargo_carried_weight_volume = row.pop(
            'Cargo carried: Weight or Volume')
        transport_work_passenger = row.pop('Transport Work: Passenger')
        transport_work_weight_volume = row.pop(
            'Transport Work: Weight or Volume')
        rob_at_departure = _process_fuel_columns(
            column_type='rob_at_departure',
            row=row,
            fuel_options=fuel_options,
        )
        rob_at_arrival = _process_fuel_columns(
            column_type='rob_at_arrival',
            row=row,
            fuel_options=fuel_options,
        )
        at_berth_consumption =_process_fuel_columns(
            column_type='at_berth_consumption',
            row=row,
            fuel_options=fuel_options,
        )
        net_consumption = _process_fuel_columns(
            column_type='net_consumption',
            row=row,
            fuel_options=fuel_options,
        )
        bunkering_before_arrival = _process_fuel_columns(
            column_type='bunkering_before_arrival',
            row=row,
            fuel_options=fuel_options,
        )
        bunkering_after_arrival = _process_fuel_columns(
            column_type='bunkering_after_arrival',
            row=row,
            fuel_options=fuel_options,
        )
        debunkering_before_arrival = _process_fuel_columns(
            column_type='debunkering_before_arrival',
            row=row,
            fuel_options=fuel_options,
        )
        debunkering_after_arrival = _process_fuel_columns(
            column_type='debunkering_after_arrival',
            row=row,
            fuel_options=fuel_options,
        )
        correction_time_at_sea = row.pop('Time spent at sea')
        correction_distance_travelled.pop('Distance travelled')
        correction_consumption = _process_fuel_columns(
            column_type='correction_consumption',
            row=row,
            fuel_options=fuel_options,
        )
        dcs_voyage = DCSVoyage(
            voyage_num,
            departure_port,
            departure_date,
            departure_cargo_operation,
            arrival_port,
            arrival_date,
            time_at_sea,
            distance_travelled,
            time_idle_at_anchorage,
            cargo_carried_passenger,
            cargo_carried_weight_volume,
            transport_work_passenger,
            transport_work_weight_volume,
            rob_at_departure,
            rob_at_arrival,
            at_berth_consumption,
            net_consumption,
            bunkering_before_arrival,
            bunkering_after_arrival,
            debunkering_before_arrival,
            debunkering_after_arrival,
            correction_time_at_sea,
            correction_distance_travelled,
            correction_consumption,
        )
        dcs_voyage_list.append(dcs_voyage)
    DCSVoyage.objects.bulk_create(dcs_voyage_list)

def _process_fuel_columns(
    column_type: str,
    row: dict,
    fuel_options: list,
):
    col_string = KR_DCS_FUEL_STRING_MAP.get(column_type)
    fuel_no_space = column_type in KR_DCS_FUEL_COLUMN_NO_SPACE
    fuel_data = {}
    for fuel_oil in fuel_options:
        fuel_oil_string = KR_DCS_FUEL_STRING_MAP.get(fuel_oil)
        if fuel_no_space:
            fuel_oil_string = fuel_oil_string.replace(" ", "")
        lookup_string = col_string.format(fuel_oil=fuel_oil_string)
        fuel_data[fuel_oil] = row.pop(lookup_string)
    return fuel_data


sample = {'Voyage No.': 0.3153154543,
          'Port code (DEPARTURE)': 0.4655006316,
          'Departure Date (UTC)': 0.158152309,
          'Departure time (UTC)': 0.8138101552,
          'Departure Cargo operation (YES/NO)': 0.5398547416,
          'Port code (ARRIVAL)': 0.2561654391,
          'Arrival Date (UTC)': 0.0694327938,
          'Arrival time (UTC)': 0.6331519475,
          'Arrival Cargo operation (YES/NO)': 0.513052133,
          'Time spent at sea (hours)': 0.1338453818,
          'Distance travelled (nm)': 0.3990102556,
          'Total idle spent time at anchorage (hours)': 0.8785904219,
          'Cargo carried: Passenger': 0.3748835493,
          'Cargo carried: Weight or Volume': 0.6325191503,
          'Transport Work: Passenger': 0.7052706735,
          'Transport Work: Weight or Volume': 0.0343378858,
          'HFO ROB at departure (MT)': 0.2324903003,
          'HFO ROB at arrival (MT)': 0.2655636863,
          'At Berth HFO Consumption (MT)': 0.2682561521,
          'HFO Consumption (MT)': 0.4769368541,
          'LFO ROB at departure (MT)': 0.1958483959,
          'LFO ROB at arrival (MT)': 0.7430845698,
          'At Berth LFO Consumption (MT)': 0.5718565916,
          'LFO Consumption (MT)': 0.2487051842,
          'MDO ROB at departure (MT)': 0.5845358893,
          'MDO ROB at arrival (MT)': 0.6877443475,
          'At Berth MDO Consumption (MT)': 0.2906715855,
          'MDO Consumption (MT)': 0.0525336404,
          'MGO ROB at departure (MT)': 0.8811898717,
          'MGO ROB at arrival (MT)': 0.6270734176,
          'At Berth MGO Consumption (MT)': 0.6623102009,
          'MGO Consumption (MT)': 0.8051026917,
          'LPG (Propane) ROB at departure (MT)': 0.6566593839,
          'LPG (Propane) ROB at arrival (MT)': 0.509974773,
          'At Berth LPG (Propane) Consumption (MT)': 0.9784356882,
          'LPG (Propane) Consumption (MT)': 0.3834369812,
          'LPG (Butane) ROB at departure (MT)': 0.9975244203,
          'LPG (Butane) ROB at arrival (MT)': 0.3711101056,
          'At Berth LPG(Butane) Consumption (MT)': 0.9366509271,
          'LPG (Butane) Consumption (MT)': 0.9038165787,
          'Methanol ROB at departure (MT)': 0.9285652409,
          'Methanol ROB at arrival (MT)': 0.049081831,
          'At Berth Methanol Consumption (MT)': 0.7603596934,
          'Methanol Consumption (MT)': 0.9824171888,
          'Ethanol ROB at departure (MT)': 0.9409301763,
          'Ethanol ROB at arrival (MT)': 0.0528017844,
          'At Berth Ethanol Consumption (MT)': 0.315027825,
          'Ethanol Consumption (MT)': 0.9436516891,
          'At Berth LNG Consumption (MT)': 0.0111645531,
          'LNG Consumption (MT)': 0.7651640162,
          'Other ROB at departure (MT)': 0.9268074099,
          'Other ROB at arrival (MT)': 0.8650373862,
          'At Berth Other Consumption (MT)': 0.4269267267,
          'Bunkering before Arrival - Received Quantity: HFO': 0.3221322044,
          'Bunkering before Arrival - Received Quantity: LFO': 0.2284466274,
          'Bunkering before Arrival - Received Quantity: MDO': 0.2660831015,
          'Bunkering before Arrival - Received Quantity: MGO': 0.2675004343,
          'Bunkering before Arrival - Received Quantity: LPG(Propane)': 0.0674299484,
          'Bunkering before Arrival - Received Quantity: LPG(Butane)': 0.7290947389,
          'Bunkering before Arrival - Received Quantity: Methanol': 0.6315816067,
          'Bunkering before Arrival - Received Quantity: Ethanol': 0.6965363123,
          'Bunkering before Arrival - Received Quantity: LNG': 0.5613297502,
          'Bunkering before Arrival - Received Quantity: Other': 0.386490762,
          'Bunkering after Arrival - Received Quantity: HFO': 0.1462950799,
          'Bunkering after Arrival - Received Quantity: LFO': 0.0229632133,
          'Bunkering after Arrival - Received Quantity: MDO': 0.3004428354,
          'Bunkering after Arrival - Received Quantity: MGO': 0.2170343006,
          'Bunkering after Arrival - Received Quantity: LPG(Propane)': 0.2207445744,
          'Bunkering after Arrival - Received Quantity: LPG(Butane)': 0.0993751619,
          'Bunkering after Arrival - Received Quantity: Methanol': 0.6512875846,
          'Bunkering after Arrival - Received Quantity: Ethanol': 0.4208855829,
          'Bunkering after Arrival - Received Quantity: LNG': 0.5416727518,
          'Bunkering after Arrival - Received Quantity: Other': 0.9684061495,
          'Bunkering after Arrival - Received Quantity': 0.8295110012,
          'De-bunkering before Arrival - De-bunkered Quantity: HFO': 0.3683528264,
          'De-bunkering before Arrival - De-bunkered Quantity: LFO': 0.642641005,
          'De-bunkering before Arrival - De-bunkered Quantity: MDO': 0.5757692033,
          'De-bunkering before Arrival - De-bunkered Quantity: MGO': 0.9763804898,
          'De-bunkering before Arrival - De-bunkered Quantity: LPG (Propane)': 0.1369860939,
          'De-bunkering before Arrival - De-bunkered Quantity: LPG (Butane)': 0.8605623033,
          'De-bunkering before Arrival - De-bunkered Quantity: Methanol': 0.9542156229,
          'De-bunkering before Arrival - De-bunkered Quantity: Ethanol': 0.8610580194,
          'De-bunkering before Arrival - De-bunkered Quantity: LNG': 0.3956613422,
          'De-bunkering before Arrival - De-bunkered Quantity: Other': 0.7879618379,
          'De-bunkering after Arrival - De-bunkered Quantity: HFO': 0.6101862533,
          'De-bunkering after Arrival - De-bunkered Quantity: LFO': 0.5959206275,
          'De-bunkering after Arrival - De-bunkered Quantity: MDO': 0.245826867,
          'De-bunkering after Arrival - De-bunkered Quantity: MGO': 0.059420241,
          'De-bunkering after Arrival - De-bunkered Quantity: LPG (Propane)': 0.4913856095,
          'De-bunkering after Arrival - De-bunkered Quantity: LPG (Butane)': 0.5936231632,
          'De-bunkering after Arrival - De-bunkered Quantity: Methanol': 0.3303325747,
          'De-bunkering after Arrival - De-bunkered Quantity: Ethanol': 0.9114503531,
          'De-bunkering after Arrival - De-bunkered Quantity: LNG': 0.1521691918,
          'De-bunkering after Arrival - De-bunkered Quantity: Other': 0.5096506809,
          'De-bunkering after Arrival - De-bunkered Quantity': 0.0962357067,
          'Time spent at sea': 0.4343116335,
          'Distance travelled': 0.4672049092,
          'Fuel consumption: HFO': 0.80509881,
          'Fuel consumption: LFO': 0.4368786195,
          'Fuel consumption: MDO': 0.6142720172,
          'Fuel consumption: MGO': 0.6130259496,
          'Fuel consumption: LPG (Propane)': 0.0359509434,
          'Fuel consumption: LPG (Butane)': 0.4121771305,
          'Fuel consumption: Methanol': 0.1813022076,
          'Fuel consumption: Ethanol': 0.9892389057,
          'Fuel consumption: LNG': 0.7688324303,
          'Fuel consumption: Other': 0.0503793734
}
