# Note: Please install following libraries to run the flask API : flask, pymongo, dnspython, flask_cors
# > set FLASK_APP=flaskr
# > set FLASK_ENV=development
# > flask run

from flask import Flask, jsonify, request, render_template, redirect
from flask_cors import CORS
##import pymongo
import numpy as np
import pandas as pd
  
# connection_url = 'mongodb+srv://admin:samplearticle@cluster0-pm5vp.mongodb.net/test?retryWrites=true&w=majority'
# connection_url = 'mongodb+srv://ibara1010:admin123@cluster0.4gh6a.mongodb.net/test?retryWrites=true&w=majority'
##connection_url = 'mongodb://ibara1010:admin123@cluster0-shard-00-00.4gh6a.mongodb.net:27017,cluster0-shard-00-01.4gh6a.mongodb.net:27017,cluster0-shard-00-02.4gh6a.mongodb.net:27017/test?ssl=true&replicaSet=atlas-i9oz7l-shard-0&authSource=admin&retryWrites=true&w=majority'

app = Flask(__name__)
# client = pymongo.MongoClient(connection_url)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Kalau butuh define sendiri :  
# Database = client["test"]
# SampleTable = Database["iot__"]

# # Database
# Database = client.get_database('Example')
# # Table
# SampleTable = Database.SampleTable


dt = pd.read_excel(r"C:\Users\Mauliya P Lestari\Documents\Budi\Krispi\static\files\isol_1jm_udh(2).xlsx", sheet_name="Sheet1")

dtreal = pd.read_excel(r"C:\Users\Mauliya P Lestari\Documents\Budi\Krispi\static\files\isol_1jm_udh(2).xlsx", sheet_name="Sheet1")

dt_normpH = (dt.ph - dt.ph.min()) / (dt.ph.max() - dt.ph.min())

dt_normsal = (dt.sal - dt.sal.min()) / (dt.sal.max() - dt.sal.min())

dt['ph'] = dt_normpH

dt['sal'] = dt_normsal

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def MAD(aktual,ramalan):
    t = np.array(aktual)
    x = sum(abs(t-ramalan))
    error = x/len(t)
    return error

def MSE(y,f):
	error = np.mean(( y - f)**2)
	return error

def MAPE(y, f): 
    y, f = np.array(y), np.array(f)
    return np.mean(np.abs((y - f) / y)) * 100


dataPh = dt['ph'].tolist()
dataSal = dt['sal'].tolist()

    
phasil = moving_average(dataPh,5)
salhasil = moving_average(dataSal,5)

phF = pd.DataFrame({'ph':phasil})
salF = pd.DataFrame({'sal':salhasil})

phF = phF*(dtreal.ph.max() - dtreal.ph.min()) + dtreal.ph.min()
salF = salF*(dtreal.sal.max() - dtreal.sal.min()) + dtreal.sal.min()

ph = phF['ph'].tolist()
sal = salF ['sal'].tolist()

ph = np.concatenate([np.zeros(4),ph])
sal = np.concatenate([np.zeros(4),sal])

phF = pd.DataFrame({'ph':ph})
salF = pd.DataFrame({'sal':sal})


dt['ph'] = phF['ph']
dt['sal'] = salF['sal']

    
# Ini home
@app.route('/', methods=['GET'])
def home():
    print(dtreal['ph'])
    print(dt['ph'])
    return "PH"+"<br>MAD :"+str(MAD(dtreal.ph[4:],dt.ph[4:]))+"<br>MSE :"+str(MSE(dtreal.ph[4:],dt.ph[4:]))+"<br>MAPE :"+str(MAPE(dtreal.ph[4:],dt.ph[4:]))+"<br><br>SAL"+"<br>MAD :"+str(MAD(dtreal.sal[4:],dt.sal[4:]))+"<br>MSE :"+str(MSE(dtreal.sal[4:],dt.sal[4:]))+"<br>MAPE :"+str(MAPE(dtreal.sal[4:],dt.sal[4:]))


#coba render
@app.route('/dashboard/', methods=['GET'])
def dashboard():
    return render_template('linechart.html')


@app.route('/data/', methods=['GET'])
def data():
    return render_template('dataview.html')

@app.route('/sma/', methods=['GET'])
def sma():
    return render_template('sma.html')

@app.route('/about/', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/apisma/', methods=['GET'])
def apisma():
    
    tmp = []

    tmp2 = []
    
    for row in dt.values:
        tmp.append({"timestamp":row[6], "ph":row[3], "sal":row[4]})
    
    for row in dtreal.values:
        tmp2.append({"timestamp":row[6], "ph":row[3], "sal":row[4]})
        
    return jsonify({"pred":tmp[5:],
                    "asli":tmp2})

  
# To find all the entries/documents in a table/collection,
# find() function is used. If you want to find all the documents
# that matches a certain query, you can pass a queryObject as an
# argument.
'''
@app.route('/find/', methods=['GET'])
def findAll():
    query = SampleTable.find()
    output = {}
    i = 0
    for x in query:
        output[i] = x
        output[i].pop('_id')
        i += 1
    return jsonify(output)
'''
@app.errorhandler(404)
def not_found(error):
    url = request.path
    if url.islower():
        return "not found"
    else:
        return redirect(request.full_path.lower())

if __name__ == '__main__':
    app.run(debug=True)
