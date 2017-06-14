from flask import Flask, render_template, request, redirect

import bokeh
import requests
import json
import pandas as pd


# bokeh / flask imports
import flask
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.resources import INLINE
#from bokeh.util.string import encode_utf8
import os

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

app.vars = {}

@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')  
    else:
        app.vars['ticker'] = request.form['ticker']
        app.vars['features'] = request.form.getlist('features')
        ticker = app.vars['ticker']
        closing = 'Close' in app.vars['features']
        opening = 'Open' in app.vars['features']
        volume = 'Volume' in app.vars['features']
 
        r = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?order=asc' + 'wpAG5_BdecqoADP7-Dtx')
        parsed_json = json.loads(r.text)
        df = pd.DataFrame(parsed_json['dataset']['data'])
        df.columns = parsed_json['dataset']['column_names']
        df['Date'] = pd.to_datetime(df['Date'])
        company = parsed_json['dataset']['name']
        company = company.split('(')
        company = company[0]
        
        def generate_close(ticker, closing):
            if closing:
                return plot.line(df['Date'], df['Close'], color='#0000FF', legend=ticker+": Close")
        def generate_open(ticker,opening):
            if opening:
                return plot.line(df['Date'], df['Open'], color='#009933', legend=ticker+": Open")            
        def generate_volume(ticker, volume):
            if volume:
                return plot.line(df['Date'], df['Volume'], color='#CC3300', legend=ticker+": Volume")
                
#        output_file("stockplot.html", title=company)
       
                
        plot = figure(tools="pan,wheel_zoom,box_zoom,reset",
              title='Data from Quandle WIKI set',
              x_axis_label='date',
              x_axis_type='datetime')
        
        generate_close(ticker, closing)
        generate_open(ticker, opening)
        generate_volume(ticker, volume)
        
        bokeh.io.output_file('templates/plotstock.html')
        bokeh.io.save(plot)
        
        script, div = components(plot, INLINE)
        return render_template('plot.html', script=script, div=div, company=company, ticker=ticker)
        #return render_template('index.html')



    
if __name__ == '__main__':
    app.run(port=33507)
