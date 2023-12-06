import json
import pandas


def calculate_stats(seasonFile, managerFile, season):
    teamFinish = {}
    stats = json.load(open("managerStats.json"))
    managers = json.load(open(managerFile))
    df = pandas.read_csv(seasonFile)
    for i, row in df.iterrows():
        if managers[row.HomeTeam] not in teamFinish:
            teamFinish[managers[row.HomeTeam]] = [0, 0]
        if managers[row.AwayTeam] not in teamFinish:
            teamFinish[managers[row.AwayTeam]] = [0, 0]
        if managers[row.HomeTeam] not in stats:
            stats[managers[row.HomeTeam]] = {
                "pointsEarned": 0,
                "gamesPlayed": 0,
                "goalsScored": 0,
                "goalsConceded": 0,
                "comebacks": 0,
                "leagueFinish": []
            }
        if managers[row.AwayTeam] not in stats:
            stats[managers[row.AwayTeam]] = {
                "pointsEarned": 0,
                "gamesPlayed": 0,
                "goalsScored": 0,
                "goalsConceded": 0,
                "comebacks": 0,
                "leagueFinish": []
            }
        homeTeam = [managers[row.HomeTeam], row.FTHG, row.HTHG]
        awayTeam = [managers[row.AwayTeam], row.FTAG, row.HTAG]
        if homeTeam[1] > awayTeam[1]:
            stats[homeTeam[0]]["pointsEarned"] += 3
            teamFinish[homeTeam[0]][0] += 3
            teamFinish[homeTeam[0]][1] += (homeTeam[1] - awayTeam[1])
            teamFinish[awayTeam[0]][1] -= (homeTeam[1] - awayTeam[1])
            if homeTeam[2] < awayTeam[2]:
                stats[homeTeam[0]]["comebacks"] += 1
        elif homeTeam[1] < awayTeam[1]:
            stats[awayTeam[0]]["pointsEarned"] += 3
            teamFinish[awayTeam[0]][0] += 3
            teamFinish[homeTeam[0]][1] -= (awayTeam[1] - homeTeam[1])
            teamFinish[awayTeam[0]][1] += (awayTeam[1] - homeTeam[1])
            if homeTeam[2] > awayTeam[2]:
                stats[awayTeam[0]]["comebacks"] += 1
        else:
            stats[homeTeam[0]]["pointsEarned"] += 1
            stats[awayTeam[0]]["pointsEarned"] += 1
            teamFinish[homeTeam[0]][0] += 1
            teamFinish[awayTeam[0]][0] += 1
        stats[homeTeam[0]]["gamesPlayed"] += 1
        stats[homeTeam[0]]["goalsScored"] += homeTeam[1]
        stats[homeTeam[0]]["goalsConceded"] += awayTeam[1]
        stats[awayTeam[0]]["gamesPlayed"] += 1
        stats[awayTeam[0]]["goalsScored"] += awayTeam[1]
        stats[awayTeam[0]]["goalsConceded"] += homeTeam[1]
    sorted_dict = dict(sorted(teamFinish.items(), key=lambda item: item[1][0]))
    i = 20
    for key in sorted_dict.keys():
        stats[key]["leagueFinish"].append((i, season))
        i -= 1
    print(len(stats))
    with open("managerStats.json", "w") as statFile:
        json.dump(stats, statFile, indent=4)
        statFile.close()


def main():
    for year in range(2000, 2018):
        calculate_stats(f"main/Datasets/{year}-{str(year+1)[2:]}.csv", f"main/Datasets/{year}-{str(year+1)[2:]}-Managers.json", f"{year}-{str(year+1)[2:]}")

main()