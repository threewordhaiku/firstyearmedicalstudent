# Standard libary
import os

# Third-party modules
from flask import Flask, jsonify, make_response, redirect, render_template, \
                  request, url_for

# Local modules
from db_tools.db_downup import download_table, fetch_table, upload_table

app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/database')
@app.route('/database/<table_name>')
def debug_database(table_name=None):
    query_results = []
    if table_name:
        query_results = fetch_table(table_name)
        #query_results = [['this', 'is', 'a', 'sample', 'db', 'response']] + [[*'abcdef']] * 500

    return render_template('debug_database.html', 
                           table_name=table_name, 
                           query_results=query_results)


@app.route('/database/<table_name>/upload', methods=['GET', 'POST'])
def debug_database_upload(table_name=None):
    if (not table_name) or (request.method == 'GET'):
        return redirect(url_for('debug_database', table_name=table_name))    
    
    f = request.files['file']
    print('get file:', f.filename)
    upload_table(table_name, f)
    # return json response to trigger JavaScript `done` callback
    return jsonify([f.filename])


@app.route('/database/<table_name>/download')
def debug_database_download(table_name=None):
    if (not table_name):
        return redirect(url_for('debug_database', table_name=table_name))    
    
    output = download_table(table_name)
    csv_fname = table_name + '.csv'
    with open(os.path.join('static', csv_fname), 'w', encoding='utf-8') as f:
        f.write(output)
    return redirect(url_for('static', filename=csv_fname))


if __name__ == '__main__':
    # Bind to env var PORT if defined, otherwise default to 5000.
    # https://stackoverflow.com/a/17276310
    port = int(os.environ.get('PORT', 5000))

    # Figure out if debugging is wanted
    debugging = int(os.environ.get('FLASK_DEBUG', 0))
    host = '127.0.0.1' if debugging else '0.0.0.0'

    app.run(host=host, port=port)