from flask import Flask, jsonify, request
import logging
from pymodm import connect
from pymodm import MongoModel, fields
from datetime import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *

app = Flask(__name__)
connect('mongodb+srv://wl181:Willy1201@bme547-uxcjh.gcp.mongodb.net/'
        'test?retryWrites=true')
logging.basicConfig(filename='HRSS.log', filemode='w', level=logging.INFO)


class Patient(MongoModel):
    patient_id = fields.IntegerField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.FloatField()
    heart_rate = fields.ListField(fields.IntegerField())
    heart_rate_time = fields.ListField()


def validate_new_patient(n):
    """
    validate input new information of patient
    Args:
        n: dictionary including patient_id, attending_email and user_age keys
         for posting

    """
    if all(m in n for m in ("patient_id", "attending_email", "user_age")):
        if type(n["patient_id"]) != int:
            if type(n["patient_id"]) != str:
                raise TypeError("patient id must be int or str.")
        # if all(m in n for m in "attending_email"):
        if "@" not in n["attending_email"]:
            # logging.exception('TypeError: illegal email string')
            raise TypeError('attending_email should be email string')
        # if all(m in n for m in "user_age"):
        if isinstance(n["user_age"], int) is False:
            # logging.exception('TypeError: user_age not integer')
            raise TypeError('user_age should be int')
    else:
        # logging.exception('AttributeError: Post without required keys')
        raise AttributeError('Post must include patient_id, attending_email'
                             ' and user_age keys.')
    logging.info('New patient' + n["patient_id"] +
                 'information posted to database')
    pass


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    """
          Add new patient to database which input dictionary should look like:
            patient_info = {
            "patient_id": "1", # usually this would be the patient MRN
            "attending_email": "dr_user_id@yourdomain.com",
            "user_age": 50, # in years
                            }
            Then post new patient information to MongoDB database
         Returns:
             200 Status after posting
         """
    n = request.get_json()
    validate_new_patient(n)
    intro = Patient(n["patient_id"], attending_email=n["attending_email"],
                    user_age=n["user_age"])
    intro.save()
    return "POSTED", 400  # not sure actually return what


def validate_heart_rate(n):
    """
    validate user inputs for post to /api/heart_rate
    Args:
         n: dictionary including patient_id, attending_email and user_age keys
         for posting
    """
    if all(m in n for m in ("patient_id", "heart_rate")):
        if type(n["heart_rate"]) != int:
            if type(n["heart_rate"]) != str:
                # logging.exception("TypeError: heart rate not integer.")
                raise TypeError("heart_rate must be an integer or str.")
        if type(n["patient_id"]) != int:
            if type(n["patient_id"]) != str:
                raise TypeError("patient id must be int or str.")
    else:
        # logging.exception("AttributeError: Post does not have proper keys.")
        raise AttributeError("Post must be dict with patient_id and"
                             " heart_rate keys.")
    # logging.info("Passed heart rate POST validation.")
    pass


def send_attending_email(attending_email, patient_id):
    """
    send email to physician including the patient_id, the tachycardic
     heart rate, and the time stamp of that heart rate.
    Returns:
        str(response): the response indicating email sent #not sure about this
    """
    patient_id = str(patient_id)
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("wl181@duke.edu")
    to_email = Email(attending_email)
    subject = "WARNING: Tachycardic Patient"
    content1 = Content("text/plain", "Patient ID "
                       + patient_id
                       + " displayed a tachycardic heart rate:"
                       + realtime_heart_rate(patient_id).realtime_hr
                       + "at time:" + str(datetime.now()))
    mail1 = Mail(from_email, subject, to_email, content1)
    response = sg.client.mail.send.post(request_body=mail1.get())
    logging.info("Patient:" + str(patient_id) + " is detected as tachycardia,"
                 + " warning email sent to " + attending_email)
    return str(response)


