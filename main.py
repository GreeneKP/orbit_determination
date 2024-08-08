"""
start demo with...
conda activate
Streamlit
streamlit run main.py
"""



#All imports first.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from requests import get
import time
from datetime import datetime, timedelta
from io import StringIO
import statistics as stats
import scipy.stats as scistats
from sklearn.linear_model import LinearRegression



#Functions next

def make_draws(dist, params, size=200):
    """
    Draw a sample from a specified distribution
    with given parameters and return these in an array.

    Parameters
    ----------

    dist: scipy.stats distribution object:
      Distribution object from scipy.stats, must have a .rvs method

    params: dict:
      Parameters needed to define the distribution dist.
    For example, if dist = scipy.stats.binom, then params could be

          {'n': 100, 'p': 0.25}

    size: int:
      The number of values to draw

    Returns
    -------
    sample: np.array, shape (size, )
      An i.i.d sample from the specified distribution.
    """
    

    return dist(**params).rvs(size)                 

def bootstrap_bill(array, num_bootstrap_samples=500):
    """Draw bootstrap resamples from the array x.

    Parameters
    ----------
    x: np.array, shape (n, )
      The data to draw the bootstrap samples from.
    
    num_bootstrap_samples: int
      The number of bootstrap samples, each is built by sampling from x with replacement.
    
    Returns
    -------
    bootstrap_samples: a list of np.ndarray with length number_bootstrap_samples.
      The bootstrap resamples from x.
    """
    return np.random.choice(array, size=num_bootstrap_samples, replace=True)

def plot_means(dist, params, size=200, repeat=5000):
    fig, ax = plt.subplots()
    
    samples = np.zeros((repeat, size))
    # a placeholder for all sampled data
    for idx in range(repeat):
        samples[idx,:] = make_draws(dist, params, size=size)
        # assign each row a sample
    sample_means = np.mean(samples, axis=1)
    # obtain the sample mean for each sample (each row)
    ax.hist(sample_means, bins=25)
    # plot the sample means on the given axis
    

    return dist(**params).rvs(size)

def fetch_csv_data(strinput):
    # initializing substrings
    sub1 = "var plotData = "
    sub2 = '";\r\n  var color1'
    
    # getting index of substrings
    idx1 = strinput.index(sub1)
    idx2 = strinput.index(sub2)
    
    res = ''
    # getting elements in between
    for idx in range(idx1 + len(sub1) + 1, idx2):
        res = res + strinput[idx]

    final_out = res.replace("|","\n")
    
    # get result
    return final_out

def time_parser(datalst):
    new_time = None

    given_string_time = datalst
    date_format = '%Y-%m-%d %H:%M:%S'

    new_time = datetime.strptime(given_string_time, date_format)
    return new_time

def show_deltas(dataframe):
    for col in dataframe.columns[:7]:
            dataframe[f'{col} Delta']= None
            for i in range(1,len(dataframe[f'{col} Delta'])):
                dataframe[f'{col} Delta'].iloc[i] = abs(dataframe[col].iloc[i] - dataframe[col].iloc[i-1])

def mean_report(dframe):
        for col in dframe.columns:
            iterables=[]
            if isinstance(dframe[col].iloc[0],int) or isinstance(dframe[col].iloc[0],float):
                iterables.append(col)
            for item in iterables:
                bootstrap= np.mean(bootstrap_bill(dframe[item]))
                st.write(f"for {item} the mean is {bootstrap} with a standard deviation of {stats.stdev(bootstrap_bill(dframe[item]))}.")

def standardized_choice(array): 
    contextualmean= np.mean(array)
    contextualstd= stats.stdev(array)
    outcome= -1000
    while outcome > contextualmean + contextualstd or outcome < contextualmean - contextualstd:
        outcome = bootstrap_bill(array,1)[0]
    return outcome

def stdev(array,dev=1):
    bootstrap= bootstrap_bill(array)
    mean=np.mean(bootstrap)
    stdev= stats.stdev(bootstrap)
    outcome= mean + stdev*dev
    return outcome
        

