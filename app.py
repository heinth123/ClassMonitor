from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# This catches requests for /models/ and pulls them straight from your 'model' folder!
@app.route('/models/<path:filename>')
def serve_models(filename):
    return send_from_directory('model', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