@app.route("/api/heart_rate", methods=["POST"])
def patient_hr():
    """
     This route should store the sent heart rate measurement
     in the record for the specified patient as well as the
     current timestamps of POST.

    Returns:
        tachycarduc_status: string containing patient tachycardia status
    """
    n = request.get_json()
    validate_heart_rate(n)
    realtime = str(datetime.now())
    patient = Patient.objects.raw({"_id": n["patient_id"]}).first()
    patient_age = patient.user_age
    attending_email = patient.attending_email
    patient.heart_rate.append(n["heart_rate"])
    patient.heart_rate_time.append(realtime)
    patient.save()
    logging.info("New heart rate posted to database")
    tachycardic_status = tachycardic_detector(patient_age, n["heart_rate"])
    if tachycardic_status is "tachycardic":
        send_attending_email(attending_email, n["patient_id"])
    return tachycardic_status, 400


def tachycardic_detector(patient_age, patient_heart_rate):
    """
    Determines if patient is tachycardic based on their age and heart rate
    Args:
        patient_age: integer extracted from patient database entry
        patient_heart_rate: integer posted to patient database entry
    Returns:
        tachycardic_status: string containing either
         "tachycardic" or "not tachycardic"
    """
    if patient_age < 3 and patient_heart_rate > 151:
        tachycardic_status = "tachycardic"
    elif patient_age < 5 and patient_heart_rate > 137:
        tachycardic_status = "tachycardic"
    elif patient_age < 8 and patient_heart_rate > 133:
        tachycardic_status = "tachycardic"
    elif patient_age < 12 and patient_heart_rate > 130:
        tachycardic_status = "tachycardic"
    elif patient_age <= 15 and patient_heart_rate > 119:
        tachycardic_status = "tachycardic"
    elif patient_heart_rate > 100:
        tachycardic_status = "tachycardic"
    else:
        tachycardic_status = "not tachycardic"
    # logging.info("Tachycardic status calculated: " + tachycardic_status)
    return tachycardic_status
    pass


def realtime_heart_rate(patient_id):
    """
    shows the heart rate and tachycardic status on the most recent timestamp.
    Args:
        patient_id: patient id in integer
    Returns:
        hr_time: most recent timestamp input
        realtime_hr: patient heart rate at the most recent timestamp
        tachycardi_status: the status whether a patient is detected as
         tachycardic at the most recent timestamp
    """
    patient_id = int(patient_id)
    patient = Patient.objects.raw({"_id": patient_id}).first()
    patient_age = patient.user_age
    realtime_hr = patient.heart_rate[-1]
    hr_time = patient.heart_rate_time[-1]
    tachycardic_status = tachycardic_detector(patient_age, realtime_hr)
    return hr_time, realtime_hr, tachycardic_status
    pass


@app.route("/api/status/<patient_id>", methods=["GET"])
def patient_stat(patient_id):
    """
    Returns a JSON containing the latest heart rate for the specified patient,
    whether this patient is currently tachycardic based on this most recently
    posted heart rate, and the timestamp of this most recent heart rate
    where return status has format of:
    status = {
                "heart_rate": 100,
                "status":  "tachycardic" | "not tachycardic",
                "timestamp": "2018-03-09 11:00:36.372339"
                }
    Args:
        patient_id: patient id in string or int
    Returns:
        heart_rate: patient's most recent heart rate
        status: whether the patient is detected as tachycardic or not
        timestamp: timestamp with data and time string
    """

    hr_time, realtime_hr, tachycardic_status = realtime_heart_rate(patient_id)
    patient_status = {
        "heart_rate": realtime_hr,
        "status": tachycardic_status,
        "timestamp": hr_time
    }
    return jsonify(patient_status)


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def list_hr(patient_id):
    """
     Gives a list of all the previous heart rate measurements for
    that patient.
    Args:
        patient_id: patient id in integer or string
    Returns:
        HR_list: json file including patient_id and heart rates with associated
         timestamps
    """
    patient_id = int(patient_id)
    patient = Patient.objects.raw({"_id": patient_id}).first()
    list_heart_rates = patient.heart_rate
    hr_list = {
        "patient_id": patient_id,
        "stored_heart_rates": list_heart_rates,
    }
    return jsonify(hr_list)