sat_owner_set= {"AB":	"the Arab Satellite Communications Organization"
                ,"ABS":	"Asia Broadcast Satellite"
                ,"AC":	"Asia Satellite Telecommunications Company (ASIASAT)"
                ,"ALG":	"Algeria"
                ,"ANG":	"Angola"
                ,"ARGN":	"Argentina"
                ,"ARM":	"the Republic of Armenia"
                ,"ASRA":	"Austria"
                ,"AUS":	"Australia"
                ,"AZER":	"Azerbaijan"
                ,"BEL":	"Belgium"
                ,"BELA":	"Belarus"
                ,"BERM":	"Bermuda"
                ,"BGD":	"the Peoples Republic of Bangladesh"
                ,"BHUT":	"the Kingdom of Bhutan"
                ,"BOL":	"Bolivia"
                ,"BRAZ":	"Brazil"
                ,"BUL":	"Bulgaria"
                ,"CA":	"Canada"
                ,"CHBZ":	"China/Brazil"
                ,"CHTU":	"China/Turkey"
                ,"CHLE":	"Chile"
                ,"CIS":	"the Commonwealth of Independent States (former USSR)"
                ,"COL":	"Colombia"
                ,"CRI":	"the Republic of Costa Rica"
                ,"CZCH":	"the Czech Republic (former Czechoslovakia)"
                ,"DEN":	"Denmark"
                ,"DJI":	"the Republic of Djibouti"
                ,"ECU":	"Ecuador"
                ,"EGYP":	"Egypt"
                ,"ESA":	"the European Space Agency"
                ,"ESRO":	"the European Space Research Organization"
                ,"EST":	"Estonia"
                ,"ETH":	"Ethiopia"
                ,"EUME":	"the European Organization for the Exploitation of Meteorological Satellites (EUMETSAT)"
                ,"EUTE":	"the European Telecommunications Satellite Organization (EUTELSAT)"
                ,"FGER":	"France/Germany"
                ,"FIN":	"Finland"
                ,"FR":	"France"
                ,"FRIT":	"France/Italy"
                ,"GER":	"Germany"
                ,"GHA":	"the Republic of Ghana"
                ,"GLOB":	"Globalstar"
                ,"GREC":	"Greece"
                ,"GRSA":	"Greece/Saudi Arabia"
                ,"GUAT":	"Guatemala"
                ,"HUN":	"Hungary"
                ,"IM":	"the International Mobile Satellite Organization (INMARSAT)"
                ,"IND":	"India"
                ,"INDO":	"Indonesia"
                ,"IRAN":	"Iran"
                ,"IRAQ":	"Iraq"
                ,"IRID":	"Iridium"
                ,"IRL":	"Ireland"
                ,"ISRA":	"Israel"
                ,"ISRO":	"the Indian Space Research Organisation"
                ,"ISS":	"the Intergovernmental Agreement of International Space Station"
                ,"IT":	"Italy"
                ,"ITSO":	"the International Telecommunications Satellite Organization (INTELSAT)"
                ,"JPN":	"Japan"
                ,"KAZ":	"Kazakhstan"
                ,"KEN":	"the Republic of Kenya"
                ,"LAOS":	"Laos"
                ,"LKA":	"the Democratic Socialist Republic of Sri Lanka"
                ,"LTU":	"Lithuania"
                ,"LUXE":	"Luxembourg"
                ,"MA":	"Morroco"
                ,"MALA":	"Malaysia"
                ,"MCO":	"the Principality of Monaco"
                ,"MDA":	"the Republic of Moldova"
                ,"MEX":	"Mexico"
                ,"MMR":	"the Republic of the Union of Myanmar"
                ,"MNG":	"Mongolia"
                ,"MUS":	"Mauritius"
                ,"NATO":	"the North Atlantic Treaty Organization (NATO)"
                ,"NETH":	"Netherlands"
                ,"NICO":	"New ICO"
                ,"NIG":	"Nigeria"
                ,"NKOR":	"the Democratic People's Republic of Korea (North Korea)"
                ,"NOR":	"Norway"
                ,"NPL":	"the Federal Democratic Republic of Nepal"
                ,"NZ":	"New Zealand"
                ,"O3B":	"O3b Networks"
                ,"ORB":	"ORBCOMM"
                ,"PAKI":	"Pakistan"
                ,"PERU":	"Peru"
                ,"POL":	"Poland"
                ,"POR":	"Portugal"
                ,"PRC":	"the People's Republic of China"
                ,"PRY":	"the Republic of Paraguay"
                ,"PRES":	"the People's Republic of China/the European Space Agency"
                ,"QAT":	"the State of Qatar"
                ,"RASC":	"RascomStar-QAF"
                ,"ROC":	"Taiwan (Republic of China)"
                ,"ROM":	"Romania"
                ,"RP":	"Philippines (Republic of the Philippines)"
                ,"RWA":	"Republic of Rwanda"
                ,"SAFR":	"South Africa"
                ,"SAUD":	"Saudi Arabia"
                ,"SDN":	"the Republic of Sudan"
                ,"SEAL":	"Sea Launch"
                ,"SES":	"SES"
                ,"SGJP":	"Singapore/Japan"
                ,"SING":	"Singapore"
                ,"SKOR":	"the Republic of Korea"
                ,"SPN":	"Spain"
                ,"STCT":	"Singapore/Taiwan"
                ,"SVN":	"Slovenia"
                ,"SWED":	"Sweden"
                ,"SWTZ":	"Switzerland"
                ,"TBD":	"To Be Determined"
                ,"THAI":	"Thailand"
                ,"TMMC":	"Turkmenistan/Monaco"
                ,"TUN":	"the Republic of Tunisia"
                ,"TURK":	"Turkey"
                ,"UAE":	"the United Arab Emirates"
                ,"UK":	"the United Kingdom"
                ,"UKR":	"Ukraine"
                ,"UNK":	"Unknown"
                ,"URY":	"Uruguay"
                ,"US":	"the United States of America"
                ,"USBZ":	"the United States of America/Brazil"
                ,"VAT":	"the Vatican City State"
                ,"VENZ":	"Venezuela"
                ,"VTNM":	"Vietnam"
                ,"ZWE":	"the Republic of Zimbabwe"}

st.title("Satellite Maneuver Predictor")

#Establish 'now', then check no against the timestamp in the last data file to see if two hours have elapsed, constituting a long enough window since the last run (2 hrs) to re-pull the data.


given_string_time = pd.read_csv("data/sat_pos_history.csv")['Timestamp'].iloc[0][:19]
date_format = '%Y-%m-%d %H:%M:%S'
new_time = datetime.strptime(given_string_time, date_format)
timestamp_difference = datetime.now() - new_time

if timestamp_difference > timedelta(hours=3):
    satcat = pd.read_csv("https://celestrak.org/pub/satcat.csv")
    satcat.to_csv('data/satcat.csv',header=True,sep=',')
else: satcat = pd.read_csv("data/satcat.csv")

# move satcat and zip response both into a data folder, and impute current time over them with a code that checlos this time against our time
satcat = satcat[satcat['OPS_STATUS_CODE'] == "+"]
satcat = satcat[satcat['OBJECT_TYPE'] != "DEB"]
satcat = satcat[satcat['OBJECT_TYPE'] != "R/B"]
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NEA"]
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NCE"]
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NIE"]
satcat = satcat[satcat['ORBIT_CENTER'] == "EA"]


sat_selection_form = st.form("SatCat selection",)
selection_criteria = sat_selection_form.radio('Select Search Criteria: ', options=['Search by Satellite Name','Search by NORAD SATCAT Number'])
name_search = sat_selection_form.selectbox('Satellite Name: ',satcat['OBJECT_NAME'])
number_search = sat_selection_form.selectbox('NORAD SATCAT Number: ',satcat['NORAD_CAT_ID'])

submission = sat_selection_form.form_submit_button("Find Maneuvers")

