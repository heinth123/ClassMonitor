from flask import Flask, send_from_directory

app = Flask(__name__)

# This serves your main game page right from your root folder safely
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# This maps /models/ requests straight to your 'model' folder
@app.route('/models/<path:filename>')
def serve_models(filename):
    return send_from_directory('model', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
