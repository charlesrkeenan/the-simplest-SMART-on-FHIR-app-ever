# STEP 0: Import software dependencies, initialize app framework, configure session key and app settings, then define functions
from flask import Flask, redirect, session, request
from fhirclient import client
from fhirclient.models.patient import Patient

app = Flask(__name__)

app.secret_key = '123abc'
app_settings = {
    'app_id': 'my_app_id',
    'app_secret': 'my_app_secret',
    'api_base': 'http://localhost:4013/v/r4/fhir',
    'redirect_uri': 'http://localhost:5000/redirect_uri',
    'scope': 'fhirUser openid patient/Patient.read'
}

def save_state(state):
    session['state'] = state

def get_smart():
    state = session.get('state')
    if state:
        return client.FHIRClient(state=state, save_func=save_state)
    else:
        return client.FHIRClient(settings=app_settings, save_func=save_state)

# STEP 1: Accept user's launch request
@app.route('/launch')
def launch():
    app_settings['launch_token'] = request.args.get('launch')
    smart = get_smart()
    return redirect(smart.authorize_url)

# STEP 2: Request user authentication and data authorization
@app.route('/redirect_uri')
def redirect_uri():
    smart = get_smart()
    smart.handle_callback(request.url)
    return redirect('/get_patient')

# STEP 3: Retrieve patient record and display in the web browser!
@app.route('/get_patient')
def get_patient():
    smart = get_smart()
    patient = Patient.read(rem_id=smart.patient_id, server=smart.server)
    return patient.as_json(), 200
    
if __name__ == '__main__': 
    app.run(port=5000)