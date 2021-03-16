import random

# Map dimensions
rows = 10
cols = 15

# Map symbols
wall = '#'
floor = ' '
goomba = 'G'
mario = 'M'
end = 'E'

# Map class that handles moving Mario
# Takes in:
# map - list of lists
# pos - tuple coordinate in the form (X, Y)
# exit - same as above
class Map:
  def __init__(self, map, pos, exit):
    self.map = map
    self.pos = pos
    self.exit = exit
    self.penalties = 0
    self.dead = False

  # Determine which direction to move in
  def up(self):
    # Check to see if in bounds
    if self.pos[1] - 1 >= 0:
      # Define move and initiate
      pos = (self.pos[0], self.pos[1] - 1)
      self.move(pos)
  def down(self):
    if self.pos[1] + 1 < rows:
      pos = (self.pos[0], self.pos[1] + 1)
      self.move(pos)
  def left(self):
    if self.pos[0] - 1 >= 0:
      pos = (self.pos[0] - 1, self.pos[1])
      self.move(pos)
  def right(self):
    if self.pos[0] + 1 < cols:
      pos = (self.pos[0] + 1, self.pos[1])
      self.move(pos)

  # Actually move player
  def move(self, pos):
    # If wall is hit, add to penalties (used for fitness function)
    if (self.is_wall(pos)):
      self.penalties += 1

    # Mario dies instantly if he lands on a goomba
    if (self.is_goomba(pos)):
      self.dead = True

    # Replace floor/exit symbol with Mario
    if (self.is_done(pos) or self.is_floor(pos)):
      self.map[self.pos[1]][self.pos[0]] = floor
      self.map[pos[1]][pos[0]] = mario
      self.pos = pos

  # Check for certain map symbols
  def is_wall(self, pos):
    return self.map[pos[1]][pos[0]] == wall
  def is_done(self, pos):
    return self.map[pos[1]][pos[0]] == end
  def is_floor(self, pos):
    return self.map[pos[1]][pos[0]] == floor
  def is_goomba(self, pos):
    return self.map[pos[1]][pos[0]] == goomba

  # Reset map after fitness evaluation
  def reset(self):
    if (self.pos != (0,2)):
        self.move((0,2))
    self.map[7][14] = end
    self.penalties = 0

  # Print map as visual aid
  def __str__(self):
    return '\n'.join([''.join([str(char) for char in row]) for row in self.map])

