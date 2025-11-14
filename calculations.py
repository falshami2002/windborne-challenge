import numpy as np

def haversine_vec(lat1, lon1, lat2, lon2):
    ''' This function accounts for the curvature of the Earth to compute the vector between two points in terms of latitude and longitude '''
    R = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dl   = np.radians(lon2-lon1)
    a = np.sin(dphi/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

def ground_vector(lat1, lon1, lat2, lon2, dt_sec):
    ''' Calculate the vector from the position of the baloon to the next one an hour later '''
    d = haversine_vec(lat1, lon1, lat2, lon2)
    spd = d / dt_sec
    y = np.sin(np.radians(lon2-lon1)) * np.cos(np.radians(lat2))
    x = np.cos(np.radians(lat1))*np.sin(np.radians(lat2)) - \
        np.sin(np.radians(lat1))*np.cos(np.radians(lat2))*np.cos(np.radians(lon2-lon1))
    brg = (np.degrees(np.arctan2(y, x)) + 360) % 360
    vx = spd * np.sin(np.radians(brg))  
    vy = spd * np.cos(np.radians(brg))  
    return vx, vy, spd, brg

def wind_vector(speed_ms, dir_deg):
    ''' In meteorolgy, wind direction is the direction from which the wind is coming, but we need it to be the direction to which it is going '''
    to_deg = (dir_deg + 180) % 360
    wx = speed_ms * np.sin(np.radians(to_deg))  
    wy = speed_ms * np.cos(np.radians(to_deg))  
    return wx, wy