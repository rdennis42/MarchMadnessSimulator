# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import random
import csv
import time


# A tournament mainly holds a list of teams imported from the CSV
class Tournament:
    def __init__(self):
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)


# A team holds the teams name, power ranking, and seed.
# Seed isn't used right now but might be usable for a different picking algorithm
class Team:
    def __init__(self, name: str, power_ranking: float, seed: int):
        self.name = name
        self.power_ranking = power_ranking
        self.seed = seed

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


# ResultSet holds both the actual tournament results, and each set of bracket picks
class ResultSet:
    def __init__(self, round_1_results, sweet_sixteen, elite_eight, final_four, finals, champion, upsets):
        self.round_1_results = round_1_results
        self.sweet_sixteen = sweet_sixteen
        self.elite_eight = elite_eight
        self.final_four = final_four
        self.finals = finals
        self.champion = champion
        self.upsets = upsets

    def __str__(self):
        return "Round 1 results: " + str(self.round_1_results) + \
               "\nSweet Sixteen: " + str(self.sweet_sixteen) + \
               "\nElite Eight: " + str(self.elite_eight) + \
               "\nFinal Four: " + str(self.final_four) + \
               "\nFinals: " + str(self.finals) + \
               "\nChampion: " + str(self.champion) + "\n"


# Make a pick for a specific game. Uses the same formula for the game simulation, but adds in risk value.
# Positive risk value makes it more likely to pick upsets, negative makes it less likely.

# Return whether this is a predicted upset, and the picked team
def make_pick(team1: Team, team2: Team, risk):
    if risk:
        return play_game(team1, team2)
    elif team1.power_ranking > team2.power_ranking:
        return False, team1
    else:
        return False, team2


# make picks for the whole bracket
def create_picks(tournament: Tournament, upset):
    round_1_results = []
    sweet_sixteen = []
    elite_eight = []
    final_four = []
    finals = []

    # pick risk based off a bell curve from roughly -0.3 to 0
    # MODIFY THIS TO CHANGE BOT VARIANCE
    risk = random.gauss(0, 0.1) if upset else 0

    # Pick up until the final four for each region
    for i in range(4):
        # Never pick a 16-1 upset. Not sure if this is best or not, can easily re-enable the chance.
        # 1-2% of brackets will pick a 16 upset if enabled, typically making them useless.
        round_1_results.append(make_pick(tournament.teams[i*16+0], tournament.teams[i*16+15], 0))
        round_1_results.append(make_pick(tournament.teams[i*16+7], tournament.teams[i*16+8], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+4], tournament.teams[i*16+11], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+3], tournament.teams[i*16+12], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+5], tournament.teams[i*16+10], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+2], tournament.teams[i*16+13], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+6], tournament.teams[i*16+9], risk))
        round_1_results.append(make_pick(tournament.teams[i*16+1], tournament.teams[i*16+14], risk))

        sweet_sixteen.append(make_pick(round_1_results[i*8+0][1], round_1_results[i*8+1][1], risk))
        sweet_sixteen.append(make_pick(round_1_results[i*8+2][1], round_1_results[i*8+3][1], risk))
        sweet_sixteen.append(make_pick(round_1_results[i*8+4][1], round_1_results[i*8+5][1], risk))
        sweet_sixteen.append(make_pick(round_1_results[i*8+6][1], round_1_results[i*8+7][1], risk))

        elite_eight.append(make_pick(sweet_sixteen[i*4+0][1], sweet_sixteen[i*4+1][1], risk))
        elite_eight.append(make_pick(sweet_sixteen[i*4+2][1], sweet_sixteen[i*4+3][1], risk))

        final_four.append(make_pick(elite_eight[i*2+0][1], elite_eight[i*2+1][1], risk))

    finals.append(make_pick(final_four[0][1], final_four[1][1], risk))
    finals.append(make_pick(final_four[2][1], final_four[3][1], risk))

    champion = make_pick(finals[0][1], finals[1][1], risk)

    # add up all the upset picks for final stats
    upsets = 0
    for game in round_1_results:
        if game[0]:
            upsets += 1
    for game in sweet_sixteen:
        if game[0]:
            upsets += 1
    for game in elite_eight:
        if game[0]:
            upsets += 1
    for game in final_four:
        if game[0]:
            upsets += 1
    for game in finals:
        if game[0]:
            upsets += 1
    if champion[0]:
        upsets += 1

    return ResultSet(round_1_results, sweet_sixteen, elite_eight, final_four, finals, champion, upsets)


def score_picks(predictions: ResultSet, results: ResultSet):
    score = 0
    for i in range(32):
        if predictions.round_1_results[i][1] == results.round_1_results[i][1]:
            score += 1

    for i in range(16):
        if predictions.sweet_sixteen[i][1] == results.sweet_sixteen[i][1]:
            score += 2

    for i in range(8):
        if predictions.elite_eight[i][1] == results.elite_eight[i][1]:
            score += 4

    for i in range(4):
        if predictions.final_four[i][1] == results.final_four[i][1]:
            score += 8

    for i in range(2):
        if predictions.finals[i][1] == results.finals[i][1]:
            score += 16

    if predictions.champion[1] == results.champion[1]:
        score += 32

    return score


