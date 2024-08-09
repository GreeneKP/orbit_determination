##Orbit Predictor

#Packages

This application requires access to the following packages to run locally:
streamlit - 1.36
pandas - 2.1
numpy - 1.26
matplotlib - 3.8
scipy - 1.13
requests - 2.31


#File Overview

This application is broken into 5 tabs which populate on the basis of the user input Satellite. As such, right at the outset, the functionality of the tool is dependent on outside sources and/or pre-existing, on-hand files, being the NORAD Satellite Catalog (saved as satcat.csv in the data folder and assigned the variable name “satcat” once read-in) and the selected vehicles positional history (taken from https://celestrak.org/NORAD/elements/graph-orbit-data.php?CATNR={sat_num} where CATNR is the Satellite Catalog number inputted by the user, saved as sat_pos_history.csv in the data folder and assigned the variable name “sat_mnvr_df” once read-in). Note that regardless of the satellite chosen by the user, the file “sat_pos_history.csv” is the output name, resulting in an over-write. This is intentional as it keeps from cluttering the data folder and helps with consistent recall later. Before exporting this file to the data folder however, it is given a timestamp of the current time. In turn, the code reads that time into a datetime object to compare with now to determine whether or not we can justifiably request another of the same file from the database should the user run the same satellite twice. Assuming you’re running the same vehicle, the time between now, when the app is run, and the prior imputed timestamp exceeds 5 hours, the app will do another request for the same file. Otherwise, it will use the on-hand file. Finally, of course, if you’re looking at a completely different satellite it will happily pull agnostic of the time difference as pulling a different file effectively resets the download-limit-timer from NORAD’s perspective. In so doing, the basis of how this code works without upsetting NORAD is a time-based loop where the data for an individual satellite is saved and the tool as far as that satellite is concerned, becomes self-serving in regards to that satellite no matter how many times it’s run for the duration of the 5 hour window.

#Tab Layout

The 5 aforementioned tabs are Basic Orbital Mechanics, Maneuver Detection, Pocket Orbital Analyst, [Satellite] Position, [Satellite] Maneuver Prediction, and Hypothesis Testing. I wanted to organize with tabs rather than pages to cut down on intermittent loading time, instead just having it load all at once at the outset. Additionally, this spares me the headache of trying to share variables and dataframes across multiple files. As stated in the blurb after the users first click “Find Maneuvers”, a surface-level analysis for the layman who doesn’t really care about the “How”, but instead just the “What”, is in Pocket Orbital Analyst, the third tab; Otherwise, it is recommended that the user click the tabs from left to right to orient themselves to the process and learn as they go.

#Basic Orbital Mechanics

The first tab, as of this version (subject to change as I insert manipulatable 3D models from CZML and Poliastro!) uses entirely in-house objects with zero-dependency on computed data etc. consisting entirely of expository text and images (from the on-hand images folder) expertly crafted in Microsoft Paint. This section introduces the Classical Orbital Elements we use to describe the orientation of a satellites orbit and the satellites position therein, which are concepts that are continually built on in later tabs. One advantage of this from a user-experience perspective is that it loads almost instantaneously when the tool is run, giving the user something to engage with, perhaps not even noticing that the rest of the tabs are still loading in the background.

#Maneuver Detection

The second tab describes how the tool determines whether or not a maneuver occurred. The process is as follows:
'Did someone drive my car today?' may seem like an innocuous way to describe maneuver detection, but bear with the analogy... There are a couple ways to determine if someone drove my car today. If I drove it, I have first-hand experience, so there's one way! Another is if my wife's nice enough to to tell me she drove my car to the store today. Assuming, however, I don't have access to the odometer, the only other way is to open the door to my garage and check if my car is there or not. Our means of maneuver detection, in this case, is exactly that; Where every data point is NORAD opening the 'garage door' to see if the satellites are all where we expect them to be since we last checked... If they're not, we can assume someone took'em for a joyride! Detecting a difference is only one piece of the puzzle though; The other is determining the nature of the change!


Image ex--


The Classical Orbital Elements that inevitably MUST change when doing an Intrack maneuver are Eccentricity and Semimajor Axis. Note in the example above that a Negative Intrack Maneuver (that is, a maneuver against the current direction of motion,) will result in a smaller SMA and higher Eccentricity, whereas a Positive Intrack Maneuver also results in an increase in Eccentricity, but now an increase in SMA. Note that these maneuvers may also have an effect on Argument of Perigee depending on both the magnitude, direction(positive/negative), and when in the orbit the maneuver is done. In our example where it looks like we're in a relatively circular orbit to start, if we do the suggested Negative Intrack Maneuver, it looks like our Perigee will shift to be exactly 180 degrees from our current position. By constrast, if we did the shown Positive Intrack Maneuver, our CURRENT position would now become Perigee! Mind you, there is a significant gradient in terms of maneuver magnitude between these two scenarios. It's worth noting as well that Eccentricity can be changed on its own by doing a Radial Maneuver, that is a maneuver that is directly towards or away from the Earth. These can be used to help shape (usually circularize) an orbit, but are fairly expensive on their own and are usually done in conjunction with an Intrack Maneuver to offset the cost for a similar result.


Image ex--


Crosstrack Maneuvers, that is maneuvers perpendicular to the direction of motion (sometimes called North/South Maneuver... which can be helpful, but also really misleading for satellites with high inclination since their direction of motion very well may be North or South!) and their effect on an orbit have as much to do with the time and position in the orbit that they occur as the magnitude and direction. Angular momentum is the heavy-hitter here in terms of limitting what is and is not possible for a satellite with the satellites orbit effectively being like a gyro, such that it's highly resistant to change. As such, the Ascending and Descending Nodes can be thought of like an 'axel' on which our Inclination can rotate. With this in mind, a Positive Crosstrack Maneuver at the Ascending Node results in an increased Inclination as in our example above, whereas a Negative Crosstrack Burn at this same position would result in a lower Inclination.


Now, if the 'axel' we mentioned is where the 'gyro' is the LEAST resistant to change, the halfway point, 90 degrees offset from that 'axel' would be when the gyro is MOST resistant to change. At this point in a satellites orbit, when it is halfway between the two Nodes, a Crosstrack burn will actually have no effect on the Inclination whatsoever; Instead, the only orbital element to change will be RAAN, in effect rotating the orbit around the North and South poles. To help with this relationship, I find it's best to think in terms of double-negatives... That is, if the satellite is South(-) of the equator and then burns in the Negative(-) crosstrack direction, it will Increase(+) its RAAN, rotating the orbit counterclockwise about the North pole as shown in the example above. A Positive(+) Crosstrack burn from this South(-) position would actually DECREASE(-) the RAAN, rotating the RAAN clockwise about the Northpole. Just the same, from the opposite side of the orbit, at the satellites Northern-most(+) point, a Positive(+) Crosstrack Maneuver would result in an INCREASED(+) RAAN, while a Negative Maneuver(-) would result in Decreased RAAN(-).


This tab also starts to introduce the user to the data from the satellite they input, describing what they may be seeing in the graphs by implementing these newly introduced analysis techniques. Mind you, this portion is somewhat a shot in the dark insomuch that the graph shown here may or may not apply to the text depending on the motion of the satellite that was run. i.e. when I describe the ‘white tails’ that trail behind an Intrack maneuver, that may not apply at all if the satellite that was run has no recorded history of Intrack maneuvers or, alternatively, the tails may be so saturated with CrossTrack maneuvers that it will appear yellow (since yellow indicates CrossTrack maneuvers) rather than white as described.

#Pocket Orbital Analyst

As mentioned at the start, Tab 3 is more or less a text-summary of what most people are looking for when they’re asking about a satellite. This tab describes the total observations we have on the satellite, the detected maneuvers, the latest and earliest observation, the orbital regime the user-input satellite is in with an indicator as to the advantages of that regime, and provides a maneuver history with a rough-wag at when the next E/W and N/S maneuvers should occur respectively, this time based purely on frequency, while ushering the user to subsequent tabs for a higher fidelity estimate for maneuver prediction.

#Satellite Position

Tab4 is a straightforward look at all available observations, first in the form of the “Sat_mnvr_df” we created earlier, then in terms of graphs showing changes to each Classical Orbital Element over time. This is the tab that a professional Orbital Analyst would probably hangout at the most.

#Satellite Maneuver Prediction

Tab5 has a strong argument as the most complex in the application. Our overall goal in this tab is to show WHEN a vehicle is most likely to maneuver given its current, untampered trajectory using usual Classical Orbital Element conditions when the vehicles has previously maneuvered as our guide. First, in order to predict future observations, it creates a dataframe where the first index is the LAST index of our “sat_mnvr_df”. It then procedurally generates 200 artificial ‘future observations’ from this starting point by pulling changes in data from the sat_mnvr_df (actual, real observations) dataframe. So as to show realistic consistency while avoiding kneejerk motions that would otherwise superimpose a maneuver (bear in mind that our goal here is not to predict HOW a maneuver would change a Classical Orbital Element, but instead, how Classical Orbital Elements influence WHEN a vehicle maneuvers,) the app bootstraps these changes, but only provided they are within one standard deviation from the mean in terms of change. This way drastic changes that otherwise indicate a maneuver should not be superimposed over our predictive observations. It is important also to bear in mind the scale difference (namely along the x axis) between these graphs and thew ones on the previous tab. These graphs only show the next 200 observations (usually 3-10 months), whereas the graphs on the previous tab show total history up until now, consisting of years in some cases. As such, slope and shape may look inconsistent at first, between the two, but in reality, if you were to “zoom in” on a portion of the corresponding graph on Tab4, you’ll likely notice the same changes to that Orbital Element over the same period of time as on Tab5, just on a more “squished” scale. This tab also introduces a new color gradient to our graphs, seeing when conditions for a maneuver have been met amid the artificial observations (determined by checking if the vehicle is within 1 standard deviation of each condition that it maneuvers at, seen in the charts on Tab3). As the color gets closer to maroon, the likelihood that the vehicle will do a corresponding E/W maneuver then reaches its highest. You can see in the chart on this tab which observations have met maneuver criteria.


(Instead of just using ROYGBIV here, with the sum of binary “were conditions met?” factors determining likelihood, my intent in future versions is to take the corollary information from the Pearson tests on the next tab and, provided the p value is low enough, make the likelihood color scale a gradient associated with both the presence of the condition AND how MUCH that Orbital Element, as a feature, historically relates to maneuvering for the satellite. If a satellite ALWAYS 100% of the time does an Intrack maneuver when it’s SMA drops to 42160 kms, for example, that should be weighed more heavily than it maneuvering 70% of the time when it’s Eccentricity reaches 0.00005)


#Hypothesis Testing

Tab6 introduces the Hypothesis test as well as some pitfall of the application itself. Generally, when conducting a hypothesis test, it's important to make the distinction that you're working with either the population or a sample thereof... This is where the limitations of our tool will begin to show themselves, though not without answer.


First of all, the scope of available data tends to go back around 2 years for each satellite. If the satellite was launched before then, it becomes clear that we're only looking at a sample, as maneuvers conducted prior to available data would not be included in our set. If the vehicle was launched within that window, we have a higher likelihood of actually capturing the population in its entirety, however, this can prove fairly disadvantageous too.


Something you learn in the trade is that most satellites have a 'check-out period' when they first go up where their functionality, mission, and trajectory are all being initialized for nominal operations later. As such, maneuvers conducted during this time period have a high likelihood of looking very different that maneuvers once nominal operations, and this period varies largely from satellite to satellite, sometimes being as small as a week and other times as large as a year, all of which can serve to skew the accuracy of predictions once nominal operations begin. Mind you, while this tool won't parse out data on the basis of proximity to a satellites launch date, it WILL issue a warning in the Pocket Orbital Analyst tab, telling you what percentage of recorded maneuvers occurred during the first 6 months of a satellites time on orbit, leaving you to trust or reject the prediction on that basis.


Another great indicator that we're dealing with a sample rather than the population is how this tool determines what constitutes a maneuver... Primarily, it uses variance in Classical Orbital Element (for Intrack and Crosstrack Maneuvers Separately,) and compares that to the usual changes from observation to observation. If the corresponding elements which would indicate a maneuver have occurred with a delta that exceeds one standard deviation of the usual delta, it assumes a maneuver has occurred.


While this is serviceable for most satellites, this can be problematic in two very specific cases: Vehicles that maneuver all the time (specifically amid more than 32% of observations,) and vehicles that cannot maneuver at all. In the case of the former, this tool will have difficulty in determining the signal from the noise. Additionally, in vehicles that cannot maneuver, this tool will likely assume that issues in position measurement or accelerative Classical Orbital Element changes due to natural perturbations are actually maneuvers. Both these issues can be resolved in the next iteration of this tool, which will calculate and superimpose J2,3, and 4 Perturbations to model motion in space more accurately such that deviations from that can be better attributed to maneuvers.
Finally, given that the tool uses changes between observations to determine if a maneuver occurred, if there's a greater time between observations, there's also a greater gap in position between observations as a result of natural motion. With that in mind, any observation that exceeds 3 standard deviations from the normal gap will not be counted as a maneuver to get rid of any 'maneuvers' that are just a result of outliers in observation consistency... This, however, doesn't mean that a maneuver didn't occur during that time, as that's still very well possible.
With all this in mind, it becomes evident that it's best to always treat our data, no matter how robust it may look, as a sample when hypothesis testing.


As for the tests themselves, we’re looking for Pearson correlation for Time Between Maneuvers and each of our features and their Deltas, being in totality Time v.s. RAAN, Inclination, Argument of Perigee, SMA, Eccentricity, RAAN Delta, Inclination Delta, Argument of Perigee Delta, SMA Delta, and Eccentricity Delta… for N/S and E/W Maneuvers separately. Particularly in terms of displaying this information, showing the corollary value from a Pearson test seemed the best way to satisfy our question of whether or not Classical Orbital Elements can be used to predict a satellites future maneuvers.
 

 





