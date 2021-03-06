from flask import jsonify, Flask, render_template, send_file, url_for
from flask_restful import Resource, Api, reqparse
import werkzeug, os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='.')
api = Api(app)

# Configurationg
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = ['jpg']

# Flask restful file upload
parser = reqparse.RequestParser()
parser.add_argument('file',
    type=werkzeug.datastructures.FileStorage,
    location='files')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from qu import img_enqueue, fetch

class FileUpload(Resource):
    def post(self):
        data = parser.parse_args()
        if data['file'] == None:
            return "no file", 400
        file = data['file']
                        
        if file and allowed_file(file.filename):
            input_data = file.read()
            
            job = img_enqueue(input_data)
            return jsonify({'url': url_for('view', job_id=job.id)})
        else:
            return 'not allowed', 403

api.add_resource(FileUpload, '/upload')
from io import BytesIO
@app.route('/view/<string:job_id>')
def view(job_id):
    job = fetch(job_id)
    if job.get_status()=='finished':
        completed, data = job.result
        if completed:
            data = BytesIO(data)
            return send_file(data, mimetype='image/jpeg')
        else:
            return 'job failed in processing', 200
    else:
        return 'processing', 404

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
