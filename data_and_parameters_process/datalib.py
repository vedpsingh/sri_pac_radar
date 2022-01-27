import math
import matplotlib.pyplot as plt
import pandas
import numpy
import pickle

class Data:
    def __init__(self):
        pass

# Loading and saving functions

    def set_file(self, file_content):
        self.file_content = file_content['data']
    
    def save_pickle(self, pickle_name):
        self.to_cart()
        with open(pickle_name, 'wb') as fp:
            pickle.dump(self.cartesian_coord,fp)
    
    def load_pickle(self, pickle_name):
        with open(pickle_name,'rb') as fp:
            self.cartesian_coord = pickle.load(fp)

# Call parameter functions

    def parameters(self,x,y):
        self.get_close_all_elev(x,y)
        self.close_data
        self.find_points(x,y)
        self.param = {}
        self.bright_points_fun()
        self.average_echo()
        self.mean_velocity_and_width()
        self.lowest_elevation()
        return self.param
    
# Parameter Calculation Functions

    def bright_points_fun(self):
        self.points = sorted(self.points, key = lambda i: i['Z'])
        self.bright_points = []
        flag = True
        for point in self.points:
            if point is None:
                continue
            if point['DBZ']>0:
                if point['Z']<25:
                    self.bright_points.append(point)
                    flag = True
                elif flag:
                    self.bright_points.append(point)
                    flag = False
                else:
                    break
            elif point['Z']>25:
                break
        if len(self.bright_points) == 0:
            self.param['base_of_brightest_echo'] = -1  
            self.param['height_of_brightest_echo'] = -1  
            return
        brightest_point = self.bright_points[0]
        for point in self.bright_points:
            if point['DBZ']>=brightest_point['DBZ']:
                brightest_point = point
        flag = True
        for point in self.bright_points:
            if flag and point['DBZ']>=(brightest_point['DBZ']-5):
                self.param['base_of_brightest_echo'] = point['Z']
                flag = False
            if point['DBZ']>=(brightest_point['DBZ']-2.5):
                self.param['height_of_brightest_echo'] = point['Z']
        self.param['brightest_ref'] = brightest_point['DBZ']
    
    def average_echo(self):
        if self.bright_points == []:
            self.param['average_echo_depth'] = 0.0
            return
        average_echo = 0
        n = len(self.bright_points)
        for point in self.bright_points:
            average_echo += 10**(point['DBZ']/10)
        average_echo /= n
        average_echo = 10*(math.log10(average_echo))
        self.param['average_echo'] = average_echo
        average_threshold = average_echo-5
        average_points = []
        for point in self.bright_points:
            if point['DBZ']>=average_threshold:
                average_points.append(point)
        self.param['average_echo_depth'] = average_points[-1]['Z']-average_points[0]['Z']
    
    def mean_velocity_and_width(self):
        mean_vel = 0
        mean_width = 0
        number_of_points = 0
        for point in self.points:
            if point is None:
                continue
            if point['Z']>3:
                break
            temp_vel = 10**(point['DBVEL']/10)
            if math.isnan(temp_vel):
                temp_vel = 0
            mean_vel += temp_vel
            mean_width += 10**(point['DBWIDTH']/10)
            number_of_points += 1
        mean_vel /= number_of_points # log scale
        # mean_vel = 10*(math.log10(mean_vel))
        mean_width /= number_of_points
        # mean_width = 10*(math.log10(mean_width))
        self.param['mean_velocity'] = mean_vel
        self.param['mean_Turbulence'] = mean_width
        
    def lowest_elevation(self):
        self.param['lowest_elevation_ref'] = self.points[0]['DBZ']

# Get points in all elevations

    def find_points(self,x, y):
        points = []
        for elevation in self.close_data:
            ind = []
            maxe = 10 #name
            for i,point in elevation.iterrows():
                if abs(x-point['X'])<=1 or abs(y-point['Y'])<=1:
                    e = (x-point['X'])**2 + (y-point['Y'])**2
                    if e<maxe:
                        maxe = e
                        ind = []
                        ind.append(i)
                    elif(e==maxe):
                        ind.append(i)
            if len(ind)==1:
                points.append(elevation.iloc[ind[0]].to_dict())
            elif len(ind)>1:
                mean = {'X':0,'Y':0,'Z':0,'DBZ':0,'DBVEL':0,'DBWIDTH':0}
                count = 0
                for i in ind:
                    count+=1
                    point = elevation.iloc[i].to_dict()
                    mean = self.add_points(mean,point)
                mean = self.average_mean(mean,count)
                points.append(mean)
            else:
                points.append(None)
        self.points = points

    def get_close_all_elev(self, x, y):
        self.close_data = []
        for i,elev in enumerate(self.cartesian_coord):
            x_dat = self.get_close(elev, x, 'X')
            y_dat = self.get_close(x_dat, y, 'Y')
            index = pandas.Index(list(range(y_dat.shape[0])))
            y_dat.index = index
            self.close_data.append(y_dat)
    
    def get_close(self, data, x, key):
        data = data.sort_values([key],ascending=True)
        hi = data.shape[0]
        lo = 0
        mid = -1
        while(lo<hi):
            mid = int((hi+lo)/2)
            val = data.iloc[mid][key]
            if abs(val-x)<2:
                break
            else:
                if x>val:
                    lo = mid
                else:
                    hi = mid
        lo = mid
        hi = mid
        while(True):
            if abs(data.iloc[lo][key]-x)<2:
                lo-=1
            else:
                break
        while(True):
            if abs(data.iloc[hi][key]-x)<2:
                hi+=1
            else:
                break
        return data.iloc[lo:hi+1,:]

