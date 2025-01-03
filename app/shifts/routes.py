from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.shifts.models import (
    Shifts, adding_allowance, change_shift, delete_allowance, diff_shifts, 
    all_allowance, edit_employee, employees, get_teams, insert_allowance, 
    remove_employee, update_allowance, add_new_employee, update_allowanceV2
)
from app import db

shifts = Blueprint('shifts', __name__)

def handle_error(message: str, status_code: int):
    """Utility function to create error responses."""
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

@shifts.route('/<month>/<year>', methods=['POST'])
def get_shifts(month: str, year: str):
    """
    Fetch shifts for a given month and year.
    
    Args:
        month (str): Month as a string.
        year (str): Year as a string.
    
    Returns:
        Response: JSON response with shifts or error message.
    """
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        team = data.get("team", "")
        if not team:
            return handle_error("Invalid input: 'team' field is required", 400)
        
        shifts = Shifts(team)
        return jsonify({'shifts': shifts.get_shifts(int(month), int(year))})
    except ValueError:
        return handle_error("Invalid input: Month and year must be integers", 400)
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/get_shifts', methods=['GET'])
def all_shifts():
    """Fetch all shifts."""
    try:
        return jsonify(diff_shifts())
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/get_allowance', methods=['GET'])
def get_allowance():
    """Fetch all allowances."""
    try:
        return jsonify(all_allowance())
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/update_allowance', methods=['POST'])
def change_allowance():
    """Update an existing allowance."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        
        update_allowanceV2(data)
        return jsonify({'status': 'Successfully updated data', 'data': all_allowance()})
    except KeyError as e:
        return handle_error(f"Missing key: {e}", 400)
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/insert_allowance', methods=['POST'])
def adding_allowance():
    """Insert a new allowance."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        
        insert_allowance(data)
        return jsonify({'status': 'Successfully inserted data', 'data': all_allowance()})
    except KeyError as e:
        return handle_error(f"Missing key: {e}", 400)
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/delete_allowance', methods=['POST'])
def remove_allowance():
    """Delete an allowance by unique ID."""
    try:
        data = request.json
        if not data or "unique_id" not in data:
            return handle_error("Invalid input: 'unique_id' is required", 400)
        
        delete_allowance(data["unique_id"])
        return jsonify({"status": "Deleted allowance...", 'data': all_allowance()})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/update_shifts', methods=['POST'])
def update_shifts():
    """Update shifts for a given month and year."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)

        month = data.get('month')
        year = data.get('year')
        team = data.get('team', '')
        shift_data = data.get('data', [])
        
        if not month or not year:
            return handle_error("Invalid input: 'month' and 'year' are required", 400)
        
        change_shift(month, year, shift_data)
        shifts = Shifts(team)
        return jsonify({'status': 'Successfully updated shifts data', 'shifts': shifts.get_shifts(int(month), int(year))})
    except ValueError:
        return handle_error("Invalid input: Month and year must be integers", 400)
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('/add_allowance', methods=['POST'])
def add_allowance():
    """Add a new allowance."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        
        return jsonify({'data': adding_allowance(data)})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('all_employees', methods=['GET'])
def all_employees():
    """Fetch all employees."""
    try:
        return jsonify({"employees": employees()})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('update_employee', methods=['POST'])
def update_employee():
    """Update employee details."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        
        edit_employee(data)
        return jsonify({"employees": employees()})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('delete_employee', methods=['POST'])
def delete_employee():
    """Delete an employee."""
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)
        
        remove_employee(data)
        return jsonify({"employees": employees()})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('add_employees', methods=['POST'])
def add_employee_data():
    """Add new employees."""
    try:
        data = request.json
        if not data or "employees" not in data:
            return handle_error("Invalid input: 'employees' field is required", 400)
        
        new_employees = data["employees"]
        return jsonify({"employees": add_new_employee(new_employees), "status": "success"})
    except Exception as e:
        return handle_error(str(e), 500)

@shifts.route('teams', methods=['GET'])
def get_teams_list():
    """Fetch all teams."""
    try:
        return jsonify(get_teams())
    except Exception as e:
        return handle_error(str(e), 500)
