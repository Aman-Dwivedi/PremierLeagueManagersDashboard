import pandas
import json

clubs = pandas.read_csv("managers/club.csv")
managers = pandas.read_csv("managers/manager.csv")
clubManagers = pandas.read_csv("managers/manager_club.csv")
correctNames = {}
clubManagerDict = {}

def find_manager(teamName, year):
    club = clubs.loc[clubs["club_name"] == teamName]
    if club.size == 0:
        clubName = input(f"Could not find a match for {teamName}. Please input the correct name\n")
        club = clubs.loc[clubs["club_name"] == clubName]
    try:
        managerId = clubManagers.loc[(clubManagers["club_id"] == club.club_id.tolist()[0]) & (clubManagers["season"] == f"{year}/{str(year+1)[2:]}")].manager_id.to_list()[0]
    except:
        print(teamName, club)
        print(f"{year}/{str(year+1)[2:]}")
        exit()
    managerName = managers.loc[managers["manager_id"] == managerId].manager_name.to_list()[0]
    return managerName

def add_managers_to_csv(file, year):
    df = pandas.read_csv(file)
    for i, row in df.iterrows():
        if row.HomeTeam not in clubManagerDict:
            clubManagerDict[row.HomeTeam] = find_manager(row.HomeTeam, year)
        if row.AwayTeam not in clubManagerDict:
            clubManagerDict[row.AwayTeam] = find_manager(row.AwayTeam, year)
    with open(f"main/Datasets/{year}-{str(year+1)[2:]}-Managers.json", "w") as outfile:
        json.dump(clubManagerDict, outfile)

def main():
    global clubManagerDict
    for year in range(2000, 2020):
        add_managers_to_csv(f"main/Datasets/{year}-{str(year+1)[2:]}.csv", year)
        clubManagerDict = dict()

main()