import cvlib as cv
from cvlib.object_detection import draw_bbox
import cv2 , time
import numpy as np
from flask import Flask , render_template , request , redirect,url_for
from cloudant.client import Cloudant

app=Flask(__name__)

client = Cloudant.iam("1fab0e8d-d938-42eb-b57d-421eccb4ed8e-bluemix" , "xSZm4--d0FbxVsGtFtbnAoC1nrl3SnnZ_tjD0voMQ21C" , connect = True)
my_database = client.create_database('my_database')


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/register" , methods = ['GET' , 'POST'])
def register():
    if request.method == "POST":
        x = [x for x in request.form.values()]
        data = {
            'email':x[0] ,
            'password':x[1]
        }
        query = {'data' : {'$eq' : data}}
        docs = my_database.get_query_result(query)
        print(len(docs.all()))
        if(len(docs.all()) == 0):
            url = my_database.create_document(data)
            return render_template('login.html')
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/afterlogin', methods=['POST'])
def afterlogin():
    user = request.form['username']
    passw = request.form['pass']
    print(user, passw)

    query = {'email': {'$eq': user}}

    docs = my_database.get_query_result(query)
    print(docs)

    print(len(docs.all()))

    if (len(docs.all()) == 0):
        return render_template('login.html', pred="The username is not found.")
    else:
        if ((user == docs[0][0]['email'] and passw == docs[0][0]['password'])):
            return redirect("/prediction")
        else:
            return render_template('login.html', pred="Invalid email or password")


@app.route("/prediction" , methods = ['GET' , 'POST'])
def predict():
    if request.method == 'POST':
        image = request.files['file']
        webcam = cv2.VideoCapture(image.filename)
        t0 = time.time()
        centre0 = np.zeros(2)
        isDrowning = False
        while True:

            status, frame = webcam.read()

            if not status:
                print("Could not read frame")
                exit()

            bbox, label, conf = cv.detect_common_objects(frame)

            if(len(bbox)>0):
                    bbox0 = bbox[0]                    
                    centre = [0,0]                    

                    centre =[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2 ]
                    hmov = abs(centre[0]-centre0[0])
                    vmov = abs(centre[1]-centre0[1])                    

                    x=time.time()

                    threshold = 10
                    if(hmov>threshold or vmov>threshold):
                        print(x-t0, 's')
                        t0 = time.time()
                        isDrowning = False

                    else:
                        print(x-t0, 's')
                        if((time.time() - t0) > 10):
                            isDrowning = True    
                            
                    print('bbox: ', bbox, 'centre:', centre, 'centre0:', centre0)
                    print('Is he drowning: ', isDrowning)                   

                    centre0 = centre                   

            out = draw_bbox(frame, bbox, label, conf,isDrowning)
            cv2.imwrite('image.jpg',out)
                
            cv2.imshow("Real-time object detection", out)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        webcam.release()
        cv2.destroyAllWindows()
    return render_template('prediction.html')

if __name__=="__main__":
   app.run(debug=True)



