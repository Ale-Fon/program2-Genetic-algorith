import random
import math
from collections import defaultdict

#variables from the assignment on canvas.
FACILITATORS = ["Lock", "Glen", "Banks", "Richards", "Shaw", "Singer", "Uther", "Tyler", "Numen", "Zeldin"]

ROOMS = {"Slater 003": 45,"Roman 216": 30,"Loft 206": 75,"Roman 201": 50,"Loft 310": 108,"Beach 201": 60,"Beach 301": 75,"Logos 325": 450,"Frank 119": 60,
}

TIMES = ["10 am", "11 am", "12 pm", "1 pm", "2 pm", "3 pm"]

ACTIVITIES = {"SLA100A": {"enroll": 50, "preferred": ["Glen", "Lock", "Banks", "Zeldin"], "other": ["Numen", "Richards"]},
    "SLA100B": {"enroll": 50, "preferred": ["Glen", "Lock", "Banks", "Zeldin"], "other": ["Numen", "Richards"]},
    "SLA191A": {"enroll": 50, "preferred": ["Glen", "Lock", "Banks", "Zeldin"], "other": ["Numen", "Richards"]},
    "SLA191B": {"enroll": 50, "preferred": ["Glen", "Lock", "Banks", "Zeldin"], "other": ["Numen", "Richards"]},
    "SLA201": {"enroll": 50, "preferred": ["Glen", "Banks", "Zeldin", "Shaw"], "other": ["Numen", "Richards", "Singer"]},
    "SLA291": {"enroll": 50, "preferred": ["Lock", "Banks", "Zeldin", "Singer"], "other": ["Numen", "Richards", "Shaw", "Tyler"]},
    "SLA303": {"enroll": 60, "preferred": ["Glen", "Zeldin", "Banks"], "other": ["Numen", "Singer", "Shaw"]},
    "SLA304": {"enroll": 25, "preferred": ["Glen", "Banks", "Tyler"], "other": ["Numen", "Singer", "Shaw", "Richards", "Uther", "Zeldin"]},
    "SLA394": {"enroll": 20, "preferred": ["Tyler", "Singer"], "other": ["Richards", "Zeldin"]},
    "SLA449": {"enroll": 60, "preferred": ["Tyler", "Singer", "Shaw"], "other": ["Zeldin", "Uther"]},
    "SLA451": {"enroll": 100, "preferred": ["Tyler", "Singer", "Shaw"], "other": ["Zeldin", "Uther", "Richards", "Banks"]},
}

