import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import requests
import lxml.html as lh
from bs4 import BeautifulSoup



# create URL from input info
# assumes only one station and sensor per request
def build_url(station=None, sensor=None, duration=None, sd=None, ed=None):

  sensordf = pd.read_csv('sensorid.csv')
  sensordict = {}
  for i in range(len(sensordf['Sensornum'])):
    sensordict[sensordf.loc[i].Sensor] = sensordf.loc[i].Sensornum
  #builds dictionary between variable type and sensor number

  #if no parameters, ask for input
  if station==None and sensor==None and duration==None and sd == None and ed==None:
    station = input('Enter a station ID: ')
    sensor = input('Enter sensor number or variable type(in CAPS): ')
    duration = input('Enter duration code(H-hourly, D-daily, M-monthly): ')
    sd = input('Enter start date (yyyy-mm-dd): ')
    ed = input('Enter end date (yyyy-mm-dd): ')
  if sensor.isdigit() == False:
      sensor = int(sensordict[sensor])
  else:
    sensor = int(sensor)
  #gets user inputs

  url = 'http://cdec.water.ca.gov/dynamicapp/req/CSVDataServlet?'
  url += 'Stations=%s' % station
  url += '&SensorNums=%d' % sensor
  url += '&dur_code=%s' % duration
  url += '&Start=%s' % sd
  url += '&End=%s' % ed
  #print(url)
  return url

# takes df from one (station, sensor) request
# converts to a series indexed by datetime
def reformat_series(df):
  try:
    # reindex by datetime
    df['DATE TIME'] = pd.to_datetime(df['DATE TIME'])
    df.set_index('DATE TIME', inplace=True)
    df.index.rename('datetime', inplace=True)

    # keep just the "VALUE" column and rename it
    name = '%s_%s_%s' % (df['STATION_ID'][0], df['SENSOR_TYPE'][0], df['UNITS'][0])
    df = df['VALUE']
    df.rename(name, inplace=True)
  except IndexError: #empty data frame causes indexerror
    raise IndexError('Requested data does not exist')
  return df

#gets data from a specific station and sensor type
def sensor_data(station=None, sensor=None, duration=None, sd=None, ed=None):
  url = build_url(station, sensor, duration, sd, ed)
  df = pd.read_csv(url)
  series = reformat_series(df)
  print(series)
  return series

# scrapes and prints table from url
def get_df(url, nodf):
  res = requests.get(url)
  soup = BeautifulSoup(res.content, 'lxml')
  table = soup.find_all('table')[nodf]
  df = pd.read_html(str(table))
  print(df)
  # print(tabulate(df[0], headers='keys', tablefmt='psql'))
  return df


def sensor_stations(sensor=None): #get stations for particular sensor
  #get dict
  sensordf = pd.read_csv('sensorid.csv')
  sensordict = {}
  for i in range(len(sensordf['Sensornum'])):
    sensordict[sensordf.loc[i].Sensor] = sensordf.loc[i].Sensornum
  if sensor==None: #if no parameter, ask for input
    sensor = input('Enter sensor number or variable type(in CAPS)')

  if sensor.isdigit() == False:
    sensor = int(sensordict[sensor])
  else:
    sensor = int(sensor)
  #get df from url
  url = 'http://cdec.water.ca.gov/dynamicapp/staSearch?sta=&sensor_chk=on&sensor='+str(sensor)+'&collect=NONE+SPECIFIED&dur=&active=&lon1=&lon2=&lat1=&lat2=&elev1=-5&elev2=99000&nearby=&basin=NONE+SPECIFIED&hydro=NONE+SPECIFIED&county=NONE+SPECIFIED&agency_num=160&display=sta'
  get_df(url, 0)
  return get_df(url,0)


def station_sensors(station=None): #get sensor for particular station
  if station==None: #ask for input if no parameters
    station = input('Enter a station ID: ')
  url = 'http://cdec.water.ca.gov/dynamicapp/staMeta?station_id='+station
  get_df(url, 1)
  return get_df(url, 1)


def save_csv(df, filename=None): #save results to csv
  if filename ==None:
    filename = input('Enter filename for saved csv, press enter to exit: ')
    if filename == '':
      pass
    else:
      df.to_csv(filename + '.csv')
  else:
    df.to_csv(filename + '.csv')
    return


def join_df(df1, df2): #function to merge two dataframes based on datetime
  new_df = pd.merge(df1, df2, on='datetime')
  return new_df



def menu():

  print('Menu: ')
  print('1 - Get data from station')
  print('2 - Get all stations with sensor type')
  print('3 - Get all sensors types from station')
  option = input('Enter an option: ')

  if option == '1':
    save_csv(sensor_data())
  elif option == '2':
    sensor_stations()
  elif option == '3':
    station_sensors()
  else:
    print('Please enter a valid option')


menu()

#SAMPLE CODE: get single df with daily inflow(76) , storage (15), and outflow (23)
# initial_df = sensor_data('SHA', sensor= '76', duration='D', sd='', ed='') #df with inflow
# add_sensors = ['15', '23'] #add storage and outflow data
# for i in add_sensors:
#   df = sensor_data('SHA', sensor= i, duration='D', sd='', ed='')
#   initial_df = join_df(initial_df, df) #combine df
#
# initial_df.to_csv('df.csv')



