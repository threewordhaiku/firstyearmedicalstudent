import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('index.html')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    # https://stackoverflow.com/a/17276310
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)