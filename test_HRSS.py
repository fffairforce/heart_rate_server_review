import pytest
import HRSS


def test_validate_new_patient1():
    t1 = {"patient_id": 2}
    with pytest.raises(AttributeError):
        HRSS.validate_new_patient(t1)


def test_validate_new_patient2():
    t2 = {"patient_id": '2', "attending_email": "wl181", "user_age": 10}
    with pytest.raises(TypeError):
        HRSS.validate_new_patient(t2)


def test_validate_new_patient3():
    t3 = {"patient_id": "2", "attending_email": "wl181@duke.edu",
          "user_age": 10.5}
    with pytest.raises(TypeError):
        HRSS.validate_new_patient(t3)


def test_validate_new_patient4():
    t4 = {"patient_id": "1", "attending_email": "wl181@duke.edu",
          "user_age": 10}
    answer = HRSS.validate_new_patient(t4)
    assert answer is None


def test_validate_heart_rate1():
    t1 = {"patient_id": 1.5, "heart_rate": '100'}
    with pytest.raises(TypeError):
        HRSS.validate_heart_rate(t1)


def test_validate_heart_rate2():
    t2 = {"patient_id": '3', "heart_rate": 100.5}
    with pytest.raises(TypeError):
        HRSS.validate_heart_rate(t2)


def test_validate_heart_rate3():
    t3 = {"heart_rate": 50}
    with pytest.raises(AttributeError):
        HRSS.validate_heart_rate(t3)


def test_validate_heart_rate4():
    t4 = {"patient_id": 3, "heart_rate": '100'}
    answer = HRSS.validate_heart_rate(t4)
    # print(answer)
    assert answer is None


@pytest.mark.parametrize("a,b,expected", [
    (2, 153, "tachycardic"),
    (4, 140, "tachycardic"),
    (6, 135, "tachycardic"),
    (10, 133, "tachycardic"),
    (14, 125, "tachycardic"),
    (16, 110, "tachycardic"),
    (16, 98, "not tachycardic")
])
def test_tachycardic_detector(a, b, expected):
    answer = HRSS.tachycardic_detector(a, b)
    assert answer == expected


def test_realtime_heart_rate():
    patient = HRSS.Patient(patient_id=3,
                           attending_email="wl181@duke.edu",
                           user_age=24,
                           heart_rate=[70],
                           heart_rate_time=["2019-04-05 18:44:01.902076"])
    patient.save()
    hr_time, realtime_hr, tachycardic_status = HRSS.realtime_heart_rate(3)
    assert hr_time == "2019-04-05 18:44:01.902076"
    assert realtime_hr == 70
    assert tachycardic_status == "not tachycardic"


# @pytest.mark.parametrize("t_patient_id, expected", [3, 80])
def test_avg_hr():
    patient = HRSS.Patient(patient_id=3,
                           attending_email="wl181@duke.edu",
                           user_age=24,
                           heart_rate=[70, 80, 90],
                           heart_rate_time=[
                               "2019-03-16 01:19:29.168676",
                               "2019-03-16 02:11:56.702286",
                               "2019-03-16 02:20:16.136095"
                           ])
    patient.save()
    answer = int(HRSS.avg_hr(3))
    assert answer == 80


def test_validate_heart_rate_interval_average():
    t1 = {"patient_id": 1.5,
          "heart_rate_average_since": "2019-04-05 1:19:29.168676"}
    with pytest.raises(TypeError):
        HRSS.validate_heart_rate_interval_average(t1)


def test_validate_heart_rate_interval_average2():
    t2 = {"patient_id": '2',
          "heart_rate_average_since": 2019}
    with pytest.raises(TypeError):
        HRSS.validate_heart_rate_interval_average(t2)


def test_validate_heart_rate_interval_average3():
    t3 = {"patient_id": 2,
          "heart_rate_average_since": "2019-04-05"}
    with pytest.raises(ValueError):
        HRSS.validate_heart_rate_interval_average(t3)


@pytest.mark.parametrize("past_hr_times, date_str, expected", [
    (["2019-03-16 01:19:29.168676", "2019-03-16 02:11:56.702286",
      "2019-03-16 02:20:16.136095"], "2019-03-16 01:19:29.168676",
     0)
])
def test_check_time_string(past_hr_times, date_str, expected):
    answer = HRSS.check_time_string(past_hr_times, date_str)
    assert answer == expected


# @pytest.mark.parametrize("t_patient_id, t_hr_time_since, expected", [
#     '2', '2019-03-16 01:19:29.168676', 70
# ])
def test_calculate_interval_av():
    patient = HRSS.Patient(patient_id=2,
                           attending_email="wl181@duke.edu",
                           user_age=24,
                           heart_rate=[70, 75],
                           heart_rate_time=['2019-03-16 01:19:29.168676',
                                            '2019-03-16 02:19:29.168676'])
    patient.save()
    answer = HRSS.calculate_interval_avg('2', '2019-03-16 01:19:29.168676')
    assert answer == 70
