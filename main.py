import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fuzzywuzzy import process

st.title('Transfer Portal Report Generator')

# Reading Excel sheets
EvanMiya = pd.read_excel("EvanMiya.xlsx")
HDI = pd.read_excel("HDI 23-24.xlsx")
HDI['Name'] = HDI['First Name'] + ' ' + HDI['Last Name']

# Allow the user to upload an Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the uploaded Excel file
    player_team_data = pd.read_excel(uploaded_file)
    
    # Rename columns if needed
    player_team_data.columns = ['Player', 'Team']
    
    st.write("Excel file uploaded successfully")
else:
    # Stop the code execution if no file is uploaded
    st.stop()

# Get the total number of players
total_players = player_team_data.shape[0]

# Create an empty element for the progress bar
progress_bar_container = st.empty()

# Reading Excel sheets
data_18_23 = pd.read_excel("Transfer Project Data 18-23.xlsx")
data_24 = pd.read_excel("Transfer Project Data 24.xlsx")

combined_data = pd.concat([data_18_23, data_24], ignore_index=True)

# Update WS/40 for players with non-zero minutes played
non_zero_mp = combined_data['MP'] != 0
combined_data.loc[non_zero_mp, 'WS/40'] = (combined_data.loc[non_zero_mp, 'WS'] / combined_data.loc[non_zero_mp, 'MP']) * 40

# Reading Excel sheets
bartt_data = pd.read_excel("Barttorvik.xlsx")

# Function to perform fuzzy matching
def find_closest_match(item, item_list):
    match, score = process.extractOne(item, item_list)
    if score >= 90:  # Adjust the threshold as needed
        return match
    else:
        return None
    
# Filter data for the 23-24 season for duplicate name checking
player_data_23_24 = combined_data[combined_data['Year'] == '23-24']

# Filter data for the 23-24 season for duplicate name checking
player_data_bartt = bartt_data[bartt_data['Yr'] == '2024']

