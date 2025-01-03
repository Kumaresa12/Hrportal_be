from bson import ObjectId
from app import db
import uuid
import calendar

class Shifts:
    def __init__(self, team):
        self.team = team
        self.employee = { data.get('unique_id'): data.get('name') for data in  db.employees.find({"team": team}, {'_id': 0}) }
    
    def get_employee_name_from_data(self, data):
        unique_id = data.get('unique_id')
        
        if unique_id:
            name = self.employee.get(unique_id, 'UNKNOWN')
        else:
            name = 'UNKNOWN'

        data['name'] = name
        return data
    
    def extract_shift(self, month: int, year: int):
        unique_id = list(self.employee.keys())
        return [self.get_employee_name_from_data(shift) for shift in db.shifts.find({'month': int(month), 'year': int(year),
                                                                                    "unique_id": {"$in": unique_id}},
                                                                                    {'_id': 0, 'unique_id': 1, 'shifts': 1})]

    def generate_shift(self, month, year):
        _, num_days = calendar.monthrange(year, month)

        random_shift = db.allowance.find_one({}, {'_id': 0, 'shift': 1}).get('shift', '')

        for unique_id, name in self.employee.items():
            data = {"unique_id": unique_id, "month": month, "year": year, "total_days": num_days}
            shifts = {}
            for day in range(1, num_days + 1):
                shifts["day_" + str(day)] = {"shift": random_shift, "overwork": False}
            data["shifts"] = shifts

            db.shifts.insert_one(data)

        return self.extract_shift(month, year)


    def get_shifts(self, month: int, year: int):
        shifts = self.extract_shift(month, year)
        
        if not shifts:
            shifts = self.generate_shift(month, year)

        return shifts
    
    def get_shift_history(self, unique_id: str, year: int):
        history = [shift for shift in db.shifts.find({'unique_id': unique_id, 'year': int(year)}, {'_id': 0, 'shifts': 1, 'month': 1, 'year': 1})]
        return {'name': self.employee.get(unique_id, 'UNKNOWN'), 'history': history}
    
def diff_shifts():
    return [shift.get('shift') for shift in db.allowance.find({}, {'_id': 0, 'shift': 1})]

def all_allowance():
    return [data for data in db.allowance.find({}, {'_id': 0})]

def update_allowance(data):
    for allowance in data:
        if allowance.get('changed') and db.allowance.find_one({'unique_id': allowance.get('unique_id')}):
            allowance.pop('changed')
            db.allowance.update_one({'unique_id': allowance.get('unique_id')}, {'$set': allowance})
        else:
            unique_id = uuid.uuid4()
            
            if db.allowance.find_one({'unique_id': unique_id}):
                raise ValueError("Unique id already exist...")
            
            allowance['unique_id'] = unique_id
            allowance.pop('changed')
            db.allowance.insert_one(allowance)

def update_allowanceV2(data):
    db.allowance.update_one({'unique_id': data.get('unique_id')}, {'$set': data})

def insert_allowance(allowance):
    unique_id = str(uuid.uuid4())
    
    if db.allowance.find_one({'unique_id': unique_id}):
        raise ValueError("Unique id already exist...")
    
    allowance['unique_id'] = unique_id

    db.allowance.insert_one(allowance)

def delete_allowance(unique_id):
    db.allowance.delete_one({"unique_id": unique_id})

def change_shift(month, year, data):

    for shift in data:
        for day, work  in shift["shifts"].items():
            if "changed" in work.keys():
                work.pop("changed")

        db.shifts.update_one({'unique_id': shift.get('unique_id'), 'month': int(month), 'year': int(year)},
                            {'$set': {'shifts': shift.get('shifts')}})
                            
def adding_allowance(data):
    for allowance in data:
        if db.allowance.find_one({'shift': allowance.get('shift', '')}):
            continue
        unique_id = str(uuid.uuid4())

        db.allowance.insert_one({'unique_id': unique_id, 'shift': allowance.get('shift', ''), 'allowance': allowance.get('allowance', ''),
                                'overwork_allowance': allowance.get('overwork_allowance', ''), 'work': allowance.get('work', False)})
    return all_allowance()

def employees():
    return [data for data in db.employees.find({}, {'_id': 0})]

def add_new_employee(new_employees):
    for employee in new_employees:
        already_exist = db.employees.find_one({"name": employee["name"], "team":employee["team"]})

        if already_exist:
            continue
    
        unique_id = str(uuid.uuid4())

        db.employees.insert_one({"name": employee["name"], "team":employee["team"], "unique_id": unique_id})

    return employees()

def edit_employee(employee):
    db.employees.update_one({"unique_id": employee["unique_id"]}, {"$set": {"name": employee["name"], "team": employee["team"]}})

def remove_employee(data):
    db.employees.delete_one({"unique_id": data["unique_id"]})

def get_teams():
    return db.portal_manager.find_one({"_id": ObjectId("673852c639119f5963cd46d8")}, {"_id": 0, "teams": 1})


    
    