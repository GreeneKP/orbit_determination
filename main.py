"""
start local demo with...
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



#Functions next...             



#This one returns bootstrap samples given an array; 
#Used a lot throughout the file.
#Also references Pirates of the Carribean....
def bootstrap_bill(array, num_bootstrap_samples=500):
    return np.random.choice(array, size=num_bootstrap_samples, replace=True)


#This one is only used once, to get the data I want out of the zipresponse.text
#The output is later sent hrough StringIO and then read in as a csv file to be manipulated.
#It's tough to describe without seeing exactly WHY it's necessary, save to say the
#substrings indicated below basically represent the left and right margins of the data I
#actually want, so I use them to define the bounds of what I want, then replace the internal
#pipe with a line to be better recognized as the delineator between columns in the csv.
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


#Given a string that represents time, in YYYY mm dd hh:mm:ss format,
#this function spits out a datetime object. This became particularly
#pertinent, as without it, when trying to graph time, it understands
#the unmanipulated 'datetime' as a string; arbitrary and categorical
#in nature. This resulted in graphing times completely out of order,
#hence necessitating a function to be called on later.
def time_parser(datalst):
    new_time = None

    given_string_time = datalst
    date_format = '%Y-%m-%d %H:%M:%S'

    new_time = datetime.strptime(given_string_time, date_format)
    return new_time


#Given the orbital parameters from our dataset, this function creates
#an additional column for each column already present, now calculating
#how much the given parameter has changed since the last observation.
#i.e. if date/time at index1 was 2024-08-08 12:00:00 and date/time at 
#index2 was 2024-08-08 13:00:00, date/time delta at index 2 would be 
#3600 seconds since that represents the time between the two observations.
def show_deltas(dataframe):
    for col in dataframe.columns[:7]:
            dataframe[f'{col} Delta']= None
            for i in range(1,len(dataframe[f'{col} Delta'])):
                dataframe[f'{col} Delta'].iloc[i] = abs(dataframe[col].iloc[i] - dataframe[col].iloc[i-1])


#Given an array, this function will return a random choice provided it
#is within one standard deviation of the mean of the dataset.
#particularly important when modeling consistent motion for a satellite
#later on; otherwise, we'd have a hgiher propensity to superimpose maneuvers
#over a satellite instead of just imposing natural motion to see when the vehicle
#will meet conditions consistent with when it regularly maneuvers.
def standardized_choice(array): 
    contextualmean= np.mean(array)
    contextualstd= stats.stdev(array)
    #arbitrarily low number so that it will always be replaced, but can be 
    #compared with < and > to initiate the while loop.
    outcome= -100000000000
    while outcome > contextualmean + contextualstd or outcome < contextualmean - contextualstd:
        outcome = bootstrap_bill(array,1)[0]
    return outcome


#This defines the bounds of a standard deviation given an array.
#also givcen the option to choose high/low bounds and how many deviations
#from the mean you want to capture.
def stdev(array,dev=1):
    bootstrap= bootstrap_bill(array)
    mean=np.mean(bootstrap)
    stdev= stats.stdev(bootstrap)
    outcome= mean + stdev*dev
    return outcome




#This is honestly much ado for nothing...
#The abbreviation on the left is how NORAD satellite catalog information 
#comes naturally. In putting that into a set and then making a human-readable
#equivalent as the value for each, I can call the value just given the column
#so the name of the satellite owner appears in one line of block text
#when the application is first run.
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





#Setup done! Let's get started!


#added this to start session timer; in retrospect I'll be caching databases and previously-run satellites 
#in the session too, but for now I'll take my lickings for having not realized that streamlit wouldn't update
#my github repository as it does locally. I know how to make this work in retrospect, but to use it to store my
#dataframe and retroactively aler all my cleaning operations after reading would be to hefty of a time-sink this
#late in the game. That's a'comin' later on this week though!
if 'Timestamp' not in st.session_state:
            st.session_state['Timestamp'] = datetime.now()   



#Title of the app
st.title("Satellite Maneuver Predictor")


#Uses on-file csv with timestamp imputed by the last unique satellite search.
#reads time into datetime object to compare with now to determine whether or not we
#can justifiably request another of the same file from the database.
#Establish 'now', then check now against the timestamp in the last data file to see if 
#at least 3 hours have elapsed, constituting a long enough window since the last run 
#(3 hrs) to re-pull the data, per Dr. Kelso to avoid this being seen as a DDOS attack.
#If the condition to pull a new file has been met, it not only reads the file, but also
#immediately files it away to reset the 3-hour clock so we play nicely with our NORAD friends.
#In retrospect, I'm finding the reason this works LOCALLY and not on streamlit is that Streamlit
#cannot update Github. will be utilizing streamlit session state going froward as seen in the below 
#timestamp sample.

if datetime.now()-st.session_state['Timestamp']>timedelta(minutes=30):
        st.session_state['Timestamp'] = datetime.now()

#if local, use these, otherwise...
#satcat_time = pd.read_csv("data/satcat.csv")['Timestamp'].iloc[0][:19]
#date_format = '%Y-%m-%d %H:%M:%S'
#new_time = datetime.strptime(satcat_time, date_format)

new_time = st.session_state['Timestamp']

timestamp_difference = datetime.now() - new_time
if timestamp_difference > timedelta(hours=3):
    satcat = pd.read_csv("https://celestrak.org/pub/satcat.csv")
    satcat['Timestamp'] = datetime.now()
    satcat.to_csv('data/satcat.csv',header=True,sep=',')
else: satcat = pd.read_csv("data/satcat.csv")

#little message to the user as to when then can see data from an updated Satellite Catalog
#admittedly, the 3 hour window is pretty extreme for this one; the Satellite Catalog is only updated
#every 24 hours and rarely sees changes at that. This still increases the chances of catching something
#as soon as it happens though!
if timestamp_difference > timedelta(hours= 3):
    st.write(f'Last Satellite Catalog ran at :red[{new_time}]. Next update available :green[Now]! This may affect the satellites you can choose from below.')
else: st.write(f'Last Satellite Catalog ran at :red[{new_time} UTC]. Next update available at :orange[{new_time + timedelta(hours=3)}]. This may affect the satellites you can choose from below.')






#The following code parses a ton of satellites out of the database so the user can only 
#select satellites with enough pertinent information to actually let the tool function properly...
#It's worth noting that the satellite catalog is a complete catalogue of everything that has EVER
#been in space to include every individual piece of debris, deorbited sats, sputnik, etc. so it must
#be parsed thoroughly so that the only available satellites to select are those that could reasonably
#benefit from a prediction... No need to predict Sputniks Orbit or maneuvers afterall!

#Sats must be considered functional and on orbit
satcat = satcat[satcat['OPS_STATUS_CODE'] == "+"]

#Sats must not be labelled as debris or rocket bodies (neither of which maneuver!)
satcat = satcat[satcat['OBJECT_TYPE'] != "DEB"]
satcat = satcat[satcat['OBJECT_TYPE'] != "R/B"]

#Sats must have complete data, without random gaps across different observations
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NEA"]
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NCE"]
satcat = satcat[satcat['DATA_STATUS_CODE'] != "NIE"]

#Sats must be orbitting the Earth
satcat = satcat[satcat['ORBIT_CENTER'] == "EA"]







#Here we create the form the user completes to select a satellite of the available options.
#I wanted to ensure no user imput errors were possible so, as such both available search criteria,
#Name and satcat number, are in drop-down menus. 
sat_selection_form = st.form("SatCat selection",)
selection_criteria = sat_selection_form.radio('Select Search Criteria: ', options=['Search by Satellite Name','Search by NORAD SATCAT Number'])
name_search = sat_selection_form.selectbox('Satellite Name: ',satcat['OBJECT_NAME'])
number_search = sat_selection_form.selectbox('NORAD SATCAT Number: ',satcat['NORAD_CAT_ID'])

#I've come to find that once interacted with, 'submission' is set to 'True',
#hence, the rest of the file will be in an if statement... 
submission = sat_selection_form.form_submit_button("Find Maneuvers")

if submission:

    #In the exceedingly rare case that a satellite makes it through the above parsing wickets,
    #but still doesn't have enough data for the tool to work appropriately, I've wrapped the
    #I've wrapped the whole tool in a try-except message that otherwise spits out an error message
    #and recommendation for the user to try other satellites or return to the chosen one in the
    #future as more data becomes available.
    try:

        #This keeps the satellite name and number variables referred to later consistent regardless
        #of the search criteria (Name or number) used by the user.
        if selection_criteria == 'Search by Satellite Name':
            sat_num = satcat['NORAD_CAT_ID'].loc[satcat['OBJECT_NAME'] == name_search].iloc[0]
            sat_name = satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]
        else: 
            sat_num = number_search
            sat_name = satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]


        #Blurb introducing the user to some identifying information about their satellite while the rest of
        #the app builds out.
        st.write(f"Showing results for {sat_name}, NORAD Satcat Number {sat_num}, owned by {sat_owner_set[satcat['OWNER'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]]}, and launched {satcat['LAUNCH_DATE'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}. For a complete rundown on how to analyze this orbit, refer to the tabs sequentially from left to right. Otherwise, select the tab to best suit your needs, with Pocket Orbital Analyst being the most surface-level, simple report on {sat_name}.")

        #wanted to organize with with tabs rather than pages to cut down on intermittent loading time, instead
        #just having it load all at once at the outset. Additionally, this spares me the headache of trying to 
        #share variables and dataframes across multiple files.
        tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["Basic Orbital Mechanics","Maneuver Detection","Pocket Orbital Analyst",f"{satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}'s Position",f"{satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}'s Maneuver Predictions","Hypothesis Testing"])

        #tab1, column1 and tab1,column2 respectively.
        t1c1, t1c2 = tab1.columns(2)


        #The following blocks of code populate the first tab, teaching the user about the Classical Orbital Elements
        #using text as well as diagrams expertly crafted in microsoft paint, pulled from the included images folder.
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


        #Here's some expository on how to detect maneuvers, coupled with a helpful visual aid from our Images folder.
        tab2.header("Maneuver Detection in a Nutshell")
        tab2.write("'Did someone drive my car today?' may seem like an innocuous way to describe maneuver detection, but bear with the analogy... There are a couple ways to determine if someone drove my car today. If I drove it, I have first-hand experience, so there's one way! Another is if my wife's nice enough to to tell me she drove my car to the store today. Assuming, however, I don't have access to the odometer, the only other way is to open the door to my garage and check if my car is there or not. Our means of maneuver detection, in this case, is exactly that; Where every data point is NORAD opening the 'garage door' to see if the satellites are all where we expect them to be since we last checked... If they're not, we can assume someone took'em for a joyride! Detecting a difference is only one piece of the puzzle though; The other is determining the nature of the change!")
        tab2.divider()
        tab2.subheader("Intrack Maneuvers")
        tab2.image("images/int_det_img.jpg")
        tab2.write("The Classical Orbital Elements that inevitably MUST change when doing an Intrack maneuver are Eccentricity and Semimajor Axis. Note in the example above that a Negative Intrack Maneuver (that is, a maneuver against the current direction of motion,) will result in a smaller SMA and higher Eccentricity, whereas a Positive Intrack Maneuver also results in an increase in Eccentricity, but now an increase in SMA. Note that these maneuvers may also have an effect on Argument of Perigee depending on both the magnitude, direction(positive/negative), and when in the orbit the maneuver is done. In our example where it looks like we're in a relatively circular orbit to start, if we do the suggested Negative Intrack Maneuver, it looks like our Perigee will shift to be exactly 180 degrees from our current position. By constrast, if we did the shown Positive Intrack Maneuver, our CURRENT position would now become Perigee! Mind you, there is a significant gradient in terms of maneuver magnitude between these two scenarios. It's worth noting as well that Eccentricity can be changed on its own by doing a Radial Maneuver, that is a maneuver that is directly towards or away from the Earth. These can be used to help shape (usually circularize) an orbit, but are fairly expensive on their own and are usually done in conjunction with an Intrack Maneuver to offset the cost for a similar result.")




        #Here we define when nominal operations for a satellite would likely begin, bearing in mind that 
        #it usually takes 6 months from launch for a satellite to establish a regular pattern of life
        #after doing all of its checkout operations, just making sure everything works at its outset.
        #This will be of use to us later on.
        launch_date = datetime.strptime(satcat['LAUNCH_DATE'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0],'%Y-%m-%d')
        checkout_duration = timedelta(weeks=24)
        nominal_ops_date=launch_date+checkout_duration



        #We're about to do another request so we use the same format as above, checkikng the timestamp of 
        #file we currently have on-hand before pulling to make sure we don't upset Dr. Kelso! Alternatively,
        #of course, if we're looking for a different satellite, the request will be different, so it won't look 
        #malicious from NORAD's perspective. After getting that data, we use an above created function in
        #conjunction with StringIO to put the data we want in a format that can be read, then turn it into
        #our dataframe.
        if timestamp_difference > timedelta(hours=3) or pd.read_csv("data/sat_pos_history.csv")['SATCAT Number'].iloc[0] != sat_num:
            zip_response = get(f"https://celestrak.org/NORAD/elements/graph-orbit-data.php?CATNR={sat_num}")
            data4csv = fetch_csv_data(zip_response.text)
            in_data = StringIO(data4csv)
            sat_mnvr_df = pd.read_csv(in_data,header=0,sep=',')


            #Housekeeping to turn the date in the dataframe into something more readable
            for i in range(len(sat_mnvr_df['Date'])):
                sat_mnvr_df['Date'].iloc[i] = sat_mnvr_df['Date'].iloc[i].replace("T", " ")
            for i in range(len(sat_mnvr_df['Date'])):
                sat_mnvr_df['Date'].iloc[i] = sat_mnvr_df['Date'][i][0:19]
            for i in range(len(sat_mnvr_df['Date'])):
                sat_mnvr_df['Date'].iloc[i] = time_parser(sat_mnvr_df['Date'].iloc[i])
            sat_mnvr_df = sat_mnvr_df.rename(columns={"Date":"Date/Time (UTC)"})

            #What's given here innately is actually altitude, not Semimajor Axis. Thankfully,
            #the quick addition of the Earths radius, 6378kms, resolves that issue!
            for i in range(len(sat_mnvr_df['SMA'])):
                sat_mnvr_df['SMA'].iloc[i] += 6378

            #quick orbital mechanics to deduce period, that is the seconds it takes for a 
            #satellite to complete one orbit, from SMA. 
            sat_mnvr_df['Period'] = None
            for i in range(len(sat_mnvr_df['SMA'])):
                sat_mnvr_df['Period'].iloc[i] = 2*math.pi*math.sqrt((sat_mnvr_df['SMA'].iloc[i]**3)/398600.44189)

            sat_mnvr_df=sat_mnvr_df.dropna()
#   

            #Impute the timestamp used to justify when new requests would be appropriate again,
            #then push this file up to data to be used later and continue the cycle as necessary!
            sat_mnvr_df['Timestamp'] = datetime.now()
            sat_mnvr_df['SATCAT Number'] = sat_num
            sat_mnvr_df.to_csv('data/sat_pos_history.csv',header=True,sep=',')
            sat_mnvr_df = sat_mnvr_df.drop(columns=['Timestamp','SATCAT Number'])


        #Pulls the on-hand file as our dataframe, cleaning out unnecessary columns at the same time. 
        else: sat_mnvr_df = pd.read_csv("data/sat_pos_history.csv").drop(columns=["Unnamed: 0", "Timestamp","SATCAT Number"])



        #ensures our Date/Time is a datetime object using a function we made earlier
        if isinstance(sat_mnvr_df['Date/Time (UTC)'].iloc[0], str):
            for i in range(len(sat_mnvr_df['Date/Time (UTC)'])):
                sat_mnvr_df['Date/Time (UTC)'].iloc[i] = time_parser(sat_mnvr_df['Date/Time (UTC)'].iloc[i])


        #Given the orbital parameters from our dataset, this function creates
        #an additional column for each column already present, now calculating
        #how much the given parameter has changed since the last observation.
        #i.e. if date/time at index1 was 2024-08-08 12:00:00 and date/time at 
        #index2 was 2024-08-08 13:00:00, date/time delta at index 2 would be 
        #3600 seconds since that represents the time between the two observations
        for col in sat_mnvr_df.columns:
                sat_mnvr_df[f'{col} Delta']= None
                for i in range(1,len(sat_mnvr_df[f'{col} Delta'])):
                    sat_mnvr_df[f'{col} Delta'].iloc[i] = abs(sat_mnvr_df[col].iloc[i] - sat_mnvr_df[col].iloc[i-1])

        sat_mnvr_df = sat_mnvr_df.dropna()

        #Gets rid of duplicate observations so our data chronologically increases.
        for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
            if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == '0:00:00':
                sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
        sat_mnvr_df = sat_mnvr_df.dropna()


        #Turns the time between observations into seconds (also not a datetime object anymore!) and also 
        #repeats above attemps to catch any duplicate observations and parse them out of the dataset. 
        for i in range(len(sat_mnvr_df['Date/Time (UTC)'])):
            sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = abs(sat_mnvr_df['Date/Time (UTC)'].iloc[i] - sat_mnvr_df['Date/Time (UTC)'].iloc[i-1]).total_seconds()
            if sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == timedelta(seconds=0)\
            or sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] == 0:
                sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] = None
        sat_mnvr_df = sat_mnvr_df.dropna()


        #Here we instantiate a column indicating the detection of an E/W maneuver.
        #This is determined using high changes in relative orbital elements, SMA and Eccentricity,
        #with that data ultimately kept in check by ensuring it's not just due to an abnormal time
        #between observations. You may notice that whereas SMA and Period just have to be above
        #one standard deviation to be considered indicative of a maneuver, Eccentricity has only 0.5.
        #Whereas radial maneuvers don't really change a satellites position, they do effect eccentricity, 
        #so it's not necessarily uncommon to couple some degree of radial maneuver with E/W maneuvers to
        #mitigate eccentricity changes.
        sat_mnvr_df['E/W Maneuver'] = False
        for i in range(len(sat_mnvr_df['SMA'])):
            if sat_mnvr_df['SMA Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['SMA Delta'])*1\
            and sat_mnvr_df['Eccentricity Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Eccentricity Delta'])*.5\
            and sat_mnvr_df['Period Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Period Delta'])*1\
            and sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] <= stats.stdev(sat_mnvr_df['Date/Time (UTC) Delta'])*2:
                sat_mnvr_df['E/W Maneuver'].iloc[i-1] = True


        #Here we instantiate a column indicating the detection of an N/S maneuver.
        #This is determined using high changes in relative orbital elements, RAAN and Inclination,
        #with that data ultimately kept in check by ensuring it's not just due to an abnormal time
        #between observations. You may notice that we also ensure any changes to RAAN above 170 are not counted.
        #this is because RAAN can sometimes flip 180 degrees as Inclination shifts, but additionally
        #RAAN usually does a full 360 degree rotation over the course of a year, so we don't want
        #to attribute it going from 360 to 1 as some massive maneuver, as these are only 1 degree
        #from each other.
        sat_mnvr_df['N/S Maneuver'] = False
        for i in range(len(sat_mnvr_df['RAAN'])):
            if sat_mnvr_df['RAAN Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['RAAN Delta'])*1\
            and sat_mnvr_df['RAAN Delta'].iloc[i] < 170\
            or sat_mnvr_df['Inclination Delta'].iloc[i] >= stats.stdev(sat_mnvr_df['Inclination Delta'])*1\
            and sat_mnvr_df['Date/Time (UTC) Delta'].iloc[i] <= stats.stdev(sat_mnvr_df['Date/Time (UTC) Delta'])*2:
                sat_mnvr_df['N/S Maneuver'].iloc[i-1] = True


        #conglomerates the presence of either maneuver into a single column.
        sat_mnvr_df['Maneuver Detected'] = False
        for i in range(len(sat_mnvr_df['Maneuver Detected'])):
            if sat_mnvr_df['N/S Maneuver'].iloc[i] == True\
            or sat_mnvr_df['E/W Maneuver'].iloc[i] == True:
                sat_mnvr_df['Maneuver Detected'].iloc[i] = True

        #creates yet another column to show maneuvers, this time singularly giving options
        #e/w, n/s, both, or none. This will be particularly valuable later when plotting as it will
        #let us call on 'uniques' in this column to change corresponding markers etc. for the given
        #observation so they appear different colors and shapes depending on the manuever profile.
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

        #Notates whether or not a maneuver occurred during the vehicles checkout period.
        sat_mnvr_df['Checkout Period'] = False
        for i in range(len(sat_mnvr_df['Maneuver Detected'])):
            if sat_mnvr_df['Maneuver Detected'].iloc[i] == True\
                and sat_mnvr_df['Date/Time (UTC)'].iloc[i] < nominal_ops_date:
                sat_mnvr_df['Checkout Period'].iloc[i] = True

        sat_mnvr_df=sat_mnvr_df.dropna()

        #Here I make a new dataframe and redo the Delta columns for later use,
        #namely so that unlike the sat_df we've been looking at, this one doesn't
        #just show the magnitude difference in any parameter as a positive value,
        #but shows it with sign as well. This becomes critical when modelling out 
        #predictive motion as otherwise we'd see every orbital element increase at
        #the right interval, but ONLY in the positive direction!
        nonabs_df = sat_mnvr_df.copy()
        for col in nonabs_df.columns[:7]:
                nonabs_df[f'{col} Delta']= 0
                for i in range(1,len(nonabs_df[f'{col} Delta'])):
                    nonabs_df[f'{col} Delta'].iloc[i] = nonabs_df[col].iloc[i] - nonabs_df[col].iloc[i-1]
        nonabs_df=nonabs_df.dropna()







        #Here we start to show off all the data we just sifted through, placing it 
        #squarely in tab4 which shows charts and visualizations of the user's
        #satellite's orbit thus far.
        tab4.header(f"{sat_name}'s NORAD Data")
        tab4.divider()
        tab4.write("The following consists of all observations available in the NORAD database.")
        tab4.write(sat_mnvr_df)







        #kneejerk to tab three because I have the brain of a squirrel!



        tab3.header("Satellite B.L.U.F. Analysis:")
        tab3.divider()
        tab3.subheader("Observations")

        #blurb highlighting the information that most people ask for upfront about a satellites orbit pattern.
        tab3.write(f"For {satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]}, there have been :orange[a total of {len(sat_mnvr_df['Date/Time (UTC)'])} observations]. The earliest observation in the current available database occured {sat_mnvr_df['Date/Time (UTC)'].iloc[0]} with the most recent occurring at {sat_mnvr_df['Date/Time (UTC)'].iloc[-1]}. Of these observations, :green[{sum(sat_mnvr_df['Maneuver Detected'])} indicate potential maneuvers given changes to Classical Orbital Elements]. Of the observed potential maneuvers in the dataset, :red[{sum(sat_mnvr_df['Checkout Period'])} occurred during the first 6 months of the satellites time on orbit] which is generally when a number of adjustments are made to initiate intended trajectory which could otherwise skew data trying to capture nominal on-orbit operations. Observations for this satellite by NORAD tend to be collected at an :blue[average interval of {round(np.mean(sat_mnvr_df['Date/Time (UTC) Delta'][1:])/3600, 2)} hours].")


        #Here's a ton of expository on each orbital regime, made a set to be called on later...
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
        if np.mean(sat_mnvr_df['SMA']) < 12000\
        and np.mean(sat_mnvr_df['Inclination']) < 105\
        and np.mean(sat_mnvr_df['Inclination']) > 94:
            regime = "Sun-Synchronous Orbit (SSO)"
        tab3.divider()
        tab3.subheader("Regime")

        #Here's where I call on that above regime expository, corresponding with the Semimajor Axes listed above.
        tab3.write(f"With a SemiMajor Axis of approximately {round(np.mean(sat_mnvr_df['SMA']),2)} kilometers, :blue[{satcat['OBJECT_NAME'].loc[satcat['NORAD_CAT_ID'] == sat_num].iloc[0]} is in a {regime}]. {regime_descr[regime]}")







        #Whiplash again! Time for Tab 2!


        #Expository on analyzing orbits, now referring to a graph thats ABOUT to populate based on the dataframe we made above, sat_mnvr_df.
        tab2.write(f"Time to flex your newfound skills as an Orbital Analyst! Check out the SMA and Eccentricity of {sat_name}, the satellite you just ran. To orient you to the graphs, white dots indicate position while the red triangles and blue stars indicate detection of Intrack or Compound (both Intrack AND Crosstrack) maneuvers respectively... You probably notice some white 'tails' trailing behind the red triangles and blue stars (if there ARE any!). This indicates that an Intrack maneuver happened at that time and then, as of the next observation, the SMA/Eccentricity was different! Now, looking just at the SMA graph and knowing what you now know about how Positive Intrack Maneuvers increase SMA while Negative Intrack Maneuvers decrease SMA, just by looking at where the while tail shifts after a Maneuver, you can tell if the Maneuver was Positive or Negative! on the SMA graph, if the next 'tail' is above the detected maneuver, it was a Positive Intrack Maneuver, whereas the opposite is true of a Negative Intrack Maneuver! You probably also noticed some yellow circles on the graph too; These indicate detection of a Crosstrack Maneuver and are what we're going to focus on next...")


        #Here some of the pieces we've been talking about start to come together...
        #Columns 4:6 correspond with orbital elements relevant to Intrack maneuvers.
        #We also instantiate some sets whose keys correspond with values from our 'Maneuver Profile'
        #column, allowing for different marker shape and color based on the type of maneuver.
        #you'll also notice I change the label to include corresponding units based on the column...
        #...can't be measuring time in kilometers or degress now, can we?
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



        #Here's a bunch more expository on orbit maneuver detection; now in terms of crosstrack motion.
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


        #Here's effectively a repeat of the above chart, this time for Inclination and RAAN.
        #Columns 1:3 correspond with orbital elements relevant to Crosstrack maneuvers.
        #We also instantiate some sets whose keys correspond with values from our 'Maneuver Profile'
        #column, allowing for different marker shape and color based on the type of maneuver.
        #you'll also notice I change the label to include corresponding units based on the column...
        #...can't be measuring time in kilometers or degress now, can we?
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

        #final expository of tab 2
        tab2.write(f"In the above graphs analyzing {sat_name} you may see RAAN skip by upwards of 180 degrees due to the oscillation of Inclination mentioned before, but most often we see ran steadily increase or decrease until reaching 360 or 0 respectively and then starting over again at the other end of the graph. (In addition to Apsidal Rotation due to J2 Pertubations, which we'll touch on later,) This is simply evidence of the Ascending Node slowly shifting every day relative to the Vernal Equinox over the course of a year, not unlike the needle of a compass changing relative to the direction you're facing if you held a compass and walked in a circle around your room; The needle doing a full 360 degree rotation before ending in the same position it started in just as you have. In the case of analyzing this orbits inclination changes, the yellow circles and blue stars should preface skips in the white tails, indicating a change in Inclination. Vehicles in GeoSynchronous Orbits tend to do Crosstrack Maneuvers less, and vehicles in SunSynchronous Orbits do these maneuvers the most. The next tab, Pocket Orbital Analyst, will give you the overview of the regime this orbit is in!")





        #kneejerk to tab4!

        #This is a repeat of the above codes used to make their corresponding charts 
        #(yes I agree, this 100% should have been a function lol), this time covering
        #all Orbital Elements, rather than dividing by N/S relevant and E/W relevant.
        tab4.divider()
        tab4.subheader(f"{sat_name}'s Orbital Elements over Time")
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

        #I split up the Orbital Elements themselves and the Change to each between observations, 
        #really to give a little expository here explaining how to digest the information effectively.
        tab4.divider()
        tab4.subheader(f"{sat_name}'s change in each Orbital Element over Time")
        tab4.write("This may seem like an innocuous destinction, but seeing how much each parameter changes between observations is arguably as important as seeing whether or not there were changes at all. The trick here is to look for parallel horizontal lines... This indicates consistency in maneuver magnitude, so not only can we see when a vehicle is maneuvering and in what direction, but in looking at the deltas, we can sometimes see a pattern that tells us the last missing piece of the puzzle!")

        #This is a repeat of the above codes used to make their corresponding charts 
        #(yes I agree, this 100% should have been a function lol), this time covering
        #all changes to Orbital Elements between observations rather than dividing by N/S relevant and E/W relevant.
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




        #Back to Tab3 'cause why not?

        tab3.divider()
        tab3.subheader("Maneuver History")
        #Here we start looking at maneuver history starting with N/S maneuvers,
        #first making a dataframe consisting only of the N/S maneuvers from the original sat_mnvr_df.
        #Then we give a brief expository on the vehicles N/S maneuvers using the dataframe
        #we just created.
        nsmnvrs = sat_mnvr_df[sat_mnvr_df['N/S Maneuver'] == True].copy()
        tab3.write(f"The following are all N/S maneuvers. In quick summation, this vehicle has done a total of :orange[{len(nsmnvrs['Date/Time (UTC)'])} N/S maneuvers], with it's earliest in the database being {nsmnvrs['Date/Time (UTC)'].iloc[0]} and the latest being {nsmnvrs['Date/Time (UTC)'].iloc[-1]}.")

        #Here I fix the index so there're no gaps, and then do the unthinkable;
        #actually USING a function I wrote. *takes a bow*
        #I then create a time between maneuvers column.
        #now, I know what you're thinking: "Isnt that the same as your Date/Time Delta' column"?
        #And you'd be right. This, however, was my first time using the .total_seconds method, after
        #which I went back and applied it to the Date/Time Delta creation way earlier since datetime
        #objects are way more finnicky than the floats they turn into when you use .total_seconds;
        #by then, however, I'd already built dependencies on Time Between Maneuvers and didn't want
        #to go back and alter something that wasn't broken this close to presentation time.
        #I drop the first row btw, because it'll never have a Time between Maneuvers as there
        #was no maneuver prior to the first one, and the single None value would complicate my data.
        #finally, I ditch the N/S maneuver column as it's redundant now in this context where our data
        #exclusively N/S maneuvers.
        nsmnvrs.index = range(len(nsmnvrs['Date/Time (UTC)']))
        show_deltas(nsmnvrs)
        nsmnvrs['Time Between Maneuvers'] = None
        for i in range(1,len(nsmnvrs['Date/Time (UTC)'])):
            nsmnvrs['Time Between Maneuvers'].iloc[i] = abs(nsmnvrs['Date/Time (UTC)'].iloc[i] - nsmnvrs['Date/Time (UTC)'].iloc[i-1]).total_seconds()
        nsmnvrs=nsmnvrs.drop(0,axis=0)
        nsmnvrs=nsmnvrs.drop(columns='N/S Maneuver')
        tab3.write(nsmnvrs)




        #Here I have a brief expository describing when a vehicle should do its next manvuever purely looking
        #at time relative to the last maneuver(nsmnvrs['Date/Time (UTC)'].iloc[-1]) and the mean of how 
        #frequently the vehicle maneuvers (ns_boot_deltaobj).
        nstime_bootstrap = np.mean(bootstrap_bill(nsmnvrs['Time Between Maneuvers']))
        ns_boot_deltaobj = timedelta(seconds=nstime_bootstrap)
        if nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj > datetime.now():
            tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :green[should occur] around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}, looking purely at maneuver frequency. For higher fidelity, continue to the Maneuver Prediction section.")
        elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
            tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :red[should have occured] around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}; However, :orange[{round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period], while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
        else: tab3.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :red[should have occured] {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


        #Here we look at maneuver history in terms of E/W maneuvers,
        #first making a dataframe consisting only of the E/W maneuvers from the original sat_mnvr_df.
        #Then we give a brief expository on the vehicles E/W maneuvers using the dataframe
        #we just created.
        ewmnvrs = sat_mnvr_df[sat_mnvr_df['E/W Maneuver'] == True].copy()
        tab3.divider()             
        tab3.write(f"The following are all E/W maneuvers. In quick summation, this vehicle has done a total of :red[{len(ewmnvrs['Date/Time (UTC)'])} E/W maneuvers], with it's earliest in the database being {ewmnvrs['Date/Time (UTC)'].iloc[0]} and the latest being {ewmnvrs['Date/Time (UTC)'].iloc[-1]}")

        #Here, just as above for the N/S counterpart, I fix the index so there're no gaps, 
        #create a time between maneuvers column, and  drop the first row btw, because it'll never 
        #have a Time between Maneuvers as there was no maneuver prior to the first one, and the single 
        #None value would complicate my data. Finally, I ditch the E/W maneuver column as it's redundant 
        #now in this context where our data is exclusively E/W maneuvers.
        ewmnvrs.index = range(len(ewmnvrs['Date/Time (UTC)']))
        show_deltas(ewmnvrs)
        ewmnvrs['Time Between Maneuvers'] = None
        for i in range(1,len(ewmnvrs['Date/Time (UTC)'])):
            ewmnvrs['Time Between Maneuvers'].iloc[i] = abs(ewmnvrs['Date/Time (UTC)'].iloc[i] - ewmnvrs['Date/Time (UTC)'].iloc[i-1]).total_seconds()
        ewmnvrs=ewmnvrs.drop(0,axis=0)
        ewmnvrs=ewmnvrs.drop(columns='E/W Maneuver')
        tab3.write(ewmnvrs)




        #Here I have a brief expository describing when a vehicle should do its next manvuever purely looking
        #at time relative to the last maneuver(ewmnvrs['Date/Time (UTC)'].iloc[-1]) and the mean of how 
        #frequently the vehicle maneuvers (ew_boot_deltaobj).
        ewtime_bootstrap = np.mean(bootstrap_bill(ewmnvrs['Time Between Maneuvers']))
        ew_boot_deltaobj = timedelta(seconds=ewtime_bootstrap)
        if ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj > datetime.now():
            tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :green[should occur] around {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}, looking purely at maneuver frequency. For higher fidelity, continue to thew Maneuver Prediciton section.")
        elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
            tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :red[should have occured] {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}, looking purely at maneuver frequency. However, :orange[{round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period], while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
        else: tab3.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :red[should have occured] {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}, looking purely at maneuver frequency. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


        #Here I create I list of all times in the Date/Time Delta column from our
        #original dataframe. I have honestly no clue why I have to do this,
        #save to say, when propogating into the future and doing our predictions later,
        #the timedelta function is willing to play nice with a list, but not the column itself...
        time_delta_sec =[]
        for i in range(len(sat_mnvr_df['Date/Time (UTC) Delta'])):
            time_delta_sec.append(sat_mnvr_df["Date/Time (UTC) Delta"].iloc[i])

        #Here I instantiate a new dataframe, I refer to as my conditional dataframe.
        #This will consist of 200 artificial observations, starting with the last actual
        #observation (sat_mnvr_df[col].iloc[-1]) and then propogating 200 times, building
        #each next 'observation' sequentially using standardized, bootstrapped samples 
        #of the corresponding Delta columns for each Orbital element. 
        cond_df=pd.DataFrame(columns=sat_mnvr_df.columns[:7], index=range(0,201))
        for col in cond_df.columns[0:7]:
            cond_df[col].iloc[0]=sat_mnvr_df[col].iloc[-1]





        #This is where I start to enact the above, iterating through each line to populate it.
        #you may also notice a couple if statements there; those keep each outcome within the bounds 
        #of its measurement, 360 and 180 degrees respectively for those orbital elements.
        for col in cond_df.columns[1:7]:
            std_choices=[]
            for i in range(201):
                std_choices.append(standardized_choice(nonabs_df[f'{col} Delta']))
            for i in range(1,201):
                cond_df[col].iloc[i] = cond_df[col].iloc[i-1] + bootstrap_bill(std_choices,1)
                if col == 'Arg of Perigee' or col == 'RAAN':
                    if cond_df[col].iloc[i] < 0:
                       cond_df[col].iloc[i] += 360
                    if cond_df[col].iloc[i] > 360:
                       cond_df[col].iloc[i] -= 360
                if col == 'Inclination':
                    if cond_df[col].iloc[i] < 0:
                       cond_df[col].iloc[i] += 180
                    if cond_df[col].iloc[i] > 180:
                       cond_df[col].iloc[i] -= 180




        #Here after having thrown a virgin into a volcano to sate the wrath of the 
        #datetime-object dieties, I'm able to populate the Date/Time observation predictor,
        #effectively simulating the same intervals by which all previous observations were taken.
        for i in range(1,len(cond_df['Date/Time (UTC)'])):
            second_offset= standardized_choice(time_delta_sec)
            cond_df['Date/Time (UTC)'].iloc[i] = cond_df['Date/Time (UTC)'].iloc[i-1] + timedelta(seconds = second_offset)

    

        #Here I create columns which indicate whether or not the conditions that constitute 
        #when an E/W maneuver occurs in terms of Orbital Elements have been reasonably met.
        #I'm at peace with being fairly liberal here, as the graphs later will overlay how
        #many conditions have been met, still granting high fidelity by virtue of the gradient.
        for col in cond_df.columns[3:7]:
            cond_df[f'{col} E/W Maneuver Conditions'] = False
            for i in range(len(cond_df['Date/Time (UTC)'])):
                if cond_df[col].iloc[i] < stdev(ewmnvrs[col],2)\
                and cond_df[col].iloc[i] >  stdev(ewmnvrs[col],-2):
                    cond_df[f'{col} E/W Maneuver Conditions'].iloc[i] = True

        #same as above, but datetime objects are always miserably more complicated
        cond_df['Delta Time E/W Maneuver Conditions'] = False
        for i in range(len(cond_df['Date/Time (UTC)'])):
             if cond_df['Date/Time (UTC)'].iloc[i] < ewmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(ewmnvrs['Time Between Maneuvers']),2))\
                and cond_df['Date/Time (UTC)'].iloc[i] < ewmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(ewmnvrs['Time Between Maneuvers']),-2)):
                    cond_df['Delta Time E/W Maneuver Conditions'].iloc[i] = True


        #Here I create columns which indicate whether or not the conditions that constitute 
        #when an N/S maneuver occurs in terms of Orbital Elements have been reasonably met.
        #I'm at peace with being fairly liberal here, as the graphs later will overlay how
        #many conditions have been met, still granting high fidelity by virtue of the gradient.
        for col in cond_df.columns[1:3]:
            cond_df[f'{col} N/S Maneuver Conditions'] = False
            for i in range(len(cond_df['Date/Time (UTC)'])):
                if cond_df[col].iloc[i] < stdev(nsmnvrs[col],2)\
                and cond_df[col].iloc[i] >  stdev(nsmnvrs[col],-2):
                    cond_df[f'{col} N/S Maneuver Conditions'].iloc[i] = True

        #same as above, but datetime objects are always miserably more complicated
        cond_df['Delta Time N/S Maneuver Conditions'] = False
        for i in range(len(cond_df['Date/Time (UTC)'])):
             if cond_df['Date/Time (UTC)'].iloc[i] < nsmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(nsmnvrs['Time Between Maneuvers']),2))\
                and cond_df['Date/Time (UTC)'].iloc[i] < nsmnvrs['Date/Time (UTC)'].iloc[-1] + timedelta(seconds=stdev(bootstrap_bill(nsmnvrs['Time Between Maneuvers']),-2)):
                    cond_df['Delta Time N/S Maneuver Conditions'].iloc[i] = True


        #Bearing in mind that 'True' = 1, this is where I conglomerate the above Maneuver Conditions met 
        #columns for N/S and E/W maneuvers respectively.
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

        #Here I introduce the tab and give a brief expository, also giving the user access
        #to the df we just populated.
        tab5.header("Predicted Observations")
        tab5.write("The following constitute predicted observations given the satellites usual Classical Orbital Element between observations as well as the usual consistency in taking observations. These are generated entirely by this application and begin at the vehicles last known location while imposing no artificial maneuvers such that you should see the vehicles approximate trajectory if it remains uncouched.")
        tab5.write(cond_df)

        #This starts with a brief expository but really is the outcome of all the work we just did,
        #outputting charts similar to all the ones we've already done, this time however, the keys
        #in our key value pairs which alter color and size correspond with unique values in the E/W
        #Maneuver likelihood column we just made above. This in turn shows how many maneuver conditions
        #have been met at any given time to sigguest when the next E/W maneuver is most likely. 
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

        #Here I have a brief expository describing when a vehicle should do its next manvuever purely looking
        #at time relative to the last maneuver(ewmnvrs['Date/Time (UTC)'].iloc[-1]) and the mean of how 
        #frequently the vehicle maneuvers (ew_boot_deltaobj).
        if ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj > datetime.now():
            tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :green[should occur around {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}], looking purely at Maneuver frequency.")
        elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
            tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :red[should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}]. However, :orange[{round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period], while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
        else: tab5.write(f"E/W maneuver average time interval is {ewtime_bootstrap} seconds, meaning its next E/W maneuver :red[should have occured {ewmnvrs['Date/Time (UTC)'].iloc[-1]+ ew_boot_deltaobj}]. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")


        #This starts with a brief expository but really is the outcome of all the work we just did,
        #outputting charts similar to all the ones we've already done, this time however, the keys
        #in our key value pairs which alter color and size correspond with unique values in the N/S
        #Maneuver likelihood column we just made above. This in turn shows how many maneuver conditions
        #have been met at any given time to sigguest when the next E/W maneuver is most likely. 
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

        #Here I have a brief expository describing when a vehicle should do its next manvuever purely looking
        #at time relative to the last maneuver(nsmnvrs['Date/Time (UTC)'].iloc[-1]) and the mean of how 
        #frequently the vehicle maneuvers (ns_boot_deltaobj).
        if nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj > datetime.now():
            tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :green[should occur around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}], looking purely at Maneuver frequency.")
        elif sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']) > 0.1:
            tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :red[should have occured around {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}], looking purely at maneuver frequency; However, :orange[{round((sum(sat_mnvr_df['Checkout Period'])/sum(sat_mnvr_df['Maneuver Detected']))*100,1)}% of the detected maneuvers occurred during the vehicles Check-out period], while it's still trying to initialize it's intended trajectory. This estimation is likely to vary greatly once nominal pattern of life maneuvers for the satellite has been established. For higher fidelity, continue to the Maneuver Prediction section, however, be warned that until more data is collected that reflects the satellites normal operations, predictions of their behavior are liable to change drastically.")
        else: tab5.write(f"N/S maneuver average time interval is {nstime_bootstrap} seconds, suggesting its next N/S maneuver :red[should have occured {nsmnvrs['Date/Time (UTC)'].iloc[-1]+ ns_boot_deltaobj}], looking purely at maneuver frequency. This departure from the previously established norms suggests that the vehicles mission may have changed or that it is nearing end-of-life and has limited fuel to maintain it's orbit.")



        #Tab6! Almost there!


        #Not so brief expository talking about the fidelity of the app; I highly recommend you read this word for word
        #as it really help understand the pitfalls and strengths of this tool in its current iteration.
        tab6.subheader("Understanding the Sample")
        tab6.write("Generally, when conducting a hypothesis test, it's important to make the distinction that you're working with either the population or a sample thereof... This is where the limitations of our tool will begin to show themselves, though not without answer.")
        tab6.write("First of all, the scope of available data tends to go back around 2 years for each satellite. If the satellite was launched before then, it becomes clear that we're only looking at a sample, as maneuvers conducted prior to available data would not be included in our set. If the vehicle was launched within that window, we have a higher likelihood of actually capturing the population in its entirety, however, this can prove fairly disadvantageous too.")
        tab6.write("Something you learn in the trade is that most satellites have a 'check-out period' when they first go up where their functionality, mission, and trajectory are all being initialized for nominal operations later. As such, maneuvers conducted during this time period have a high likelihood of looking very different that maneuvers once nominal operations, and this period varies largely from satellite to satellite, sometimes being as small as a week and other times as large as a year, all of which can serve to skew the accuracy of predictions once nominal operations begin. Mind you, while this tool won't parse out data on the basis of proximity to a satellites launch date, it WILL issue a warning in the Pocket Orbital Analyst tab, telling you what percentage of recorded maneuvers occurred during the first 6 months of a satellites time on orbit, leaving you to trust or reject the prediction on that basis.") 
        tab6.write("Another great indicator that we're dealing with a sample rather than the population is how this tool determines what constitutes a maneuver... Primarily, it uses variance in Classical Orbital Element (for Intrack and Crosstrack Maneuvers Separately,) and compares that to the usual changes from observation to observation. If the corresponding elements which would indicate a maneuver have occurred with a delta that exceeds one standard deviation of the usual delta, it assumes a maneuver has occurred.")
        tab6.write("While this is serviceable for most satellites, this can be problematic in two very specific cases: Vehicles that maneuver all the time (specifically amid more than 32% of observations,) and vehicles that cannot maneuver at all. In the case of the former, this tool will have difficulty in determining the signal from the noise. Additionally, in vehicles that cannot maneuver, this tool will likely assume that issues in position measurement or accelerative Classical Orbital Element changes due to natural perturbations are actually maneuvers. Both these issues can be resolved in the next iteration of this tool, which will calculate and superimpose J2,3, and 4 Perturbations to model motion in space more accurately such that deviations from that can be better attributed to maneuvers.") 
        tab6.write("Finally, given that the tool uses changes between observations to determine if a maneuver occurred, if there's a greater time between observations, there's also a greater gap in position between observations as a result of natural motion. With that in mind, any observation that exceeds 3 standard deviations from the normal gap will not be counted as a maneuver to get rid of any 'maneuvers' that are just a result of outliers in observation consistency... This, however, doesn't mean that a maneuver didn't occur during that time, as that's still very well possible.")
        tab6.write("With all this in mind, it becomes evident that it's best to always treat our data, no matter how robust it may look, as a sample when hypothesis testing.")

        #Here we make copies of our different maneuver-specific daraframes and parse out the columns for each that are not
        #pertinent to determining correlation with maneuver time using Pearson correlation. You may note that I'm taking out
        #Period as well. This serves a nice academic purpose, but is otherwise colinear with SMA, so I don't want to skew
        #results by including it in the tests.
        nsmnvrs_delta= nsmnvrs.copy()
        ewmnvrs_delta= ewmnvrs.copy()

        for col in nsmnvrs_delta.columns[0:7]:
                for i in range(1,len(nsmnvrs_delta[f'{col} Delta'])):
                    nsmnvrs_delta[f'{col} Delta'].iloc[i] = abs(nsmnvrs_delta[col].iloc[i] - nsmnvrs_delta[col].iloc[i-1])
        nsmnvrs_delta= nsmnvrs_delta.drop(columns=['Checkout Period',
                                                   'Maneuver Profile',
                                                   'Maneuver Detected',
                                                   'E/W Maneuver',
                                                   'Date/Time (UTC) Delta',
                                                   'Period',
                                                   'Period Delta'])

        for col in ewmnvrs_delta.columns[0:7]:
                for i in range(1,len(ewmnvrs_delta[f'{col} Delta'])):
                    ewmnvrs_delta[f'{col} Delta'].iloc[i] = abs(ewmnvrs_delta[col].iloc[i] - ewmnvrs_delta[col].iloc[i-1])
        ewmnvrs_delta= ewmnvrs_delta.drop(columns=['Checkout Period',
                                                   'Maneuver Profile',
                                                   'Maneuver Detected',
                                                   'N/S Maneuver',
                                                   'Date/Time (UTC) Delta',
                                                   'Period',
                                                   'Period Delta'])

        tab6.divider()
        tab6.header("Hypothesis Tests")
        tab6.write("Our Hypothesis is that Classical Orbital Elements can be used as a metric to predict when future maneuvers will occur... Let's see if we're right!")


        #This is where we conduct our tests for N/S maneuvers and then E/W maneuvers in turn. 
        #Bear in mind the first and last columns in this dataframe are Date/Time and Time between Maneuvers 
        #respectively, the first of which as an epoch is known to be independent, and the later of which is 
        #what we're testing against which is why they're both excised from the slice. The output is an expository
        #which highlights the results for each test as well as a line graph that shows the observed maneuvers over time
        #so the pearson results should clue you in to focus in on those charts with corrolary features.
        tab6.divider()
        tab6.header("For N/S Maneuver Pearson Correlation...")
        tab6.write(nsmnvrs_delta)
        nsdependencies=[]
        for col in nsmnvrs_delta.columns[1:-1]:        
            tab6.subheader(f'{col}')

            #graph starts here and follows most of the same format as the previous charts.
            colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
            size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
            mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
            opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}
            fig, ax = plt.subplots()
            datax=nsmnvrs_delta['Date/Time (UTC)']
            datay=nsmnvrs_delta[col]
            ax.plot(datax, 
                   datay,
                   color='y')
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
            fig.tight_layout()
            fig.set_figwidth(20)
            fig.set_figheight(10)
            ax.set_facecolor('black')
            fig.set_facecolor('white')
            tab6.pyplot(fig)

            #pearson corrolation
            data1=nsmnvrs_delta[col]
            data2=nsmnvrs_delta['Time Between Maneuvers']
            stat, p = scistats.pearsonr(data1,data2)
            tab6.write('stat=%.3f, p=%.3f' % (stat, p))
            corrolation_str = ':red[Weak]'
            if abs(stat) > 0.6:
                corrolation_str = ':green[Strong]'
            elif abs(stat) > 0.3:
                corrolation_str = ':orange[Moderate]'
            tab6.write(f'There is a {corrolation_str} statistic corrolation between {col} and Time between maneuvers.')

            if p > 0.05:
                tab6.write(f'{col} likely does :red[NOT] correspond with Time between Maneuvers for N/S Maneuvers and should :red[not] be weighed as a parameter for predicting this type of Maneuver for {sat_name} with regard to its p-value.')
            else: 
                tab6.write(f'{col} likely :green[corresponds] with Time between Maneuvers for N/S Maneuvers and :green[should] be weighed as a parameter for predicting this type of Maneuver for {sat_name} with regard to its p-value.')
            if abs(stat) > 0.3 and p < 0.05:
                nsdependencies.append(col)
            tab6.divider()

        tab6.header("For E/W Maneuver Pearson Correlation...")
        tab6.write(ewmnvrs_delta)
        ewdependencies=[]
        for col in ewmnvrs_delta.columns[1:-1]:
            tab6.subheader(f'{col}')

            #graph starts here and follows most of the same format as the previous charts.
            colors = {'None':'w', 'Compound Maneuver':'c', 'Intrack Maneuver':'r', 'Crosstrack Maneuver':'y'}
            size = {'None':5, 'Compound Maneuver':50, 'Intrack Maneuver':50, 'Crosstrack Maneuver':50}
            mark = {'None':'.', 'Compound Maneuver':'*', 'Intrack Maneuver':'>', 'Crosstrack Maneuver':'o'}
            opacity = {'None':0.2, 'Compound Maneuver':1, 'Intrack Maneuver':1, 'Crosstrack Maneuver':1}
            fig, ax = plt.subplots()
            datax=ewmnvrs_delta['Date/Time (UTC)']
            datay=ewmnvrs_delta[col]
            ax.plot(datax, 
                   datay,
                   color='r')
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
            fig.tight_layout()
            fig.set_figwidth(20)
            fig.set_figheight(10)
            ax.set_facecolor('black')
            fig.set_facecolor('white')
            tab6.pyplot(fig)

            #pearson corrolation
            data1=ewmnvrs_delta[col]
            data2=ewmnvrs_delta['Time Between Maneuvers']
            stat, p = scistats.pearsonr(data1,data2)
            tab6.write('stat=%.3f, p=%.3f' % (stat, p))
            corrolation_str = ':red[Weak]'
            if abs(stat) > 0.6:
                corrolation_str = ':green[Strong]'
            elif abs(stat) > 0.3:
                corrolation_str = ':orange[Moderate]'
            tab6.write(f'There is a {corrolation_str} statistic corrolation between {col} and Time between maneuvers.')
            if p > 0.05:
                tab6.write(f'{col} likely does :red[NOT] correspond with Time between Maneuvers for E/W Maneuvers and should :red[not] be weighed as a parameter for predicting this type of Maneuver for {sat_name} with regard to its p-value.')
            else: 
                tab6.write(f'{col} likely :green[corresponds] with Time between Maneuvers for E/W Maneuvers  and :green[should] be weighed as a parameter for predicting this type of Maneuver for {sat_name} with regard to its p-value.')
            if abs(stat) > 0.3 and p < 0.05:
                ewdependencies.append(col)
            tab6.divider()

        #Here we summarize the test results so you can see which orbital elements are the best indicators of 
        #the chosen vehicles likelihood to maneuver.  
        tab6.header("Hypothesis Test Summary")
        tab6.write(f"In summation, based on the available data for {sat_name}, of the 20 total tests run against different Classical Orbital Elements and their changes, with :orange[{len(nsdependencies)} total significant parameters] of 10 possible, the Classical Orbital Elements that can best be used to determine N/S Maneuvers are :orange[{nsdependencies}], whereas with :red[{len(ewdependencies)} total significant parameters] of 10 possible, the factors that can be best used to determine E/W Maneuvers are :red[{ewdependencies}].")
    except:
        st.header(":red[Awww, Fish Paste!]")
        st.write(f"Looks like {sat_name} doesn't have enough data for the tool to work properly or has been run too many times in too short a window to continue to populate! Please orange:[select another satellite of interest] or green:[try again in the future] as more data becomes available! If the application was just working recently for this satellite, you may need to wait 3 hours to view this satellite again!")
