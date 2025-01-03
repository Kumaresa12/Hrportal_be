from __future__ import annotations
from flask import Blueprint, request, jsonify, send_file
from app import db
from app.report.models import get_months_created
from app.report.utils import Report

report = Blueprint('report', __name__)

def handle_error(message: str, status_code: int):
    """
    Utility function to create error responses.
    
    Args:
        message (str): Error message to include in the response.
        status_code (int): HTTP status code to return.

    Returns:
        Response: Flask JSON response with error message and status code.
    """
    response = jsonify({'error': message})
    response.status_code = status_code
    return response

@report.route('/get_months/<year>', methods=['POST'])
def get_months(year: str):
    """
    Retrieve months for which reports are created for a specific year and team.

    Args:
        year (str): The year for which to fetch created months.

    Returns:
        Response: JSON response with months and year, or an error message.
    """
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)

        team = data.get("team", "")
        if not team:
            return handle_error("Invalid input: 'team' field is required", 400)

        months = get_months_created(year, team)
        return jsonify({"months": months, "year": year})
    except Exception as e:
        return handle_error(str(e), 500)

@report.route('/generate_csv', methods=['POST'])
def generate_csv():
    """
    Generate a CSV report for specified months, year, and team.

    Args:
        None (data passed in JSON format via POST request).

    Returns:
        Response: File download response for the generated CSV, or an error message.
    """
    try:
        data = request.json
        if not data:
            return handle_error("Invalid input: No JSON data found", 400)

        months = data.get("months", [1])
        year = data.get("year", 2024)
        team = data.get("team", "")

        if not isinstance(months, list) or not all(isinstance(m, int) for m in months):
            return handle_error("Invalid input: 'months' must be a list of integers", 400)

        if not isinstance(year, int):
            return handle_error("Invalid input: 'year' must be an integer", 400)

        if not team:
            return handle_error("Invalid input: 'team' field is required", 400)

        months.sort()
        report = Report(months, year, team)
        csv_buf = report.run()

        return send_file(csv_buf, mimetype='text/csv', as_attachment=True, download_name='data.csv')
    except Exception as e:
        return handle_error(str(e), 500)
