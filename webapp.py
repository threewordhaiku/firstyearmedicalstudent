import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/database')
@app.route('/database/<table_name>')
def show_debug_database(table_name=None):
    query_results = None
    if table_name:
        query_results = [['this', 'is', 'a', 'sample', 'db', 'response']] + [[*'abcdef']] * 500

    return render_template('debug_database.html', table_name=table_name, query_results=query_results)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    # https://stackoverflow.com/a/17276310
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)