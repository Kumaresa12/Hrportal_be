import pandas as pd
from app import db
import io
import calendar

class Report:
    def __init__(self, months, year, team):
        self.employee = { data.get('unique_id'): data.get('name') for data in db.employees.find({"team": team}, {'_id': 0}) }
        self.allowance = [data for data in db.allowance.find({}, {'_id': 0})]
        self.unique_id = list(self.employee.keys())
        self.team = team
        self.months = months
        self.year = year
        self.report_data = {}
    
    def extract_data(self):
        for month in self.months:
            month_data = db.shifts.find({"month": month, "year": self.year,
                                          "unique_id": {"$in": self.unique_id}}, {"_id": 0})
            for data in month_data:
                shift_dict = {}
                # working_days = 0
                for day, shift_info in data["shifts"].items():
                    if shift_info["shift"] in ["general", "planned", "restricted", "holiday"]:
                        continue

                    for allowance in self.allowance:
                        if allowance["shift"] == shift_info["shift"]:
                            if shift_info["overwork"]:
                                shift_name = "holiday"
                                allowance_amount = allowance["overwork_allowance"]
                            else:
                                shift_name = shift_info["shift"]
                                allowance_amount = allowance["allowance"]
                            # working_days += 1

                    if shift_info["shift"] not in shift_dict.keys():
                        shift_dict[shift_name] = {"total": 1, "allowance": allowance_amount}
                    else:
                        shift_dict[shift_name]["total"] += 1
                        shift_dict[shift_name]["allowance"] += allowance_amount
                
                # shift_dict["working_days"] = working_days

                if self.employee[data["unique_id"]] not in self.report_data.keys():
                    self.report_data[self.employee[data["unique_id"]]] = {calendar.month_name[month]: shift_dict}
                else:
                    self.report_data[self.employee[data["unique_id"]]].update({calendar.month_name[month]: shift_dict})
    
    def convert_to_csv(self):
        header = ["name"]
        shift_list = ["night", "afternoon", "holiday"]

        shift_columns = []

        for shift in shift_list:
            for month in self.months:
                header.append(f"{calendar.month_name[month]} ({shift})")
            shift_columns.append(f"Total {shift} shift")
            header.append(f"Total {shift} shift")
        
        header.append("Total working days")

        for shift in shift_list:
            header.append(f"Total {shift} shift Allowance")


        dataframe = pd.DataFrame(columns=header)
        
        for employee, data in self.report_data.items():
            row_data = {"name": employee}
            for month, shift_data in data.items():
                for shift, value in shift_data.items():


                    if f"{month} ({shift})" in header:
                        row_data[f"{month} ({shift})"] = value["total"]

                        if f"Total {shift} shift" in row_data.keys():
                            row_data[f"Total {shift} shift"] += value["total"]
                        else:
                            row_data[f"Total {shift} shift"] = value["total"]
                        
                        if f"Total {shift} shift Allowance" in row_data.keys():
                            row_data[f"Total {shift} shift Allowance"] += value["allowance"]
                        else:
                            row_data[f"Total {shift} shift Allowance"] = value["allowance"]
                    
            dataframe = pd.concat([dataframe, pd.DataFrame([row_data])], ignore_index=True)
            dataframe.fillna(0, inplace=True)
        dataframe["Total working days"]= dataframe[shift_columns].sum(axis=1)

        csv_buffer = io.BytesIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        return csv_buffer

    def run(self):
        self.extract_data()
        return self.convert_to_csv()

