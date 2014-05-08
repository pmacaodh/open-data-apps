# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 20:44:32 2014

@author: paul
"""

import requests
import requests_cache
import dateutil
import datetime
import pandas as pd
from matplotlib import pyplot as plt

requests_cache.install_cache('sbb_transport')
# Sample of first monday of 2014
sampledate = datetime.date(2014,1,6)
sampletime = datetime.time(8,30)

destination = 'Zurich HB'
origins = ['Baden','Spreitenbach','Dietikon','Schlieren','Altstetten',
           'Watt','Regensdorf',u'Zürich-Affoltern','Dielsdorf',
           'Oerlikon', 'Opfikon','Kloten',u'Bülach',
           'Wallisellen', u'Brüttisellen', 'Effretikon','Winterthur',
           u'Dübendorf','Volketswil','Uster',
           'Zollikon', u'Küsnacht','Meilen',
           'Kilchberg','Thalwil','Horgen',u'Wädenswil',
           'Adliswil','Zug',
           'Birmensdorf','Bonstetten','Affoltern am Albis', 'Cham',
           'Bremgarten','Wohlen'
           ]
# Fillers to help contour
origins += ['Brugg','Lenzburg','Muri','Arth','Wollerau',u'Stäfa',
            'Wetzikon','Eglisau','Seuzach','Hinwil']

def get_location( query, x=None, y=None, loc_type='all'):
    """
    query:	required	Specifies the location name to search for	Basel
    x:	optional	Latitude	47.476001
    y:	optional	Longitude	8.306130
    type:	optional	 Specifies the location type, possible types are:
        all (default): Looks up for all types of locations
        station: Looks up for stations (train station, bus station)
        poi: Looks up for points of interest (Clock tower, China garden)
        address: Looks up for an address (Zurich Bahnhofstrasse 33)    
    """
    url = u'http://transport.opendata.ch/v1/locations'
    url+= u"?query={}".format(query)
    url+= u"&x={}".format(x) if x else u""
    url+= u"&y={}".format(y) if y else u""
    url+= u"&type={}".format(loc_type) if loc_type else u""
    
    r = requests.get(url)
    return r.json()
    
def get_connection( loc_from, loc_to, via=None, date=None, time=None, is_arrival_time=False):
    """
    from	required	Specifies the departure location of the connection	Lausanne
    to	required	Specifies the arrival location of the connection	Genève
    via	optional	Specifies up to five via locations. When specifying several vias, array notation (via[]=via1&via[]=via2) is required.	Bern
    date	optional	Date of the connection, in the format YYYY-MM-DD	2012-03-25
    time	optional	Time of the connection, in the format hh:mm	17:30
    isArrivalTime	optional	defaults to 0, if set to 1 the passed date and time is the arrival time	1
    
    """
    url = u'http://transport.opendata.ch/v1/connections'
    url+= u"?from={}&to={}".format(loc_from, loc_to)
    if via: url+= u"&via={}".format(via)
    if date: url+= u"&date={}".format(date)
    if time: url+= u"&time={}".format(time)
    if is_arrival_time: url+= u"&isArrivalTime=true"

    r = requests.get(url)
    try:
        rjson = r.json()
    except:
        rjson = []
    return rjson
    
def connection_duration(connection):
    """ Compute duration from arrival and departure times
    """
    a = connection['to']['arrival']
    d = connection['from']['departure']
    a = dateutil.parser.parse(a)
    d = dateutil.parser.parse(d)
    return a-d

def get_data(origins):
    results = dict()
    for origin in origins:
        print origin
    #origin, lat, lon, destination, lat, lon, duration
        conns = get_connection(origin,
                              destination,
                              sampledate,
                              sampletime,
                              is_arrival_time=True
                              )
        # Duration
        durations = [connection_duration(c) for c in conns['connections']]
        if not durations:
            continue
        duration = min(durations)
        # Coords, from
        o_coords = conns['from']['coordinate']
        d_coords = conns['to']['coordinate']
        results[origin] = dict(destination=destination,
                               d_lat=d_coords['y'],
                               d_lon=d_coords['x'],
                               o_lat=o_coords['y'],
                               o_lon=o_coords['x'],
                               duration=duration
                               )
    data = pd.DataFrame(results).T
    #mins = lambda dt:dt/np.timedelta64(1,'m')
    mins = lambda dt:dt.total_seconds()/60
    data['minutes'] = data['duration'].apply(mins)
    return data
    
# bar chart of minutes
#duration = data['minutes'].copy()
#duration.sort()
#duration.plot(kind='bar')

# contour map with labels
from scipy.interpolate import griddata
import numpy as np

def plot_map(data, method='nearest'):
    lon_min = data['o_lon'].min()
    lon_max = data['o_lon'].max()
    lat_min = data['o_lat'].min()
    lat_max = data['o_lat'].max()
    xi = np.linspace(lon_min,lon_max,500)
    yi = np.linspace(lat_min,lat_max,500)
    x = data['o_lon']
    y = data['o_lat']
    z = data['minutes']
    
    zi = griddata((x,y), z, (xi[None,:], yi[:,None]), method)
    levels = np.arange(5,20,1)
    #CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
    CS = plt.contourf(xi,yi,zi,levels,cmap=plt.cm.jet)
    plt.colorbar()
    plt.title('Minimum Connection Time to Zurich HB (minutes)')
    ax = plt.scatter(x,y)
    for x,y,label in zip(x,y,x.index.values):
        plt.text(x,y,label)