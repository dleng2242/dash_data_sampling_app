
# Plotly Dash Data Sampling App

This repo contains a simple demo Plotly Dash app that draws a sample of 
data from the Old Faithful dataset and presents the same sample to multiple
outputs using in-browser storing of data, including a histogram, a table, 
and also the option to download the sample.

## Quick Start

Clone this repo and recreate the virtual environnement using the 
`requirements.txt` file with `pip install -r requirements.txt`. 

To run the app, activate your virtual environment, run the following, 
and navigate to http://127.0.0.1:8050/ in your browser. 

```
python app.py
```

## Docker Quick Start

Build the image from the Dockerfile with `docker build -t dash_sampling:0.1 .`

Then run it using `docker run -d -p 8050:8050 dash_sampling:0.1`.

## Resources

* [Dash in 20 Minutes](https://dash.plotly.com/tutorial)
* [Sharing Data Between Callbacks](https://dash.plotly.com/sharing-data-between-callbacks)

