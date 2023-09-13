import os
import uuid
import flask
import numpy as np
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file, jsonify
from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ORI
# model = load_model(os.path.join(BASE_DIR , 'model.hdf5'))

# SUKMA
model = load_model(os.path.join(BASE_DIR, 'model-baru.keras'))


ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

# ORI
# classes = ['airplane' ,'automobile', 'bird' , 'cat' , 'deer' ,'dog' ,'frog', 'horse' ,'ship' ,'truck']


# SUKMA
# classes = ['Angka 0' ,'Angka 1', 'Angka 2' , 'Angka 3' , 'Angka 4' ,'Angka 5' ,'Angka 6', 'Angka 7' ,'Angka 8' ,'Angka 9']
classes = ['Kubis Rusak', 'Kubis Sehat']


def predict(filename, model):
    img = load_img(filename, target_size=(28, 28), color_mode="grayscale")
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(2):
        # Store with class names as keys
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:2]

    prob_result = []
    class_result = []
    for i in range(2):
        prob_result.append((prob[i]*10).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')

    tindakan_rusak = ['Kasih Pestisida', 'Kasih Makan', 'Jangan A']
    tindakan_sehat = ['Pertahankan Pestisida',
                      'Pertahankan Makan', 'Pertahankan A']

    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                # if class_result[0] == 'Kubis Sehat':
                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    # "class3":class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    # "prob3": prob_result[2],
                }
                # else:
                #     predictions = {
                #         "class1": class_result[0],
                #         "class2": class_result[1],
                #         # "class3":class_result[2],
                #         "prob1": prob_result[0]*10,
                #         "prob2": prob_result[1]*10,
                #         # "prob3": prob_result[2],
                #     }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    # "class3":class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    # "prob3": prob_result[2],
                }
            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

    else:
        return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predictAndroid():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')

    tindakan_rusak = ['Kasih Pestisida', 'Kasih Makan', 'Jangan A']
    tindakan_sehat = ['Pertahankan Pestisida',
                      'Pertahankan Makan', 'Pertahankan A']

    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                if class_result[0] == 'Kubis Sehat':
                    predictions = {
                        "class1": class_result[0],
                        # "class2":class_result[1],
                        # "class3":class_result[2],
                        "prob1": tindakan_sehat,
                        # "prob2": prob_result[1],
                        # "prob3": prob_result[2],
                    }
                else:
                    predictions = {
                        "class1": class_result[0],
                        # "class2":class_result[1],
                        # "class3":class_result[2],
                        "prob1": tindakan_rusak,
                        # "prob2": prob_result[1],
                        # "prob3": prob_result[2],
                    }

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions)
            else:
                return render_template('index.html', error=error)

        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                if class_result[0] == 'Kubis Sehat':
                    predictions = {
                        "class1": class_result[0],
                        # "class2": class_result[1],
                        # "class3":class_result[2],
                        # "prob1": prob_result[0],
                        "prob1": tindakan_sehat,
                        # "prob2": prob_result[1],
                        # "prob3": prob_result[2],
                    }
                else:
                    predictions = {
                        "class1": class_result[0],
                        # "class2": class_result[1],
                        # "class3":class_result[2],
                        "prob1": tindakan_rusak,
                        # "prob1": prob_result[0],
                        # "prob2": prob_result[1],
                        # "prob3": prob_result[2],
                    }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if (len(error) == 0):
                return jsonify({"status": "success", "prediksi": predictions})
            else:
                return jsonify({"status": 'error'})

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
