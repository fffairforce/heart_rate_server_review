# BME 547 
heart-rate-sentinel-server-fffairforce
[![Build Status](https://travis-ci.com/BME547-Spring2019/heart-rate-sentinel-server-fffairforce.svg?token=y2E3CUdmbCCXpxoiT8Pe&branch=master)](https://travis-ci.com/BME547-Spring2019/heart-rate-sentinel-server-fffairforce)
Due date: 4/5/2019 11:59pm

wl81, WeiHsien, Lee
# Functional codes
`HRSS.py`

The server code is located in hrss.py. 
The server is currently running at vcm-9129.vm.duke.edu:5000.
It should work on all accounts (SendGrid API included) and unit tested.
Just run the HRSS.py file and the server will be on for use.

`hrss_test_client.py`

This file contains a client to make POST and GET requests to all 
the functionalities included in `hrss.py`. Example executions are 
included in the file under 
`if __name__ == "__main__"`.
Note that, at this time, POST /api/heart_rate/interval_average only allows 
users to post times at which heart rate data was taken to calculate the 
heart rate average since that time. It is recommended that users 
GET these times from /api/heart_rate/<patient_id> and then select
a time from the resultant timestamp list to use in their POST.

If running `hrss.py` on a different server, 
change the `api_host` string in line 3 to the appropriate host name and port.
 It is currently set to the vcm server listed above,