def play_tournament(tournament):
    round_1_results = []
    sweet_sixteen = []
    elite_eight = []
    final_four = []
    finals = []
    for i in range(4):
        round_1_results.append(play_game(tournament.teams[i * 16 + 0], tournament.teams[i * 16 + 15]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 7], tournament.teams[i * 16 + 8]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 4], tournament.teams[i * 16 + 11]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 3], tournament.teams[i * 16 + 12]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 5], tournament.teams[i * 16 + 10]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 2], tournament.teams[i * 16 + 13]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 6], tournament.teams[i * 16 + 9]))
        round_1_results.append(play_game(tournament.teams[i * 16 + 1], tournament.teams[i * 16 + 14]))

        sweet_sixteen.append(play_game(round_1_results[i * 8 + 0][1], round_1_results[i * 8 + 1][1]))
        sweet_sixteen.append(play_game(round_1_results[i * 8 + 2][1], round_1_results[i * 8 + 3][1]))
        sweet_sixteen.append(play_game(round_1_results[i * 8 + 4][1], round_1_results[i * 8 + 5][1]))
        sweet_sixteen.append(play_game(round_1_results[i * 8 + 6][1], round_1_results[i * 8 + 7][1]))

        elite_eight.append(play_game(sweet_sixteen[i * 4 + 0][1], sweet_sixteen[i * 4 + 1][1]))
        elite_eight.append(play_game(sweet_sixteen[i * 4 + 2][1], sweet_sixteen[i * 4 + 3][1]))

        final_four.append(play_game(elite_eight[i * 2 + 0][1], elite_eight[i * 2 + 1][1]))

    finals.append(play_game(final_four[0][1], final_four[1][1]))
    finals.append(play_game(final_four[2][1], final_four[3][1]))

    champion = play_game(finals[0][1], finals[1][1])
    upsets = 0

    for game in round_1_results:
        if game[0]:
            upsets += 1
    for game in sweet_sixteen:
        if game[0]:
            upsets += 1
    for game in elite_eight:
        if game[0]:
            upsets += 1
    for game in final_four:
        if game[0]:
            upsets += 1
    for game in finals:
        if game[0]:
            upsets += 1
    if champion[0]:
        upsets += 1
    return ResultSet(round_1_results, sweet_sixteen, elite_eight, final_four, finals, champion, upsets)


def setup_tournament():
    tournament = Tournament()
    with open('forecast.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            tournament.add_team(Team(row[0], float(row[2]), int(row[3])))
    return tournament


# Games are decided by the power rankings and odds from fivethirtyeight.com
# Power rankings here: Go to table view and pick pre-tournament
# https://projects.fivethirtyeight.com/2022-march-madness-predictions/
# Formula here: https://fivethirtyeight.com/features/how-our-march-madness-predictions-work-2/
# Risk parameter allows for variance in simulated bracket picks. Higher risk value should result in picking more upsets
def play_game(team1: Team, team2: Team, risk=0):
    # This formula decides odds of winning a game
    diff = abs(team1.power_ranking - team2.power_ranking) * -1
    odds = 1 / (1 + pow(10, diff * 30.464 / 400))

    # Only used in picks, skew towards or away from an upset
    # This can/should be refined
    rand = random.random() + risk

    # Only really counts as an upset if there's a noticeable difference in power ranking
    upset = rand > odds > 0.6

    if rand < odds and team1.power_ranking > team2.power_ranking:
        return upset, team1
    else:
        return upset, team2


if __name__ == '__main__':
    tournament = setup_tournament()
    naive_picks = create_picks(tournament, False)

    naive_bracket_wins = 0
    total_actual_upsets = 0
    total_picked_upsets = 0

    iterations = 100000
    players = 10

    print("Running " + str(iterations) + " iterations with " + str(players) + " players.")

    start_time = time.perf_counter()

    # run x iterations of complete simulation
    for i in range(iterations):
        if i % 1000 == 0:
            print("Starting iteration " + str(i))
        bracket_pool = [naive_picks]
        results = play_tournament(tournament)
        scores = [score_picks(naive_picks, results)]
        best_bracket_index = 0
        high_score = scores[0]

        # create a bracket for each non-naive player
        for j in range(players - 1):
            bracket_pool.append(create_picks(tournament, True))
            scores.append(score_picks(bracket_pool[j+1], results))
            total_picked_upsets += bracket_pool[j+1].upsets
            if scores[j+1] > high_score:
                high_score = scores[j+1]
                best_bracket_index = (j+1)

        total_actual_upsets += results.upsets
        if best_bracket_index == 0:
            naive_bracket_wins += 1

    end_time = time.perf_counter()
    runtime = round(end_time - start_time, 2)
    runtime_minutes = int(runtime / 60)
    runtime_string = str(runtime_minutes) + "m " + str(round(runtime - (runtime_minutes * 60))) + "s"
    expected_wins = round(iterations / players)
    percent_improvement = round(100 * (naive_bracket_wins-expected_wins) / expected_wins)
    average_actual_upsets = total_actual_upsets / iterations
    average_picked_upsets = total_picked_upsets / iterations / players

    print("Simulation complete")

    print("\nAverage number of actual upsets: " + str(average_actual_upsets))
    print("Average number of predicted upsets: " + str(average_picked_upsets))

    print("Naive bracket wins: " + str(naive_bracket_wins))
    print("Expected wins: " + str(round(iterations / players)))
    print("Percent improvement: " + str(percent_improvement) + "%")

    print("Runtime: " + runtime_string)