if submission:
    if selection_criteria == 'Search by Satellite Name':
        sat_num = satcat['NORAD_CAT_ID'].loc[satcat['OBJECT_NAME'] == name_search].iloc[0]
        sat_name = satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]
    else: sat_num = number_search

    st.write(f"Showing results for {sat_name}, NORAD Satcat Number {sat_num}, owned by {sat_owner_set[satcat['OWNER'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]]}, and launched {satcat['LAUNCH_DATE'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}. For a complete rundown on how to analyze this orbit, refer to the tabs sequentially from left to right. Otherwise, select the tab to best suit your needs, with Pocket Orbital Analyst being the most surface-level, simple report on {sat_name}.")
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["Basic Orbital Mechanics","Maneuver Detection","Pocket Orbital Analyst",f"{satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}'s Position",f"{satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}'s Maneuver Predictions"])
    
    t1c1, t1c2 = tab1.columns(2)


   
    t1c1.image("images/sma_img.jpg")
    t1c2.subheader("Semimajor Axis (SMA)")
    t1c2.write("Semimajor Axis (measured in kms) is effectively the 'radius' of an ellipse or oval, measured along the most oblong side (hence the 'Major' as opposed to 'Minor'!). As you can see on the left, the smaller of the two semimajor axes is overall closer to the Earth than the one shown on the right. This not only allows it to travel faster in its orbit as it's closer to the mass its orbiting (known as the 'Primary'), but it also has much less distance to cover, like a runner on the inside lanes of a track as opposed to the runner on the outside! This results in a directly linear relationship between SMA and Period, that is, the amount of time it takes for a satellite to complete one full orbit and return to its original position.")


    t1c2.image("images/eccentricity_img.jpg")
    t1c1.subheader("Eccentricity")
    t1c1.write("Eccentricity (between 0 and 1, with 0 being most circular,) is effectively how 'oblong' vs circular the orbit is. That is to say, no orbit is perfectly circular, which is why we describe orbit shape as an ellipse instead of a circle. Apoapsis (or Apogee if the satellite is orbiting the Earth,) is when the satellite is farthest away from the primary in its orbit whereas Periapsis ('Perigee' in the Earths case!) is when a satellite is closest to the primary. Eccentricity describes the difference between Periapsis and Apoapsis such that a satellite with lower Eccentricity has very little difference between Apoapsis and Periapsis, whereas a vehicle with high Eccentricity sees a big difference between the two. Satellites' velocity is determined by gravity, so as a satellite approaches perigee it speeds up since Earth pulls it even more, then slows down as it approaches Apogee.")

    t1c1.image("images/inc_img.jpg")
    t1c2.subheader("Inclination")
    t1c2.write("Inclination (measured from 0 to 180 in degrees) is the angle formed by the equator and the pathe of the orbit measured in the direction the satellite is travelling at the Ascending Node (the point at which a satellite crosses the equator going North!). Up until 90 degrees, inclination also happens to be the highest Latitude over the Earth a satellite reaches in its orbit. Note the satellite on the right has a higher Inclination than the one on the left by ~15 degrees. Bear in mind that the reason inclination only goes from 0 to 180 degrees is because of how we measure it; At 179 degrees, the point from which we're measuring is still the Ascending Node since the satellite is still travelling North when it crosses the equator at that point. However, at a hypothetical '181 degree' angle, the point we were previously measuring from is no longer the Ascending Node, since we are now travelling South when crossing the equator; Thus it becomes the Descending Node, with the Ascending Node now being on the other side of the planet and the Inclination being 1 degree.")

    t1c2.image("images/raan_img.jpg")
    t1c1.subheader("Right Ascension of the Ascending Node (RAAN)")
    t1c1.write("RAAN is a tricky concept, so buckle up! First, once upon a time it was determined that you need a reference point in order to describe position. On the Earth, we use the concept of 'North' as a reference point. In space however, there isn't really a 'North', nor a compass to point to it. To that end, the Vernal Equinox, a constellation of distant stars, was chosen as our 'North' for describing RAAN. RAAN (measured from 0 to 360 degrees in the direction of motion,) is the angle between the Vernal Equinox and the Ascending Node. Note the difference in RAAN in the example; it looks like the one on the right(~135 degrees) is about 90 degrees higher than the one on the left(~45 degrees)!")
               

    t1c1.image("images/arg_img.jpg")
    t1c2.subheader("Argument of Perigee")
    t1c2.write("Argument of Perigee (measured from 0 to 360 in degrees,) describes the orientation of a satellites Perigee. This is measured in the direction of motion from the Ascending Node to Perigee. In our example, it looks like the satellite with a lower Argument of Perigee is measuring at about 180 degrees, whereas the satellites with a larger Argument of Perigee is measuring at around 270 degrees.")

    t1c2.image("images/ta_img.jpg")
    t1c1.subheader("True Anomaly")
    t1c1.write("True Anomaly (measured in degrees from 0 to 360,) is the satellites position in its orbit at the time of measuring, measured from Perigee to the satellites current position. Bear in mind, while all the above Classical Orbital Elements describe the shape of a satellites orbit and are subject to change due to a number of perturbations from other gravitational forces as well as active maneuvers, True Anomaly, as a descriptor of where a satellite is in its orbit, goes from 0 to 360 over the course of a single Period (which changes based on SMA!), so can change wildly depending on the time you check its position, usally via a Two-Line-Element-Set (TLE). This is also an Orbital Element whose rate of change can vary based on the orbits Eccentricity as, if you recall, higher Eccentricities mean the satellite will speed up and slow down more while orbiting as opposed to more circular orbits.")
               
    
    tab2.header("Maneuver Detection in a Nutshell")
    tab2.write("'Did someone drive my car today?' may seem like an innocuous way to describe maneuver detection, but bear with the analogy... There are a couple ways to determine if someone drove my car today. If I drove it, I have first-hand experience, so there's one way! Another is if my wife's nice enough to to tell me she drove my car to the store today. Assuming, however, I don't have access to the odometer, the only other way is to open the door to my garage and check if my car is there or not. Our means of maneuver detection, in this case, is exactly that; Where every data point is NORAD opening the 'garage door' to see if the satellites are all where we expect them to be since we last checked... If they're not, we can assume someone took'em for a joyride! Detecting a difference is only one piece of the puzzle though; The other is determining the nature of the change!")

    tab2.divider()
    tab2.subheader("Intrack Maneuvers")
    tab2.image("images/int_det_img.jpg")
    tab2.write("The Classical Orbital Elements that inevitably MUST change when doing an Intrack maneuver are Eccentricity and Semimajor Axis. Note in the example above that a Negative Intrack Maneuver (that is, a maneuver against the current direction of motion,) will result in a smaller SMA and higher Eccentricity, whereas a Positive Intrack Maneuver also results in an increase in Eccentricity, but now an increase in SMA. Note that these maneuvers may also have an effect on Argument of Perigee depending on both the magnitude, direction(positive/negative), and when in the orbit the maneuver is done. In our example where it looks like we're in a relatively circular orbit to start, if we do the suggested Negative Intrack Maneuver, it looks like our Perigee will shift to be exactly 180 degrees from our current position. By constrast, if we did the shown Positive Intrack Maneuver, our CURRENT position would now become Perigee! Mind you, there is a significant gradient in terms of maneuver magnitude between these two scenarios. It's worth noting as well that Eccentricity can be changed on its own by doing a Radial Maneuver, that is a maneuver that is directly towards or away from the Earth. These can be used to help shape (usually circularize) an orbit, but are fairly expensive on their own and are usually done in conjunction with an Intrack Maneuver to offset the cost for a similar result.")



    launch_date = datetime.strptime(satcat['LAUNCH_DATE'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0],'%Y-%m-%d')
    checkout_duration = timedelta(weeks=24)
    nominal_ops_date=launch_date+checkout_duration

    if timestamp_difference > timedelta(hours=3) or pd.read_csv("data/sat_pos_history.csv")['SATCAT Number'].iloc[0] != sat_num:
        zip_response = get(f"https://celestrak.org/NORAD/elements/graph-orbit-data.php?CATNR={sat_num}")
        #zip_response = get(f"https://celestrak.org/NORAD/elements/graph-orbit-data.php?CATNR=49260")
        data4csv = fetch_csv_data(zip_response.text)
        in_data = StringIO(data4csv)
        sat_mnvr_df = pd.read_csv(in_data,header=0,sep=',')


    
        for i in range(len(sat_mnvr_df['Date'])):
            sat_mnvr_df['Date'].iloc[i] = sat_mnvr_df['Date'].iloc[i].replace("T", " ")
        for i in range(len(sat_mnvr_df['Date'])):
            sat_mnvr_df['Date'].iloc[i] = sat_mnvr_df['Date'][i][0:19]
        for i in range(len(sat_mnvr_df['Date'])):
            sat_mnvr_df['Date'].iloc[i] = time_parser(sat_mnvr_df['Date'].iloc[i])
        sat_mnvr_df = sat_mnvr_df.rename(columns={"Date":"Date/Time (UTC)"})
    
        for i in range(len(sat_mnvr_df['SMA'])):
            sat_mnvr_df['SMA'].iloc[i] += 6378

        sat_mnvr_df['Period'] = None
        for i in range(len(sat_mnvr_df['SMA'])):
            sat_mnvr_df['Period'].iloc[i] = 2*math.pi*math.sqrt((sat_mnvr_df['SMA'].iloc[i]**3)/398600.44189)

        sat_mnvr_df=sat_mnvr_df.dropna()

        #for col in sat_mnvr_df.columns:
        #    sat_mnvr_df[f'{col} Delta']= None
        #    for i in range(1,len(sat_mnvr_df[f'{col} Delta'])):
        #        sat_mnvr_df[f'{col} Delta'].iloc[i] = abs(sat_mnvr_df[col].iloc[i] - sat_mnvr_df[col].iloc[i-1])
