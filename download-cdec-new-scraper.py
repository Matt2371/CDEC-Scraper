import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import requests
import lxml.html as lh
from bs4 import BeautifulSoup



# create URL from input info
# assumes only one station and sensor per request
def build_url(station='', sensor='', duration='D', sd='', ed=''):

  sensordf = pd.read_csv('sensorid.csv')
  sensordict = {}
  for i in range(len(sensordf['Sensornum'])):
    sensordict[sensordf.loc[i].Sensor] = sensordf.loc[i].Sensornum
  #builds dictionary between variable type and sensor number


  station = input('Enter a station ID')
  sensor = input('Enter sensor number or variable type(in CAPS)')
  duration = input('Enter duration code(H-hourly, D-daily, M-monthly)')
  sd = input('Enter start date (yyyy-mm-dd)')
  ed = input('Enter end date (yyyy-mm-dd) ')
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

# def get_df(url, table = str(1)):
#
#
#   # Create a handle, page, to handle the contents of the website
#   page = requests.get(url)
#   # Store the contents of the website under doc
#   doc = lh.fromstring(page.content)
#   # Parse data that are stored between <tr>..</tr> of HTML
#   tr_elements = doc.xpath('//tr')
#
#
#
#   # Create empty list
#   col = []
#   i = 0
#   # For each row, store each first element (header) and an empty list
#   for t in tr_elements[0]:
#     i += 1
#     name = t.text_content()
#     #print ('%d:"%s"' % (i, name))
#     col.append((name, []))
#
#
#   # Since out first row is the header, data is stored on the second row onwards
#   for j in range(1, len(tr_elements)):
#     # T is our j'th row
#     T = tr_elements[j]
#
#     # If row is not of size second row, the //tr data is not from our table
#     if len(T) != len(tr_elements[1]):
#       break
#
#     # i is the index of our column
#     i = 0
#
#     # Iterate through each element of the row
#     for t in T.iterchildren():
#       data = t.text_content()
#       # Check if row is empty
#       # if i > 0:
#       #   # Convert any numerical value to float
#       #   try:
#       #     data = float(data)
#       #   except:
#       #     pass
#
#       # Append the data to the empty list of the i'th column
#       col[i][1].append(data)
#       # Increment i for the next column
#       i += 1
#
#
#   #create dataframe
#   Dict = {title: column for (title, column) in col}
#   df = pd.DataFrame(Dict)
#   print(df)
#   return df

# scrapes and prints table from url
def get_df(url, nodf):
  res = requests.get(url)
  soup = BeautifulSoup(res.content, 'lxml')
  table = soup.find_all('table')[nodf]
  df = pd.read_html(str(table))
  print(df)
  # print(tabulate(df[0], headers='keys', tablefmt='psql'))



def sensor_stations(): #get stations for particular sensor
  #get dict
  sensordf = pd.read_csv('sensorid.csv')
  sensordict = {}
  for i in range(len(sensordf['Sensornum'])):
    sensordict[sensordf.loc[i].Sensor] = sensordf.loc[i].Sensornum
  sensor = input('Enter sensor number or variable type(in CAPS)')
  if sensor.isdigit() == False:
    sensor = int(sensordict[sensor])
  else:
    sensor = int(sensor)
  #get df from url
  url = 'http://cdec.water.ca.gov/dynamicapp/staSearch?sta=&sensor_chk=on&sensor='+str(sensor)+'&collect=NONE+SPECIFIED&dur=&active=&lon1=&lon2=&lat1=&lat2=&elev1=-5&elev2=99000&nearby=&basin=NONE+SPECIFIED&hydro=NONE+SPECIFIED&county=NONE+SPECIFIED&agency_num=160&display=sta'
  get_df(url, 0)
  return


def station_sensors(): #get sensor for particular station
  station = input('Enter a station ID: ')
  url = 'http://cdec.water.ca.gov/dynamicapp/staMeta?station_id='+station
  get_df(url, 1)
  return




print('Menu: ')
print('1 - Get data from station')
print('2 - Get all stations with sensor type')
print('3 - Get all sensors types from station')
option = input('Enter an option: ')

if option == '1':
  url = build_url()
  df = pd.read_csv(url)
  series = reformat_series(df)
  print(series)
elif option == '2':
  sensor_stations()
elif option == '3':
  station_sensors()
else:
  print('Please enter a valid option')



