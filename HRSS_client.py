import requests

# api_host = "vcm-9129.vm.duke.edu"
api_host = "http://127.0.0.1:5000/"

def post_new_patients(patient_id, attending_email, user_age):
    """
    Makes  new patient information POST request to /api/new_patient
    Args:
        patient_id: patient id in string or int
        attending_email: patient's attending email in string
        user_age: patient's age in years(int)
    Returns:
         r: POST request status
    """
    test_data = {
        "patient_id": patient_id,
        "attending_email": attending_email,
        "user_age": user_age
    }
    r = requests.post(api_host + '/api/new_patient', json=test_data)
    return r


def post_heart_rate(patient_id, heart_rate):
    """
    Makes new heart rate data POST request to /api/heart_rate.
    Args:
        patient_id: patient id in string
        heart_rate: patient heart rate in integer
    Returns:
        r: POST request status
    """
    test_data = {
        "patient_id": patient_id,
        "heart_rate": heart_rate
    }
    r = requests.post(api_host + '/api/heart_rate', json=test_data)
    return r


def get_patient_stat(patient_id):
    """
    Makes GET request to /api/status/<patient_id>.
    Args:
        patient_id: patient id in string
    Returns:
        patient_stat: patient status from database in dictionary including
        heart rate, tachycardic status, timestamp
    """
    r = requests.get(api_host + '/api/status/' + str(patient_id))
    patient_stat = r.json()
    return patient_stat


def get_patient_hr_list(patient_id):
    """
    Makes GET request to /api/heart_rate/<patient_id>
    Args:
        patient_id: patient id in string
    Returns:
        heart_rate_list: json file with list of saved patient heart rates and
        patient id keys
    """
    r = requests.get(api_host + '/api/heart_rate/' + str(patient_id))
    heart_rate_list = r.json()
    return heart_rate_list


def get_hr_average(patient_id):
    """
    Makes GET request  from /api/heart_rate/average/<patient_id>.
    Args:
        patient_id: patient id in string
    Returns:
        heart_rate_avg: json file with average heart rate saved and patient id
         keys
    """
    r = requests.get(api_host + '/api/heart_rate/average/' + patient_id)
    heart_rate_avg = r.json()
    return heart_rate_avg


def post_interval_avg(patient_id, heart_rate_average_since):
    """
    Makes POST request from /api/heart_rate/interval_average to post interval
     heart rate average.
    Args:
        patient_id: patient id in string or integer
        heart_rate_average_since: average heart rate from the specific time
    Returns:
         r: POST request status
    """
    # patient_id = int(patient_id)
    test_data = {
        "patient_id": patient_id,
        "heart_rate_average_since": heart_rate_average_since
    }
    r = requests.post(api_host + '/api/heart_rate/interval_average',
                      json=test_data)
    return r


if __name__ == "__main__":

    # post a new patient from local
    post1 = post_new_patients('1', "wl181@duke.edu", 20)
    print(post1)
    # post new heart rate for patient from local
    post2 = post_heart_rate(1, 65)
    print(post2)
    # get patient data from local
    patient_status = get_patient_stat(1)
    print(patient_status)
    # get patient heart rate from local
    hr_list = get_patient_hr_list(1)
    print(hr_list)
    # get patient average heart rate from local
    hr_avg = get_hr_average(1)
    print(hr_avg)
    # post interval heart rate from specified timestamp from local
    post3 = post_interval_avg(1, "2018-03-09 11:00:36.372339")
    print(post3)
