import os
from flask import Flask, jsonify, make_response, redirect, render_template, request, url_for
from io import StringIO

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/database')
@app.route('/database/<table_name>')
def debug_database(table_name=None):
    query_results = None
    if table_name:
        #query_results = fetch_table(table_name)
        query_results = [['this', 'is', 'a', 'sample', 'db', 'response']] + [[*'abcdef']] * 500
    return render_template('debug_database.html', table_name=table_name, query_results=query_results)


@app.route('/database/<table_name>/upload', methods=['GET', 'POST'])
def debug_database_upload(table_name):
    if request.method == 'POST':
        f = request.files['file']
        print('get file:', f.filename)
        #upload_table(f)
        return jsonify([f.filename])
    return redirect(url_for('debug_database', table_name=table_name))


@app.route('/database/<table_name>/download')
def debug_database_download(table_name=None):
    if table_name:
        #download_table(table_name)
        pass
    
    csv_fname = table_name + '.csv'
    with open(os.path.join('static', csv_fname), 'w', encoding='utf-8') as f:
        f.write("foo|bar|baz\neggs|ham|spam")
        
    return redirect(url_for('static', filename=csv_fname))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    # https://stackoverflow.com/a/17276310
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)