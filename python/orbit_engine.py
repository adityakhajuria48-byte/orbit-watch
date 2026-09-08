"""SGP4 ground-track pass predictions, shared by CPython and browser Pyodide.
Times are Unix milliseconds; distances use WGS84 subpoints and a mean-Earth sphere.
"""
import json
import math
from datetime import datetime, timezone
from sgp4.api import Satrec
from sgp4 import omm
from sgp4.propagation import gstime

EARTH_KM = 6371.0088

def epoch_ms(value):
    return datetime.fromisoformat(value.rstrip('Z')).replace(tzinfo=timezone.utc).timestamp()*1000

def satellite(row):
    fields = dict(row)
    fields['EPOCH'] = fields['EPOCH'].rstrip('Z')
    fields.setdefault('CLASSIFICATION_TYPE', 'U')
    fields.setdefault('EPHEMERIS_TYPE', 0)
    fields.setdefault('ELEMENT_SET_NO', 999)
    fields.setdefault('REV_AT_EPOCH', 0)
    sat = Satrec()
    omm.initialize(sat, fields)
    return sat

def position(sat, time_ms):
    jd = time_ms / 86400000 + 2440587.5
    whole = math.floor(jd)
    error, r, _ = sat.sgp4(whole, jd-whole)
    if error or not all(math.isfinite(x) for x in r):
        return None
    x,y,z = r
    theta = gstime(jd)
    lon = (math.atan2(y,x)-theta+math.pi) % (2*math.pi)-math.pi
    horizontal = math.hypot(x,y)
    lat = math.atan2(z,horizontal)
    e2 = 0.00669437999014
    for _ in range(10):
        n = 6378.137/math.sqrt(1-e2*math.sin(lat)**2)
        lat = math.atan2(z+e2*n*math.sin(lat),horizontal)
    return {'lat':math.degrees(lat),'lon':math.degrees(lon)}

def distance(a,b):
    p,q = math.radians(a['lat']),math.radians(b['lat'])
    d = math.radians(b['lon']-a['lon'])
    h = math.sin((q-p)/2)**2 + math.cos(p)*math.cos(q)*math.sin(d/2)**2
    return EARTH_KM*2*math.asin(math.sqrt(min(1,max(0,h))))

def pass_intervals(distance_at, start, end, radius, step=30000):
    """Refine local minima as well as sampled entries, retaining grazing passes.
    Returned boundary-clipped durations are explicitly marked as lower bounds.
    Numerical boundaries are refined to < 0.25s, not an accuracy guarantee.
    """
    times = list(range(int(start),int(end),step))+[int(end)]
    ds = [distance_at(t) for t in times]
    candidates = [(t,d) for t,d in zip(times,ds) if d<=radius]
    brackets = [(times[i-1],times[i+1]) for i in range(1,len(times)-1)
                if ds[i]<=ds[i-1] and ds[i]<=ds[i+1]]
    # A minimum inside the first/last interval need not be a sampled local minimum.
    if len(times)>1:
        brackets.extend([(times[0],times[1]),(times[-2],times[-1])])
    for l,r in brackets:
        for _ in range(23):
            a,b=l+(r-l)/3,r-(r-l)/3
            if distance_at(a)<distance_at(b):r=b
            else:l=a
        t=(l+r)/2;d=distance_at(t)
        if d<=radius:candidates.append((t,d))
    result=[]
    for t,d in sorted(candidates):
        if result and t<=result[-1]['exit']+250:continue
        left=t
        while left>start and distance_at(left)<=radius:left=max(start,left-step)
        right=t
        while right<end and distance_at(right)<=radius:right=min(end,right+step)
        clipped_start=left==start and distance_at(start)<=radius
        clipped_end=right==end and distance_at(end)<=radius
        def boundary(outside,inside):
            while abs(outside-inside)>250:
                mid=(outside+inside)/2
                if distance_at(mid)<=radius:inside=mid
                else:outside=mid
            return inside
        enter=start if clipped_start else boundary(left,t)
        leave=end if clipped_end else boundary(right,t)
        l,r=enter,leave
        for _ in range(24):
            a,b=l+(r-l)/3,r-(r-l)/3
            if distance_at(a)<distance_at(b):r=b
            else:l=a
        closest=(l+r)/2
        result.append({'entry':round(enter),'exit':round(leave),'closestTime':round(closest),
                       'closestKm':distance_at(closest),'durationSeconds':(leave-enter)/1000,
                       'clippedStart':clipped_start,'clippedEnd':clipped_end})
    return result

def predict_one(row, loc, radius, start, end):
    if abs(start-epoch_ms(row['EPOCH']))>7*86400000:
        return {'passes':[], 'skipped':1}
    sat=satellite(row)
    def d(t):
        if abs(t-epoch)>7*86400000:return math.inf
        p=position(sat,t)
        return distance(loc,p) if p else math.inf
    epoch=epoch_ms(row['EPOCH'])
    passes=pass_intervals(d,start,end,radius)
    for p in passes:p.update(id=str(row['NORAD_CAT_ID']),name=str(row['OBJECT_NAME']),epoch=epoch)
    return {'passes':passes,'skipped':0}

def predict_json(payload):
    p=json.loads(payload)
    try:
        result=predict_one(p['row'],p['loc'],p['radius'],p['start'],p['end'])
    except (ValueError,TypeError,KeyError,OverflowError):
        result={'passes':[], 'skipped':1}
    return json.dumps(result,allow_nan=False)

if __name__=='__main__':
    import argparse,time
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog');parser.add_argument('--lat',type=float,required=True);parser.add_argument('--lon',type=float,required=True)
    parser.add_argument('--radius',type=float,default=45);parser.add_argument('--hours',type=float,default=6);parser.add_argument('--ids',default='25544,20580,49260')
    a=parser.parse_args()
    if not (-90<=a.lat<=90 and -180<=a.lon<=180 and 10<=a.radius<=1000 and 0<a.hours<=24):parser.error('Coordinates, radius or hours out of range')
    start=time.time()*1000;events=[]
    for row in json.load(open(a.catalog)):
        if str(row['NORAD_CAT_ID']) in a.ids.split(','):events.extend(predict_one(row,{'lat':a.lat,'lon':a.lon},a.radius,start,start+a.hours*3600000)['passes'])
    print(json.dumps(sorted(events,key=lambda x:x['entry']),indent=2))