#I made this class in order to be able to set up the activities with the rooms, time, and facilitator for the program. 
class Schedule:
    def __init__(self):
        self.assignments = {}
        for activity in ACTIVITIES:
            room = random.choice(list(ROOMS.keys()))
            time = random.choice(TIMES)
            facilitator = random.choice(FACILITATORS)
            self.assignments[activity] = (room, time, facilitator)
    #function to just make a copy of the schedule, as the new copy takes the assignments from the old one.
    def copy(self):
        new_schedule = Schedule()
        new_schedule.assignments = self.assignments.copy()
        return new_schedule

    #Function to help set up the mutation for the activities
    def mutation(self, mutation_rate=0.01):
        for activity in self.assignments:
            if random.random() < mutation_rate:
                room = random.choice(list(ROOMS.keys()))
                time = random.choice(TIMES)
                facilitator = random.choice(FACILITATORS)
                self.assignments[activity] = (room, time, facilitator)

    #This function will help defind the fitness in each activities in the assignments variable.
    def fitness(self):
        score = 0.0
        used_slots = defaultdict(list)
        facilitator_slots = defaultdict(list)
        facilitator_load = defaultdict(int)

        for act, (room, time, fac) in self.assignments.items():
            enroll = ACTIVITIES[act]["enroll"]
            room_cap = ROOMS[room]
            used_slots[(time, room)].append(act)
            facilitator_slots[time].append(fac)
            facilitator_load[fac] += 1

            if room_cap < enroll:
                score -= 0.5
            elif room_cap > 6 * enroll:
                score -= 0.4
            elif room_cap > 3 * enroll:
                score -= 0.2
            else:
                score += 0.3


            if fac in ACTIVITIES[act]['preferred']:
                score += 0.5
            elif fac in ACTIVITIES[act]['other']:
                score += 0.2
            else:
                score -= 0.1

        for (time, room), acts in used_slots.items():
            if len(acts) > 1:
                score -= 0.5 * (len(acts) - 1)

        for time, facs in facilitator_slots.items():
            for f in FACILITATORS:
                if facs.count(f) > 1:
                    score -= 0.2

        for f, load in facilitator_load.items():
            if load > 4:
                score -= 0.5
            elif load <= 2:
                if f != "Tyler":
                    score -= 0.4

        # This function is a specific scheduling rules for Sla101 and sla191
        def hour(t):
            return int(t.split()[0]) + (0 if 'am' in t else 12)

        times_by_act = {act: hour(time) for act, (_, time, _) in self.assignments.items()}
        rooms_by_act = {act: room for act, (room, _, _) in self.assignments.items()}

        def delta_time(a1, a2):
            return abs(times_by_act[a1] - times_by_act[a2])

        if delta_time("SLA100A", "SLA100B") > 4:
            score += 0.5
        elif times_by_act["SLA100A"] == times_by_act["SLA100B"]:
            score -= 0.5

        if delta_time("SLA191A", "SLA191B") > 4:
            score += 0.5
        elif times_by_act["SLA191A"] == times_by_act["SLA191B"]:
            score -= 0.5

        for a in ["SLA191A", "SLA191B"]:
            for b in ["SLA100A", "SLA100B"]:
                dt = delta_time(a, b)
                if dt == 1:
                    score += 0.5
                    r1, r2 = rooms_by_act[a], rooms_by_act[b]
                    if ("Roman" in r1 or "Beach" in r1) != ("Roman" in r2 or "Beach" in r2):
                        score -= 0.4
                elif dt == 2:
                    score += 0.25
                elif times_by_act[a] == times_by_act[b]:
                    score -= 0.25

        return score

    #This is the final results from the fitness, it will append each result from room, time, and fac and place them inside the array called result.
    def __str__(self):
        result = []
        for act, (room, time, fac) in self.assignments.items():
            result.append(f"{act}: Room={room}, Time={time}, Facilitator={fac}")
        return "\n".join(result)

#This function uses softmax to help convert the fitness scores
def softmax(x):
    e_x = [math.exp(i) for i in x]
    total = sum(e_x)
    return [i / total for i in e_x]

#This function helps pick out the parents from the population.
def select_parents(population):
    fitnesses = [s.fitness() for s in population]
    probs = softmax(fitnesses)
    return random.choices(population, weights=probs, k=2)

#the crossover function helps find out which child can crossover to another activitiy inside the assignment variable.
def crossover(p1, p2):
    child = Schedule()
    for act in ACTIVITIES:
        if random.random() < 0.5:
            child.assignments[act] = p1.assignments[act]
        else:
            child.assignments[act] = p2.assignments[act]
    return child

#Function that will run at least 100 generations and takes the help from all the other functions to be able to find the improvement till the final generation. Once done, it will output the results into best_schedule.txt
def runGeneticAlgorithm(generations=100, pop_size=500):
    population = [Schedule() for _ in range(pop_size)]
    mutationRate = 0.01

    best = max(population, key=lambda s: s.fitness())
    print("starting best fitness:", best.fitness())

    for gen in range(generations):
        newPop = []
        for _ in range(pop_size):
            p1, p2 = select_parents(population)
            child = crossover(p1, p2)
            child.mutation(mutationRate)
            newPop.append(child)

        avg_old = sum(s.fitness() for s in population) / pop_size
        avg_new = sum(s.fitness() for s in newPop) / pop_size

        if avg_new - avg_old < 0.01 * avg_old:
            print(f"Generation {gen}: < 1% improvement")
            break

        population = newPop
        mutationRate /= 2
        currentBest = max(population, key=lambda s: s.fitness())
        if currentBest.fitness() > best.fitness():
            best = currentBest

    print("The final best fitness is:", best.fitness())
    with open("best_schedule.txt", "w") as f:
        f.write(str(best))

#the main to run the program
if __name__ == "__main__":
    runGeneticAlgorithm()