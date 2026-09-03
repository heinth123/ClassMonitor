from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/models/<path:filename>')
def serve_models(filename):
    return send_from_directory('model', filename)

@app.route('/<path:filename>')
def serve_any_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