#
        #sat_mnvr_df = sat_mnvr_df.dropna()
        #for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
        #    if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == '0:00:00':
        #        sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
        #sat_mnvr_df = sat_mnvr_df.dropna()
#


        sat_mnvr_df['Timestamp'] = datetime.now()
        sat_mnvr_df['SATCAT Number'] = sat_num
        sat_mnvr_df.to_csv('data/sat_pos_history.csv',header=True,sep=',')
        sat_mnvr_df = sat_mnvr_df.drop(columns=['Timestamp','SATCAT Number'])



    else: sat_mnvr_df = pd.read_csv("data/sat_pos_history.csv").drop(columns=["Unnamed: 0", "Timestamp","SATCAT Number"])

    if isinstance(sat_mnvr_df['Date/Time (UTC)'].iloc[0], str):
        for i in range(len(sat_mnvr_df['Date/Time (UTC)'])):
            sat_mnvr_df['Date/Time (UTC)'].iloc[i] = time_parser(sat_mnvr_df['Date/Time (UTC)'].iloc[i])
    
    for col in sat_mnvr_df.columns:
            sat_mnvr_df[f'{col} Delta']= None
            for i in range(1,len(sat_mnvr_df[f'{col} Delta'])):
                sat_mnvr_df[f'{col} Delta'].iloc[i] = abs(sat_mnvr_df[col].iloc[i] - sat_mnvr_df[col].iloc[i-1])

    sat_mnvr_df = sat_mnvr_df.dropna()
    for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
        if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == '0:00:00':
            sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
    sat_mnvr_df = sat_mnvr_df.dropna()

    sat_mnvr_df = sat_mnvr_df.dropna()
    for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
        if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == '0:00:00':
            sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
    sat_mnvr_df = sat_mnvr_df.dropna()


    for i in range(len(sat_mnvr_df['Date/Time (UTC)'])):
        sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = abs(sat_mnvr_df['Date/Time (UTC)'].iloc[i] - sat_mnvr_df['Date/Time (UTC)'].iloc[i-1]).total_seconds()
        if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == timedelta(seconds=0)\
        or sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == 0:
            sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
    sat_mnvr_df = sat_mnvr_df.dropna()



    sat_mnvr_df['E/W Maneuver'] = False
    for i in range(len(sat_mnvr_df['SMA'])):
        if sat_mnvr_df['SMA Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['SMA Delta'])*1\
        and sat_mnvr_df['Eccentricity Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Eccentricity Delta'])*.5\
        and sat_mnvr_df['Period Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Period Delta'])*1\
        and sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] <= stats.stdev(sat_mnvr_df['Date/Time (UTC) Delta'])*2:
            sat_mnvr_df['E/W Maneuver'].iloc[i-1] = True

    sat_mnvr_df['N/S Maneuver'] = False
    for i in range(len(sat_mnvr_df['RAAN'])):
        if sat_mnvr_df['RAAN Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['RAAN Delta'])*1\
        and sat_mnvr_df['RAAN Delta'].iloc[i] < 170\
        or sat_mnvr_df['Inclination Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Inclination Delta'])*1\
        and sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] <= stats.stdev(sat_mnvr_df['Date/Time (UTC) Delta'])*2:
            sat_mnvr_df['N/S Maneuver'].iloc[i-1] = True

    sat_mnvr_df['Maneuver Detected'] = False
    for i in range(len(sat_mnvr_df['Maneuver Detected'])):
        if sat_mnvr_df['N/S Maneuver'].iloc[i] == True\
        or sat_mnvr_df['E/W Maneuver'].iloc[i] == True:
            sat_mnvr_df['Maneuver Detected'].iloc[i] = True

    sat_mnvr_df['Maneuver Profile'] = None
    for i in range(len(sat_mnvr_df['Maneuver Detected'])):
        if sat_mnvr_df['N/S Maneuver'].iloc[i] == False and sat_mnvr_df['E/W Maneuver'].iloc[i] == False:
            sat_mnvr_df['Maneuver Profile'].iloc[i] = 'None'
        if sat_mnvr_df['N/S Maneuver'].iloc[i] == True and sat_mnvr_df['E/W Maneuver'].iloc[i] == False:
            sat_mnvr_df['Maneuver Profile'].iloc[i] = 'Crosstrack Maneuver'
        if sat_mnvr_df['N/S Maneuver'].iloc[i] == False and sat_mnvr_df['E/W Maneuver'].iloc[i] == True:
            sat_mnvr_df['Maneuver Profile'].iloc[i] = 'Intrack Maneuver'
        if sat_mnvr_df['N/S Maneuver'].iloc[i] == True and sat_mnvr_df['E/W Maneuver'].iloc[i] == True:
            sat_mnvr_df['Maneuver Profile'].iloc[i] = 'Compound Maneuver'

    sat_mnvr_df['Checkout Period'] = False
    for i in range(len(sat_mnvr_df['Maneuver Detected'])):
        if sat_mnvr_df['Maneuver Detected'].iloc[i] == True\
            and sat_mnvr_df['Date/Time (UTC)'].iloc[i] < nominal_ops_date:
            sat_mnvr_df['Checkout Period'].iloc[i] = True

    sat_mnvr_df=sat_mnvr_df.dropna()
    
    nonabs_df = sat_mnvr_df.copy()
    for col in nonabs_df.columns[:7]:
            nonabs_df[f'{col} Delta']= 0
            for i in range(1,len(nonabs_df[f'{col} Delta'])):
                nonabs_df[f'{col} Delta'].iloc[i] = nonabs_df[col].iloc[i] - nonabs_df[col].iloc[i-1]
    nonabs_df=nonabs_df.dropna()

     
    tab4.header(f"{sat_name}'s NORAD Data")
    tab4.divider()
    tab4.write("The following consists of all observations available in the NORAD database.")
    tab4.write(sat_mnvr_df)

    tab3.header("Satellite B.L.U.F. Analysis:")
    tab3.divider()
    tab3.subheader("Observations")
    tab3.write(f"For {satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}, there have been a total of {len(sat_mnvr_df['Date/Time (UTC)'])} observations. The earliest observation in the current available database occured {sat_mnvr_df['Date/Time (UTC)'].iloc[0]} with the most recent occurring at {sat_mnvr_df['Date/Time (UTC)'].iloc[-1]}. Of these observations, {sum(sat_mnvr_df['Maneuver Detected'])} indicate potential maneuvers given changes to Classical Orbital Elements. Of the observed potential maneuvers in the dataset, {sum(sat_mnvr_df['Checkout Period'])} occurred during the first 6 months of the satellites time on orbit which is generally when a number of adjustments are made to initiate intended trajectory which could otherwise skew data trying to capture nominal on-orbit operations. Observations for this satellite by NORAD tend to be collected at an average interval of {round(np.mean(sat_mnvr_df['Date/Time (UTC) Delta'][1:])/3600, 2)} hours.")
    #add a section to account for frontloading maneuvers during orbit insertion.
    regime_descr = {"Low Earth Orbit (LEO)":"These satellites move at a high velocity relative to the earth, circling the planet about 14-16 times a day. They require the lowest power budget to contact, but their field of view is small relative to satellites in higher orbital regimes, requiring the greatest number of satellites to achieve a globally effective constellation."
                    ,"Medium Earth Orbit (MEO)":"These satellites are situated safely between the Earths two Van Allen Radiation belts whose radiation is otherwise a detriment to most satellites lifespans. These satellites circle the planet every 12 hours which makes their frequency less potent than satellites in Low Earth Orbit, however, these satellites are far enough from the planet to be afforded a much larger Field of View. As a result, most Navigation satellites are primarily in this orbital regime to include GPS and GLONASS."
                    ,"GeoSynchronous Earth Orbit (GEO)":"At lower inclination, these satellites are stationary relative to the ground below and will, in fact, appear as the only 'stars' in the sky that do not move over the course of a full night. Their positional consistency makes them ideal for satellite communication as antennae on the ground rarely need to be reoriented to follow them. Additionally, only three satellites are needed for a constellation that has complete coverage of the Earth barring some locations at very high or low latitudes."
                    ,"SuperSynchronous Graveyard Orbit":"The GEOBelt at a SemiMajor Axis of 42164 kms represents a highly valued and sought-after orbit, especially bearring in mind the Longitude over which these seemingly stationary satellites are placed. As a result, it becomes necessary to clear the belt for future use as a satellite nears the end of its lifespan. The SuperSynchronous Graveyard is a space above the GEOBelt that is not stationary relative to the Earth, losing the advantage of the later, rendering it an appropriate space to dispose of satellites at the end of their functional life."
                    ,"CisLunar Space or Beyond":"Satellites at this altitude have generally surrendered any Earth-focused advantage in terms of either their power budget for contacts or time-synchronous activities in favor of a usually scientific objective to advance our understanding of the Moon or of other celestial bodies."
                    ,"Highly Elliptical Orbit (HEO)":"The oblong shape of this orbit allows for increased hang-time as the satellite approaches Apogee, it's furthest point from Earth. This is particularly valuable for for constellations which require increased coverage at higher latitudes which may otherwise not be servicable by satellites in a GeoSynchronous Orbit attributing to it often being coupled with a high inclination as well, bearing in mind that the inclination also represents the maximum latitude reached over the Earth. Often called Molniya Orbits, these are used primarily by Russia, but have also been utilized by Japan to increase hang-time over the mainland as well as Sirius XM radio to corner the trucking market amid the Canadian Rockies."
                    ,"Sun-Synchronous Orbit (SSO)":"This orbital regime is a subsection of Low Earth Orbit, placed at a high Inclination (between 95 and 105 usually, with a sweet-spot around 98) to take advantage of J2 Perturbations such that over the course of 24 hours this satellite will circle the entire planet by travlling from pole to pole 14-16 times as the Earth rotates beneath it, finally returning to the same geographic location overhead at the same time the following day. This is ideal for tracking day-to-day changes on the Earth and this orbit is often used for tracking weather as a result. These orbits need to be meticulously maintained to be effective so these vehicles may see a high volume of maneuvers relative to other satellites."}
    if np.mean(sat_mnvr_df['SMA']) < 12000:
        regime = "Low Earth Orbit (LEO)"
    elif np.mean(sat_mnvr_df['SMA']) < 38000:
        regime = "Medium Earth Orbit (MEO)"
    elif np.mean(sat_mnvr_df['SMA']) < 45000:
        regime = "GeoSynchronous Earth Orbit (GEO)"
    elif np.mean(sat_mnvr_df['SMA']) < 50000:
        regime = "SuperSynchronous Graveyard Orbit"
    elif np.mean(sat_mnvr_df['SMA']) > 50000:
        regime = "CisLunar Space or Beyond"
    if np.mean(sat_mnvr_df['Eccentricity']) >= 0.05:
        regime = "Highly Elliptical Orbit (HEO)"
    if np.mean(sat_mnvr_df['SMA']) < 10000\
    and np.mean(sat_mnvr_df['Inclination']) < 105\
    and np.mean(sat_mnvr_df['Inclination']) > 94:
        regime = "Sun-Synchronous Orbit (SSO)"
    tab3.divider()
    tab3.subheader("Regime")
    tab3.write(f"With a SemiMajor Axis of approximately {round(np.mean(sat_mnvr_df['SMA']),2)} kilometers, {satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]} is in a {regime}. {regime_descr[regime]}")

    tab2.write(f"Time to flex your newfound skills as an Orbital Analyst! Check out the SMA and Eccentricity of {sat_name}, the satellite you just ran. To orient you to the graphs, white dots indicate position while the red triangles and blue stars indicate detection of Intrack or Compound (both Intrack AND Crosstrack) maneuvers respectively... You probably notice some white 'tails' trailing behind the red triangles and blue stars (if there ARE any!). This indicates that an Intrack maneuver happened at that time and then, as of the next observation, the SMA/Eccentricity was different! Now, looking just at the SMA graph and knowing what you now know about how Positive Intrack Maneuvers increase SMA while Negative Intrack Maneuvers decrease SMA, just by looking at where the while tail shifts after a Maneuver, you can tell if the Maneuver was Positive or Negative! on the SMA graph, if the next 'tail' is above the detected maneuver, it was a Positive Intrack Maneuver, whereas the opposite is true of a Negative Intrack Maneuver! You probably also noticed some yellow circles on the graph too; These indicate detection of a Crosstrack Maneuver and are what we're going to focus on next...")

    for col in sat_mnvr_df.columns[4:6]:
        colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
        size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
        mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
        opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}
        fig, ax = plt.subplots()
        for innate in np.unique(sat_mnvr_df['Maneuver Profile']):
            datax=sat_mnvr_df['Date/Time (UTC)']
            datay=sat_mnvr_df[col]
            ax.scatter(datax.loc[sat_mnvr_df['Maneuver Profile']==innate], 
                   datay.loc[sat_mnvr_df['Maneuver Profile']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   marker=mark[innate],
                   label = innate)
        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20) 
        if col == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab2.pyplot(fig)
    
    tab2.subheader("Crosstrack Maneuvers")
    tab2.image("images/ct_det_img.jpg")
    tab2.write("If you're not confused yet, this oughta do the trick... Crosstrack Maneuvers, that is maneuvers perpendicular to the direction of motion (sometimes called North/South Maneuver... which can be helpful, but also really misleading for satellites with high inclination since their direction of motion very well may be North or South!) and their effect on an orbit have as much to do with the time and position in the orbit that they occur as the magnitude and direction. Angular momentum is the heavy-hitter here in terms of limitting what is and is not possible for a satellite with the satellites orbit effectively being like a gyro, such that it's highly resistant to change. As such, the Ascending and Descending Nodes can be thought os like an 'axel' on which our Inclination can rotate. With this in mind, a Positive Crosstrack Maneuver at the Ascending Node results in an increased Inclination as in our example above, whereas a Negative Crosstrack Burn at this same position would result in a lower Inclination.")
    tab2.write("Now, if the 'axel' we mentioned is where the 'gyro' is the LEAST resistant to change, the halfway point, 90 degrees offset from that 'axel' would be when the gyro is MOST resistant to change. At this point in a satellites orbit, when it is halfway between the two Nodes, a Crosstrack burn will actually have no affect on the Inclination whatsoever; Instead, the only orbital element to change will be RAAN, in effect rotating the orbit around the North and South poles. To help with this relationship, I find it's best to think in terms of double-negatives... That is, if the satellite is South(-) of the equator and then burns in the Negative(-) crosstrack direction, it will Increase(+) its RAAN, rotating the orbit counterclockwise about the North pole as shown in the example above. A Positive(+) Crosstrack burn from this South(-) position would actually DECREASE(-) the RAAN, rotating the RAAN clockwise about the Northpole. Just the same, from the opposite side of the orbit, at the satellites Northern-most(+) point, a Positive(+) Crosstrack Maneuver would result in an INCREASED(+) RAAN, while a Negative Maneuver(-) would result in Decreased RAAN(-)...")
    tab2.write("Like I said, just like multiplying negatives in Algebra:") 
    tab2.write("-1 x -1 = +1,")
    tab2.write("+1 x +1 = +1,")
    tab2.write("+1 x -1 = -1,")
    tab2.write("and -1 x +1 = -1!")  
    tab2.write("Better yet...")
    tab2.write("(-Position) x (-Mnvr Direction) = (+RAAN change),")
    tab2.write("(+Position) x (+Mnvr Direction) = (+RAAN Change),")
    tab2.write("(+Position) x (-Mnvr Direction) = (-RAAN Change),")
    tab2.write("and (-Position) x (+Mnvr Direction) = (-RAAN Change)!")               
    tab2.write("Luckily for budding Orbital Analysts like yourself, maneuvers intended to change soleley RAAN are exceedingly rare... What's not as rare is RAAN-flipping, which is when RAAN all-of-a-sudden changes 180 degrees. This is almost never because of some profound maneuver, but is instead because Inclination changed, flipping which Node is the Ascending Node and which is the DEscending Node, in turn shifting RAAN by 180 degrees as well due to how RAAN is measured.")

    for col in sat_mnvr_df.columns[1:3]:
        colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
        size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
        mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
        opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}
        fig, ax = plt.subplots()
        for innate in np.unique(sat_mnvr_df['Maneuver Profile']):
            datax=sat_mnvr_df['Date/Time (UTC)']
            datay=sat_mnvr_df[col]
            ax.scatter(datax.loc[sat_mnvr_df['Maneuver Profile']==innate], 
                   datay.loc[sat_mnvr_df['Maneuver Profile']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   marker=mark[innate],
                   label = innate)
        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20) 
        if col == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab2.pyplot(fig)
    
    tab2.write(f"In the above graphs analyzing {sat_name} you may see RAAN skip by upwards of 180 degrees due to the oscillation of Inclination mentioned before, but most often we see ran steadily increase or decrease until reaching 360 or 0 respectively and then starting over again at the other end of the graph. (In addition to Apsidal Rotation due to J2 Pertubations, which we'll touch on later,) This is simply evidence of the Ascending Node slowly shifting every day relative to the Vernal Equinox over the course of a year, not unlike the needle of a compass changing relative to the direction you're facing if you held a compass and walked in a circle around your room; The needle doing a full 360 degree rotation before ending in the same position it started in just as you have. In the case of analyzing this orbits inclination changes, the yellow circles and blue stars should preface skips in the white tails, indicating a change in Inclination. Vehicles in GeoSynchronous Orbits tend to do Crosstrack Maneuvers less, and vehicles in SunSynchronous Orbits do these maneuvers the most. The next tab, Pocket Orbital Analyst, will give you the overview of the regime this orbit is in!")

    for col in sat_mnvr_df.columns[1:7]:
        colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
        size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
        mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
        opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}

        fig, ax = plt.subplots()
        for innate in np.unique(sat_mnvr_df['Maneuver Profile']):
            datax=sat_mnvr_df['Date/Time (UTC)']
            datay=sat_mnvr_df[col]
            ax.scatter(datax.loc[sat_mnvr_df['Maneuver Profile']==innate], 
                   datay.loc[sat_mnvr_df['Maneuver Profile']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   marker=mark[innate],
                   label = innate)

        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20) 
        if col == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab4.pyplot(fig)



    for col in sat_mnvr_df.columns[7:14]:
        colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
        size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
        mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
        opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}

        fig, ax = plt.subplots()
        for innate in np.unique(sat_mnvr_df['Maneuver Profile']):
            datax=sat_mnvr_df['Date/Time (UTC)']
            datay=sat_mnvr_df[col]
            ax.scatter(datax.loc[sat_mnvr_df['Maneuver Profile']==innate], 
                   datay.loc[sat_mnvr_df['Maneuver Profile']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   marker=mark[innate],
                   label = innate)

        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20) 
        if col[:-6] == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col[:-6] == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col[:-6] == 'Date/Time (UTC)':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col[:-6] == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab4.pyplot(fig)


    j2_nodal_proc_rads_pr_sec=(-3/2)*(0.000108262668)*(
    6378/np.mean(sat_mnvr_df['SMA'])*(
        1-np.mean(sat_mnvr_df['Eccentricity'])**2)**2)*math.sqrt(
            (398600.44189/np.mean(sat_mnvr_df['SMA'])**3))*(
                math.cos(np.mean(sat_mnvr_df['Inclination'])))
    
    if timestamp_difference > timedelta(hours=3) or pd.read_csv("data/sat_pos_history.csv")['SATCAT Number'].iloc[0] != sat_num:
        tle = pd.read_csv(f"https://celestrak.org/NORAD/elements/gp.php?CATNR={sat_num}")
        tle.to_csv('data/tle.csv',header=True,sep=',')
    else: tle = pd.read_csv('data/tle.csv')

    #mean_motion = math.sqrt(398600.4418/np.mean(sat_mnvr_df['SMA']))

    #ball_coef = eval(tle.iloc[0][1][34:43])

    tab3.divider()
    tab3.subheader("Maneuver History")

    nsmnvrs = sat_mnvr_df[sat_mnvr_df['N/S Maneuver'] == True].copy()
    tab3.write(f"The following are all N/S maneuvers. In quick summation, this vehicle has done a total of {len(nsmnvrs['Date/Time (UTC)'])} N/S maneuvers, with it's earliest in the database being {nsmnvrs['Date/Time (UTC)'].iloc[0]} and the latest being {nsmnvrs['Date/Time (UTC)'].iloc[-1]}.")


    nsmnvrs.index = range(len(nsmnvrs['Date/Time (UTC)']))
    show_deltas(nsmnvrs)
    nsmnvrs['Time Between Maneuvers'] = None
    for i in range(1,len(nsmnvrs['Date/Time (UTC)'])):
        nsmnvrs['Time Between Maneuvers'].iloc[i] = abs(nsmnvrs['Date/Time (UTC)'].iloc[i] - nsmnvrs['Date/Time (UTC)'].iloc[i-1]).total_seconds()
    nsmnvrs=nsmnvrs.drop(0,axis=0)
    nsmnvrs=nsmnvrs.drop(columns='N/S Maneuver')
    
   # mean_report(nsmnvrs)

    nstime_bootstrap = np.mean(bootstrap_bill(nsmnvrs['Time Between Maneuvers']))
    ns_boot_deltaobj = timedelta(seconds=nstime_bootstrap)

    nsmnvrs['Time Residuals'] = None
    for i in range(len(nsmnvrs['Time Between Maneuvers'])):
        nsmnvrs['Time Residuals'].iloc[i] = nsmnvrs['Time Between Maneuvers'].iloc[i]-nstime_bootstrap

    tab3.write(nsmnvrs)
    if nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj > datetime.now():
        tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should occur around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}. For higher fidelity, continue to the Maneuver Prediction section.")
    elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
        tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should have occured around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}; However, {round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period, while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
    else: tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should have occured {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


    ewmnvrs = sat_mnvr_df[sat_mnvr_df['E/W Maneuver'] == True].copy()
    tab3.divider()             
    tab3.write(f"The following are all E/W maneuvers. In quick summation, this vehicle has done a total of {len(ewmnvrs['Date/Time (UTC)'])} E/W maneuvers, with it's earliest in the database being {ewmnvrs['Date/Time (UTC)'].iloc[0]} and the latest being {ewmnvrs['Date/Time (UTC)'].iloc[-1]}")

    ewmnvrs.index = range(len(ewmnvrs['Date/Time (UTC)']))
    show_deltas(ewmnvrs)
    ewmnvrs['Time Between Maneuvers'] = None
    for i in range(1,len(ewmnvrs['Date/Time (UTC)'])):
        ewmnvrs['Time Between Maneuvers'].iloc[i] = abs(ewmnvrs['Date/Time (UTC)'].iloc[i] - ewmnvrs['Date/Time (UTC)'].iloc[i-1]).total_seconds()
    ewmnvrs=ewmnvrs.drop(0,axis=0)
    ewmnvrs=ewmnvrs.drop(columns='E/W Maneuver')
    
   # mean_report(ewmnvrs)

    ewtime_bootstrap = np.mean(bootstrap_bill(ewmnvrs['Time Between Maneuvers']))
    ew_boot_deltaobj = timedelta(seconds=ewtime_bootstrap)

    ewmnvrs['Time Residuals'] = None
    for i in range(len(ewmnvrs['Time Between Maneuvers'])):
        ewmnvrs['Time Residuals'].iloc[i] = ewmnvrs['Time Between Maneuvers'].iloc[i]-ewtime_bootstrap

    
    tab3.write(ewmnvrs)
    if ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj > datetime.now():
        tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should occur around {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}. For higher fidelity, continue to thew Maneuver Prediciton section.")
    elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
        tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}.However, {round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period, while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
    else: tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}.This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")

    time_delta_sec =[]
    for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
        time_delta_sec.append(sat_mnvr_df["Date/Time (UTC) Delta"].iloc[i])

    cond_df=pd.DataFrame(columns=sat_mnvr_df.columns[:7], index=range(0,501))
    for col in cond_df.columns[0:7]:
        cond_df[col].iloc[0]=sat_mnvr_df[col].iloc[-1]

    #st.write(type(standardized_choice(sat_mnvr_df['Date/Time (UTC) Delta'])),standardized_choice(sat_mnvr_df['Date/Time (UTC) Delta']))

    for i in range(1,len(nonabs_df['Date/Time (UTC) Delta'])):
        nonabs_df['Date/Time (UTC) Delta'].iloc[i]= nonabs_df['Date/Time (UTC) Delta'].iloc[i].total_seconds()

    nonabs_df= nonabs_df.iloc[1:]
    nonabs_df.index= range(len(nonabs_df['Date/Time (UTC) Delta']))


    #don't need this anymore st.write(type(nonabs_df['Date/Time (UTC) Delta'].iloc[2]))

    

    for col in cond_df.columns[1:7]:
        std_choices=[]
        for i in range(501):
            std_choices.append(standardized_choice(nonabs_df[f'{col} Delta']))
        for i in range(1,501):
           cond_df[col].iloc[i] = cond_df[col].iloc[i-1] + bootstrap_bill(std_choices,1)
    
    for i in range(len(cond_df['RAAN'])):
        if cond_df['RAAN'].iloc[i] < 0:
            cond_df['RAAN'].iloc[i] += 360

    for i in range(1,len(cond_df['Date/Time (UTC)'])):
        cond_df['Date/Time (UTC)'].iloc[i] = cond_df['Date/Time (UTC)'].iloc[i-1] + timedelta(seconds=standardized_choice(nonabs_df['Date/Time (UTC) Delta']))

    #st.write((cond_df["Date/Time (UTC)"].iloc[0])+timedelta(seconds=10000000))

    for col in cond_df.columns[3:7]:
        cond_df[f'{col} E/W Maneuver Conditions'] = False
        for i in range(len(cond_df['Date/Time (UTC)'])):
            if cond_df[col].iloc[i] < stdev(ewmnvrs[col],2)\
            and cond_df[col].iloc[i] >  stdev(ewmnvrs[col],-2):
                cond_df[f'{col} E/W Maneuver Conditions'].iloc[i] = True
    
    cond_df['Delta Time E/W Maneuver Conditions'] = False
    for i in range(len(cond_df['Date/Time (UTC)'])):
         if cond_df['Date/Time (UTC)'].iloc[i] < ewmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(ewmnvrs['Time Between Maneuvers']),2))\
            and cond_df['Date/Time (UTC)'].iloc[i] < ewmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(ewmnvrs['Time Between Maneuvers']),-2)):
                cond_df['Delta Time E/W Maneuver Conditions'].iloc[i] = True

    for col in cond_df.columns[1:3]:
        cond_df[f'{col} N/S Maneuver Conditions'] = False
        for i in range(len(cond_df['Date/Time (UTC)'])):
            if cond_df[col].iloc[i] < stdev(nsmnvrs[col],2)\
            and cond_df[col].iloc[i] >  stdev(nsmnvrs[col],-2):
                cond_df[f'{col} N/S Maneuver Conditions'].iloc[i] = True

    cond_df['Delta Time N/S Maneuver Conditions'] = False
    for i in range(len(cond_df['Date/Time (UTC)'])):
         if cond_df['Date/Time (UTC)'].iloc[i] < nsmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(nsmnvrs['Time Between Maneuvers']),2))\
            and cond_df['Date/Time (UTC)'].iloc[i] < nsmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(nsmnvrs['Time Between Maneuvers']),-2)):
                cond_df['Delta Time N/S Maneuver Conditions'].iloc[i] = True

    cond_df['E/W Maneuver Likelihood']=0
    for i in range(len(cond_df['Date/Time (UTC)'])):
        cond_df['E/W Maneuver Likelihood'].iloc[i]=sum([
            cond_df['Arg of Perigee E/W Maneuver Conditions'].iloc[i],
            cond_df['SMA E/W Maneuver Conditions'].iloc[i],
            cond_df['Eccentricity E/W Maneuver Conditions'].iloc[i],
            cond_df['Period E/W Maneuver Conditions'].iloc[i],
            cond_df['Delta Time E/W Maneuver Conditions'].iloc[i]])

    cond_df['N/S Maneuver Likelihood']=0
    for i in range(len(cond_df['Date/Time (UTC)'])):
        cond_df['N/S Maneuver Likelihood'].iloc[i]=sum([
            cond_df['RAAN N/S Maneuver Conditions'].iloc[i],
            cond_df['Inclination N/S Maneuver Conditions'].iloc[i],
            cond_df['Delta Time N/S Maneuver Conditions'].iloc[i]])


    tab5.header("Predicted Observations")
    tab5.write("The following constitute predicted observations given the satellites usual Classical Orbital Element between observations as well as the usual consistency in taking observations. These are generated entirely by this application and begin at the vehicles last known location while imposing no artificial maneuvers such that you should see the vehicles approximate trajectory if it remains uncouched.")
    tab5.write(cond_df)

    tab5.divider()
    tab5.write("The below graphs indicate E/W maneuver likelihood in terms of each Classical Orbital Element over time. When the conditions for any one COE is within 1 standard deviation from the usual maneuvring parameters seen in the past, that increases the vehicles likelihood by 1, with the overall likelihood being a summation of all parameters, starting at 0 and maxing at 5.")

    for col in cond_df.columns[1:7]:
        colors = {0:'w', 1:'c', 2:'g', 3:'y', 4:'r', 5:'p'}
        size = {0:5, 1:10, 2:20, 3:30, 4:40, 5:50}
        fig, ax = plt.subplots()
        for innate in np.unique(cond_df['E/W Maneuver Likelihood']):
            datax=cond_df['Date/Time (UTC)']
            datay=cond_df[col]
            ax.scatter(datax.loc[cond_df['E/W Maneuver Likelihood']==innate], 
                   datay.loc[cond_df['E/W Maneuver Likelihood']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   label = f'E/W Maneuver likelihood {innate}')

        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20)
        if col == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab5.pyplot(fig)


    if ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj > datetime.now():
        tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should occur around {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}. Looking purely at Maneuver frequency.")
    elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
        tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}. However, {round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period, while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
    else: tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


    tab5.divider()
    tab5.write("The below graphs indicate N/S maneuver likelihood in terms of each Classical Orbital Element over time. When the conditions for any one COE is within 1 standard deviation from the usual maneuvring parameters seen in the past, that increases the vehicles likelihood by 1, with the overall likelihood being a summation of all parameters, starting at 0 and maxing out at 3.")
    for col in cond_df.columns[1:7]:
        colors = {0:'w', 1:'y', 2:'r', 3:'p'}
        size = {0:5, 1:15, 2:30, 3:45}
        fig, ax = plt.subplots()
        for innate in np.unique(cond_df['N/S Maneuver Likelihood']):
            datax=cond_df['Date/Time (UTC)']
            datay=cond_df[col]
            ax.scatter(datax.loc[cond_df['N/S Maneuver Likelihood']==innate], 
                   datay.loc[cond_df['N/S Maneuver Likelihood']==innate],
                   s=size[innate],
                   alpha=0.5,
                   color=colors[innate],
                   label = f'N/S Maneuver likelihood {innate}')

        ax.set_title(f'{col} vs Time',size=30) 
        ax.set_xlabel('Epoch', size = 20) 
        if col == 'SMA': 
            ax.set_ylabel(f'{col} (Kilometers)', size = 20)
        elif col == 'Period':
            ax.set_ylabel(f'{col} (Seconds)', size = 20)
        elif col == 'Eccentricity':
            ax.set_ylabel(f'{col}', size = 20)
        else: ax.set_ylabel(f'{col} (Degrees)', size = 20)
        ax.grid(axis='y',color='white')
        ax.grid(which='minor',axis='x',color='white')
        ax.legend(loc=2)
        fig.tight_layout()
        fig.set_figwidth(20)
        fig.set_figheight(10)
        ax.set_facecolor('black')
        fig.set_facecolor('white')
        tab5.pyplot(fig)
    
    
    if nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj > datetime.now():
        tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should occur around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}, looking purely at Maneuver frequency.")
    elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
        tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should have occured around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}; However, {round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period, while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
    else: tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver should have occured {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


    modelns= LinearRegression()
    yns=nsmnvrs['Date/Time (UTC)']
    for col in cond_df.columns[1:7]:
        xns=nsmnvrs[col]
        modelns.fit(xns,yns)
        modelns.predict([[2]])
        modelns.coef_
        modelns.intercept_


   # for i in range(1,501):
   #     cond_df['Date/Time (UTC)'].iloc[i] = cond_df['Date/Time (UTC)'].iloc[i-1] + timedelta(seconds=bootstrap_bill(time_delta_sec,1)[0])
              


   #st.write(cond_df)

    ##pages = st.navigation([st.Page('./pages/orbit_determination.py'), st.Page('./pages/maneuver_model.py')])
    #pages.run()

    

    #n = len(sat_mnvr_df['Date/Time (UTC)'])
    #n_holdout = int(n*0.2)
    #st.write(f"{n} records total, holding out {n_holdout}")
    