# Genetic algorithm class
# Takes in:
# map - a Map object
# move_limit - maximum amount of moves allowed in chromosome
# population_size - how many chromosomes in the population
# mutation_chance - what are the odds of a chromosome mutating? (0-1)
class Genetic:
  def __init__(self, map, move_limit, population_size, mutation_chance):
    self.map = map
    self.move_limit = move_limit
    self.population_size = population_size
    self.mutation_chance = mutation_chance

    # Initialize population with population_size chromosomes containg move_limit
    # moves
    self.population = [[random.randint(0, 4) for x in range(self.move_limit)] for y in
        range(self.population_size)]

  # Determine fitness of a chromosome
  def fitness(self, chromosome):
    for move in chromosome:
      if move == 0: pass # Don't move anywhere
      # Move up, down, left, right based on number in chromosome
      elif move == 1: self.map.up()
      elif move == 2: self.map.down()
      elif move == 3: self.map.left()
      elif move == 4: self.map.right()

    # Score is Manhattan distance since we're using a Cartesian coordinate
    # system
    score = abs(self.map.exit[0] - self.map.pos[0]) + abs(self.map.exit[1] -
        self.map.pos[1])

    # Move Mario back to beginning to evaluate new chromosomes
    self.map.reset()

    return score

  # Simple function that returns fittest score from a population
  # Get fitness for every chromosome in population and return list containing
  # just the scores, sort it numerically, and return first (lowest) score
  def fittest_score(self, population):
    fitness = list(map(self.fitness, population))
    fitness.sort()
    return fitness[0]

  # Replace random move in chromosome with another move based on mutation_chance
  def mutate(self, chromosome):
    if self.mutation_chance > random.random():
      chromosome[random.randint(0, len(chromosome) - 1)] = random.randint(0, 4)

    return chromosome

  # Produce offspring for the population
  def crossover(self, population):
    new_population = []

    for i in range(self.population_size - 1):
      # Select two random chromosomes from population
      mom = self.population[random.randint(0, len(population) + 1)]
      dad = self.population[random.randint(0, len(population) + 1)]

      # The point at which the moves will be combined
      crossover_point = random.randint(0, self.move_limit - 1)

      # Produce offspring with chance of mutation
      offspring = mom[0:crossover_point] + dad[crossover_point:len(dad)]
      offspring = self.mutate(offspring)

      new_population.append(offspring)

    return new_population

  # Find best moves from the population
  # Start off with absurdly large fitness score
  def get_optimal_moves(self, population):
     return self.helper(population, 999)

  # Helper function for finding optimal moves
  # Iterative solution used since Python does not use tail call optimization
  def helper(self, population, most_fit_score):
    # Change this to find a solution within N tiles from exit
    while most_fit_score > 0:
      fitness = list(map(lambda x: (self.fitness(x), x), population))

      # Survival of the fittest, get most fit half from population
      sorted_fitness = sorted(fitness, key=lambda tup: tup[0])
      half_most_fit = sorted_fitness[0:int(len(sorted_fitness) / 2)]

      # Get most fit score from the half and keep trying
      new_population = self.crossover(list(map(lambda x:(x[1]), half_most_fit)))
      population = new_population
      most_fit_score = self.fittest_score(new_population)
    return population

def main():
  # The maze Mario will be navigating
  lst = [['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#'],
         ['#',' ','#',' ',' ',' ',' ',' ','#','#','#',' ','G',' ','#'],
         ['M',' ',' ',' ',' ','G',' ',' ','#','#','#',' ',' ',' ','#'],
         ['#',' ',' ',' ','#','#','#',' ',' ','#',' ',' ',' ',' ','#'],
         ['#',' ',' ',' ','#','#','#',' ',' ',' ',' ',' ','#',' ','#'],
         ['#','#',' ',' ','#','#','#',' ',' ',' ',' ',' ','#',' ','#'],
         ['#',' ',' ',' ',' ','#',' ',' ',' ',' ','#','#','#',' ','#'],
         ['#','G','#','#',' ',' ',' ','#',' ',' ',' ',' ',' ',' ','E'],
         ['#',' ','#','#',' ',' ',' ','#',' ',' ','G',' ',' ',' ','#'],
         ['#','#','#','#','#','#','#','#','#','#','#','#','#','#','#']]
  maze = Map(lst, (0,2), (14,7))
  print('\nMario\'s position: (0, 2)\n' + str(maze))

  # Population size should be kept within a good range (both too low and too
  # large will result in slow execution
  # Maximum moves for chromosome is twenty-five (twenty-one required to solve
  # maze in best case)
  # Mutation rate should be kept low to reach goal faster
  genetic = Genetic(maze, 1000, 25, 0.01)

  print('\nFinding solution to the maze...')

  # Get moves required for optimal traversal and score that results
  optimal_moves = genetic.get_optimal_moves(genetic.population)
  final_fitness = list(map(lambda x: (genetic.fitness(x), x), optimal_moves))
  sorted_final_fitness = sorted(final_fitness, key=lambda tup: tup[0])
  print('\nScore: ' + str(sorted_final_fitness[0][0]))

  # Actually move Mario
  for move in sorted_final_fitness[0][1]:
    if move == 0: pass
    elif move == 1: maze.up()
    elif move == 2: maze.down()
    elif move == 3: maze.left()
    elif move == 4: maze.right()

  # Print solved maze
  print('\nMario\'s position: ' + str(maze.pos) + '\n' + str(maze))

if __name__ == "__main__":
  main()
