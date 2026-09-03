from flask import Flask, send_from_directory

# This tells Flask to serve everything in the root folder automatically!
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

# This maps /models/ requests straight to your singular 'model' folder
@app.route('/models/<path:filename>')
def serve_models(filename):
    return send_from_directory('model', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