# Loop through each player
for index, row in player_team_data.iterrows():
    player_name = row['Player']
    team_name = row['Team']
    
    # Update progress bar
    progress_bar_container.progress((index + 1) / total_players, f"Processing player {index+1} of {total_players}")
    
    # Perform fuzzy matching to find the closest player name
    closest_match = find_closest_match(player_name, EvanMiya['Name'].tolist())
    
    if closest_match:
        # Check if the player name appears more than once in EvanMiya dataset
        if EvanMiya['Name'].value_counts()[closest_match] > 1:
            
            closest_match_team = find_closest_match(team_name, EvanMiya['Team'].tolist())
            
            if closest_match_team:
                player_data = EvanMiya[(EvanMiya['Name'] == closest_match) & (EvanMiya['Team'] == closest_match_team)].iloc[:, list(range(2, 11)) + list(range(14, len(EvanMiya.columns)))]
                
                # Perform fuzzy matching to find the closest player name in HDI dataset
                closest_match_HDI = find_closest_match(player_name, HDI['Name'].tolist())
                if closest_match_HDI:
                    player_HDI = HDI[HDI['Name'] == closest_match_HDI]
                    player_data['HDI Rating'] = player_HDI['RATING'].values[0]

                # Display tables
                st.write(f"## {closest_match}")
                st.write(f"### EvanMiya Data and HDI Rating")
                st.table(player_data)
                
                # Visualization with matplotlib
                fig, ax = plt.subplots()
                ax.scatter(EvanMiya['OBPR'], EvanMiya['DBPR'], label="All Players")
                ax.scatter(player_data['OBPR'], player_data['DBPR'], color='red', label=closest_match)
                ax.set_title(f"23-24 Offensive BPR and Defensive BPR")
                ax.set_xlabel("OBPR")
                ax.set_ylabel("DBPR")
                ax.legend()
                st.pyplot(fig)
                
                # Perform fuzzy matching to find the closest player name
                closest_match_cref = find_closest_match(player_name, combined_data['Player'].tolist())
                
                if closest_match:
                    # Check for duplicate names in 23-24 season data
                    duplicate_names = player_data_23_24['Player'].duplicated()
                    
                    if duplicate_names.any():
                        # If there are duplicate names, filter data by team only for players with duplicate names
                        closest_match_team_cref = find_closest_match(team_name, combined_data['School'].tolist())
                        
                        if closest_match_team_cref:
                            filtered_data = combined_data[(combined_data['Player'] == closest_match_cref) & (combined_data['School'] == closest_match_team_cref)]
                            
                            # Sort the filtered data by player name and year
                            filtered_data.sort_values(by=['Player', 'Year'], inplace=True)

                            # Reset the index of the filtered data
                            filtered_data.reset_index(drop=True, inplace=True)
                            
                            st.write(f"### CBB Reference Data")
                            st.table(filtered_data)
                        else:
                            st.write(f"No matching player found for {player_name}, {team_name}")
                    else:
                        # If no duplicate names, append all data for the player
                        filtered_data = combined_data[combined_data['Player'] == closest_match_cref]
                        
                        # Sort the filtered data by player name and year
                        filtered_data.sort_values(by=['Player', 'Year'], inplace=True)

                        # Reset the index of the filtered data
                        filtered_data.reset_index(drop=True, inplace=True)
                        
                        st.write(f"### CBB Reference Data")
                        st.table(filtered_data)
                else:
                    st.write(f"No matching player found for {player_name}, {team_name}")
                    
                # Perform fuzzy matching to find the closest player name
                closest_match_bartt = find_closest_match(player_name, bartt_data['PLAYER'].tolist())
                
                if closest_match:
                    # Check for duplicate names in 23-24 season data
                    duplicate_name = player_data_bartt['PLAYER'].duplicated()
                    
                    if duplicate_name.any():
                        # If there are duplicate names, filter data by team only for players with duplicate names
                        closest_match_team_bartt = find_closest_match(team_name, bartt_data['TEAM'].tolist())
                        
                        if closest_match_team_bartt:
                            filter_data = bartt_data[(bartt_data['PLAYER'] == closest_match_bartt) & (bartt_data['TEAM'] == closest_match_team_bartt)]
                            
                            # Sort the filtered data by player name and year
                            filter_data.sort_values(by=['PLAYER', 'Yr'], inplace=True)

                            # Reset the index of the filtered data
                            filter_data.reset_index(drop=True, inplace=True)
                            
                            st.write(f"### Barttorvik Data")
                            st.table(filter_data)
                        else:
                            st.write(f"No matching player found for {player_name}, {team_name}")
                    else:
                        # If no duplicate names, append all data for the player
                        filter_data = bartt_data[bartt_data['PLAYER'] == closest_match_bartt]
                        
                        # Sort the filtered data by player name and year
                        filter_data.sort_values(by=['PLAYER', 'Yr'], inplace=True)

                        # Reset the index of the filtered data
                        filter_data.reset_index(drop=True, inplace=True)
                        
                        st.write(f"### Barttorvik Data")
                        st.table(filter_data)
                else:
                    st.write(f"No matching player found for {player_name}, {team_name}")
            else:
                st.write(f"No matching player found for {player_name}, {team_name}")
        else:
            player_data = EvanMiya[EvanMiya['Name'] == closest_match].iloc[:, list(range(2, 11)) + list(range(14, len(EvanMiya.columns)))]
            
            # Perform fuzzy matching to find the closest player name in HDI dataset
            closest_match_HDI = find_closest_match(player_name, HDI['Name'].tolist())
            if closest_match_HDI:
                player_HDI = HDI[HDI['Name'] == closest_match_HDI]
                player_data['HDI Rating'] = player_HDI['RATING'].values[0]

            # Display tables
            st.write(f"## {closest_match}")
            st.write(f"### EvanMiya Data and HDI Rating")
            st.table(player_data)
            
            # Visualization with matplotlib
            fig, ax = plt.subplots()
            ax.scatter(EvanMiya['OBPR'], EvanMiya['DBPR'], label="All Players")
            ax.scatter(player_data['OBPR'], player_data['DBPR'], color='red', label=closest_match)
            ax.set_title(f"23-24 Offensive BPR and Defensive BPR")
            ax.set_xlabel("OBPR")
            ax.set_ylabel("DBPR")
            ax.legend()
            st.pyplot(fig)
            
            # Perform fuzzy matching to find the closest player name
            closest_match_cref = find_closest_match(player_name, combined_data['Player'].tolist())
                
            if closest_match:   
                # Check for duplicate names in 23-24 season data
                duplicate_names = player_data_23_24['Player'].duplicated()
                    
                if duplicate_names.any():
                    # If there are duplicate names, filter data by team only for players with duplicate names
                    closest_match_team_cref = find_closest_match(team_name, combined_data['School'].tolist())
                        
                    if closest_match_team_cref:
                        filtered_data = combined_data[(combined_data['Player'] == closest_match_cref) & (combined_data['School'] == closest_match_team_cref)]
                            
                        # Sort the filtered data by player name and year
                        filtered_data.sort_values(by=['Player', 'Year'], inplace=True)

                        # Reset the index of the filtered data
                        filtered_data.reset_index(drop=True, inplace=True)
                            
                        st.write(f"### CBB Reference Data")
                        st.table(filtered_data)
                    else:
                        st.write(f"No matching player found for {player_name}, {team_name}")
                else:
                    # If no duplicate names, append all data for the player
                    filtered_data = combined_data[combined_data['Player'] == closest_match_cref]
                        
                    # Sort the filtered data by player name and year
                    filtered_data.sort_values(by=['Player', 'Year'], inplace=True)

                    # Reset the index of the filtered data
                    filtered_data.reset_index(drop=True, inplace=True)
                        
                    st.write(f"### CBB Reference Data")
                    st.table(filtered_data)
            else:
                st.write(f"No matching player found for {player_name}, {team_name}")
                    
            # Perform fuzzy matching to find the closest player name
            closest_match_bartt = find_closest_match(player_name, bartt_data['PLAYER'].tolist())
                
            if closest_match:
                # Check for duplicate names in 23-24 season data
                duplicate_name = player_data_bartt['PLAYER'].duplicated()
                    
                if duplicate_name.any():
                    # If there are duplicate names, filter data by team only for players with duplicate names
                    closest_match_team_bartt = find_closest_match(team_name, bartt_data['TEAM'].tolist())
                        
                    if closest_match_team_bartt:
                        filter_data = bartt_data[(bartt_data['PLAYER'] == closest_match_bartt) & (bartt_data['TEAM'] == closest_match_team_bartt)]
                            
                        # Sort the filtered data by player name and year
                        filter_data.sort_values(by=['PLAYER', 'Yr'], inplace=True)

                        # Reset the index of the filtered data
                        filter_data.reset_index(drop=True, inplace=True)
                        
                        st.write(f"### Barttorvik Data")
                        st.table(filter_data)
                    else:
                        st.write(f"No matching player found for {player_name}, {team_name}")
                else:
                    # If no duplicate names, append all data for the player
                    filter_data = bartt_data[bartt_data['PLAYER'] == closest_match_bartt]
                    
                    # Sort the filtered data by player name and year
                    filter_data.sort_values(by=['PLAYER', 'Yr'], inplace=True)

                    # Reset the index of the filtered data
                    filter_data.reset_index(drop=True, inplace=True)
                    
                    st.write(f"### Barttorvik Data")
                    st.table(filter_data)
            else:
                st.write(f"No matching player found for {player_name}, {team_name}")
    else:
        st.write(f"No matching player found for {player_name}, {team_name}")
    
    progress_bar_container.empty()
        