# Get data in cartesian format

    def to_cart(self):
        fcontent = self.file_content
        cart = []
        for key1 in fcontent:#10 readings at different elevations
            sweep_reading = fcontent[key1]['sweep_data']
            db_vel = sweep_reading['DB_VEL']#extract only dbvel data from reading
            db_dbz = sweep_reading['DB_DBZ']#extract only dbz data from reading
            db_width = sweep_reading['DB_WIDTH']
            if db_dbz['azi_start'][0]>1:
                db_dbz['azi_start'][0]-=360
            dbz = pandas.DataFrame.from_dict({'azi_start':db_dbz['azi_start'],'azi_stop':db_dbz['azi_stop'],'ele_start':db_dbz['ele_start'],'ele_stop':db_dbz['ele_stop']})#convert dbz data to dataframe
            dbz['azi_mean'] = dbz[['azi_start','azi_stop']].mean(axis=1)#compute mean of azi
            dbz['ele_mean'] = dbz[['ele_start','ele_stop']].mean(axis=1)#compute mean of ele
            dbz['azi_mean'] = dbz['azi_mean'].apply(self.convert_radian)#convert mean from degree to radian
            dbz['ele_mean'] = dbz['ele_mean'].apply(self.convert_radian)#convert mean from degree to radian
            dbz_data = db_dbz['data']#extract data list (2-d) (360x500)
            dbvel_data = db_vel['data']#extract data list (2-d) (360x500)
            dbwidth_data = db_width['data']
            # dbz_data = np.round(db_dbz['data'], 4)#extract data list (2-d) (360x500)
            # dbvel_data = np.round(db_vel['data'], 4)#extract data list (2-d) (360x500)
            # dbwidth_data = np.round(db_width['data'], 4)
            x,y,z,dbz_v,dbvel_v,dbwidth_v = [],[],[],[],[],[]#declare lists for coordinates and values
            for j in range(len(dbz_data)):
                azi = dbz['azi_mean'][j]#read azi for particular ray
                ele = dbz['ele_mean'][j]#read ele for particular ray
                dbzvalue = dbz_data[j]
                dbvelvalue = dbvel_data[j]
                dbwidthvalue = dbwidth_data[j]
                for k in range(len(dbzvalue)):#process all (500) reading of particular ray
                    i = k*0.5
                    Z = i*math.sin(ele)
                    Y = i*math.cos(ele)*math.cos(azi)
                    X = i*math.cos(ele)*math.sin(azi)
                    x.append(X)
                    y.append(Y)
                    z.append(Z)
                    dbz_v.append(dbzvalue[k])
                    if dbvelvalue[k] < -47:
                        dbvel_v.append(0)
                    else:
                        dbvel_v.append(float(dbvelvalue[k]))
                    dbwidth_v.append(dbwidthvalue[k])
            cart.append(pandas.DataFrame({'X':x,'Y':y,'Z':z,'DBZ':dbz_v,'DBVEL':dbvel_v,'DBWIDTH':dbwidth_v}))
        self.cartesian_coord = cart

# Utility Functions

    def convert_radian(self, angle):
        angle*= math.pi/180
        return angle
    
    def plot(self):
        df = self.cartesian_coord
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter3D(df['X'], df['Y'], df['Z'], marker = 1)
        fig.show()

    def add_points(self,m,point):
        keys = m.keys()
        for k in keys:
            if k.startswith('DB'):
                m[k]+=10**(point[k]/10)
            else:
                m[k]+=point[k]
        return m

    def average_mean(self,m,count):
        keys = m.keys()
        for k in keys:
            if k.startswith('DB'):
                m[k] = 10*(math.log10(m[k]/count))
            else:
                m[k] = m[k]/count
        return m