def avg_hr(patient_id):
    """
    Algorithm to calculate average heart rate saved so far.
    Args:
        patient_id: patient id in integer
    Returns:
        hr_avg: average heart rate calculated
    """
    patient_id = int(patient_id)
    patient = Patient.objects.raw({"_id": patient_id}).first()
    list_heart_rates = patient.heart_rate
    avg = sum(list_heart_rates) / len(list_heart_rates)
    # hr_avg = {
    #     "patient_id": patient_id,
    #     "heart_rate_average": avg
    # }
    logging.info('Patient heart rate average is:' + str(avg))
    return avg


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def avg_hr_result(patient_id):
    """
    GETs  average of heart rate over all timestamps of every specific patient
    Args:
        patient_id: patients' id in integer
    Returns:
         hr_avg: json dictionary with patient_id and heart rate average keys
    """
    hr_avg = avg_hr(patient_id)
    return hr_avg


def validate_heart_rate_interval_average(n):
    """
    validates inputs for posts to /api/heart_rate/interval_average
    Args:
        n: dictionary with patient_id and heart_rate_average_since

    """
    if all(m in n for m in ("patient_id", "heart_rate_average_since")):
        if type(n["patient_id"]) != int:
            if type(n["patient_id"]) != str:
                raise TypeError("patient id invalid")
        if type(n["heart_rate_average_since"]) != str:
            # logging.exception("TypeError: time stamp not string")
            raise TypeError("heart_rate_average_since should be string")
        try:
            datetime.strptime(n["heart_rate_average_since"],
                              "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            # logging.exception("ValueError: time string has invalid format")
            raise ValueError("ValueError: time string should have format of"
                             "%Y-%m-%d %H:%M:%S.%f")
    else:
        logging.exception("AttributeError: Post have illegal keys.")
        raise AttributeError("Post should be dictionary with patient_id"
                             "and heart_rate_average_since.")
    # logging.info("Passed heart rate interval average POST validation")


def check_time_string(past_hr_times, date_str):
    """
        Iterates through the listed timestamps for validation of the defined
         input time.
    Args:
        past_hr_times: list of saved heart rate timestamps
        date_str: the specified input string of time
    Returns:
        time_index: index in past_hr_times where the date_str occur
        ValueError: error raised when input specific time not valid
    """
    try:
        time_index = past_hr_times.index(date_str)
    except ValueError:
        logging.exception("ValeError: Time string not in database")
        raise ValueError("No valid heart rate at this time point."
                         "Enter a valid time.")
    return time_index
    pass


def calculate_interval_avg(patient_id, hr_time_since):
    """
    Parse the input time string data.
    Algorithm to calculate the average of interval heart rate since
    given date/ time.
    Args:
        patient_id: patient id number in str or int
        hr_time_since: specific timestamp defined by user
    Returns:
        interval_hr_avg: the average of heart rate since the specific timestamp
    """
    patient_id = int(patient_id)
    patient = Patient.objects.raw({"_id": patient_id}).first()
    past_hr_times = patient.heart_rate_time
    time_index = check_time_string(past_hr_times, hr_time_since)
    past_heart_rates = patient.heart_rate[time_index:-1]
    interval_hr_avg = sum(past_heart_rates) / len(past_heart_rates)
    logging.info("Heart rate interval average calculated: " +
                 str(interval_hr_avg) + ' bpm')
    return interval_hr_avg


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_avg():
    """
    Calculate average heart rate since a defined time point
    Returns:
        interval_avg:  average heart rate since the specific time
        200 Status after posting has occurred
    """
    n = request.get_json()
    validate_heart_rate_interval_average(n)
    patient_id = n["patient_id"]
    hr_time_since = n["heart_rate_average_since"]
    interval_hr_avg = calculate_interval_avg(patient_id, hr_time_since)
    return interval_hr_avg, 400


if __name__ == "__main__":
    app.run()
