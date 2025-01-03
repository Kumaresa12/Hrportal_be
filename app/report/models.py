from app import db

def get_months_created(year, team):
    unique_id = [data.get('unique_id', "") for data in db.employees.find({"team": team}, {'_id': 0})]
    return db.shifts.distinct("month", {"year": int(year), "unique_id": {"$in": unique_id}})

