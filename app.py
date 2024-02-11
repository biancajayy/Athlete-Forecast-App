import pandas as pd
import numpy as np

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    # Attempt to get the result from URL parameters, defaulting to None if not present
    result = request.args.get('result', None)
    return render_template('index.html', result=result)

@app.route('/submit', methods=['POST'])
def submit():
    # Extracting the form data
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    rating = float(request.form['rating'])
    stars = float(request.form['stars'])

    #algorithm starts
    url = '/Users/chloenicola/Desktop/GT 24/Hacklytics/Hacklytics2024/HSRecruitStats.csv'
    hsDf = pd.read_csv(url)
    hsDf = hsDf.drop(columns=['Name','Unnamed: 6','Unnamed: 11','Id','AthleteId'])
    hsDf = hsDf.drop(hsDf.index[1973:2476])
    #Transform variables needed for calculations into arrays
    stat_columns = ['Full Name','Height','Weight','Stars','Rating']
    array_selected = hsDf[stat_columns[1:5]]
    array_selected_with_name = hsDf[stat_columns]
    hs_stats_array = array_selected.to_numpy()
    hs_stats_array_with_name = array_selected_with_name.to_numpy()
    print(hs_stats_array)
    #Normalize values in array (height, weight, stars, rating)
    from sklearn.preprocessing import StandardScaler

    #Create a Scaler object
    scaler = StandardScaler()

    #Standardize to proceed in Euclidean Distance calculations
    standardized_data = scaler.fit_transform(array_selected)
    print(standardized_data)
    #create input data
    appendedArr = np.array([height, weight, stars, rating])

    heightIndex = 0
    weightIndex = 1
    starIndex = 2
    ratingIndex = 3

    #add input data to original  data set and normalize all data together
    result = np.vstack([array_selected, appendedArr])
    normalizedRes = scaler.fit_transform(result)

    skillRes = normalizedRes
    heightWeightRes = normalizedRes

    #Skill Calculations
    #add a weight of 5 to star data
    skillRes[:, starIndex] *= 3
    skillRes[:, ratingIndex] *= 6

    #label standardized data
    normalizedSkill = skillRes[-1]
    skillRes = skillRes[:-1]

    Skill_distances = np.linalg.norm(normalizedSkill - skillRes, axis=1)
    skill_indeces = np.argsort(Skill_distances)[:10]

    #Height and Weight Calculations
    heightWeightRes[:, heightIndex] *= 8
    heightWeightRes[:, weightIndex] *= 8
    heightWeightRes[:, starIndex] *= 2
    heightWeightRes[:, ratingIndex] *= 2

    #label standardized data
    normalizedHeightWeight = heightWeightRes[-1]
    heightWeightRes = heightWeightRes[:-1]

    HW_distances = np.linalg.norm(normalizedHeightWeight - heightWeightRes, axis=1)
    HW_indeces = np.argsort(HW_distances)[:10]
    #print(skill_indeces)
    #names_by_skill = hs_stats_array_with_name[skill_indeces][0]
    #print(names_by_skill)
    #print(HW_indeces)

    name1 = None
    name2 = None

    ESPN = '/Users/chloenicola/Desktop/GT 24/Hacklytics/Hacklytics2024/ESPN WR Stats.csv'
    ESPNdf=pd.read_csv(ESPN)
    ESPNdf = ESPNdf.drop(columns=['First Name', 'Last name'])
    ESPNdf.head(20)
    counter = 0


    for index in skill_indeces:
        player = hs_stats_array_with_name[index][0]
        player_stats_skill = ESPNdf[ESPNdf['Name'] == player]
        if player_stats_skill.empty and (counter <= 9):
            counter += 1
            continue
        elif (counter <= 9):
            name1 = player
            rushing1 = player_stats_skill.iloc[0,3]
            touchdowns1 = int(player_stats_skill.iloc[0,6])
            break


    for index in HW_indeces:
        player = hs_stats_array_with_name[index][0]
        player_stats_HW = ESPNdf[ESPNdf['Name'] == player]
        if player_stats_HW.empty and (counter <= 9):
            counter += 1
            continue
        elif (counter <= 9):
            name2 = player
            rushing2 = player_stats_HW.iloc[0,3]
            touchdowns2 = int(player_stats_HW.iloc[0,6])
            break

    if name1 == name2:
        message = f"Using data from their recruitment season, {name1} is the athlete most similar to your profile.\n{name1} had {rushing1} rushing yards and {touchdowns1} touchdowns this past season!"
    elif height < 60 or weight < 100 or rating < 0.1000:
        message = "Unfortunately, there are no athletes whose data during their recruitment seasons matches your profile."
    else:
        message = f"Using data from their recruitment seasons, {name1} is the athlete most similar to your profile by height and weight, and {name2} is the athlete most similar to your profile based on stars and rating.\n{name1} had {rushing1} rushing yards and {touchdowns1} touchdowns this past season, and {name2} had {rushing2} rushing yards and {touchdowns2} touchdowns this past season!"

    return redirect(url_for('index', result = message))

if __name__ == '__main__':
    app.run(debug=True)
