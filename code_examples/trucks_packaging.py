from dimod import ConstrainedQuadraticModel, Binary, quicksum, cqm_to_bqm
from dimod import SimulatedAnnealingSampler
import random

# Number of packages
num_packages = 300

# Randomly generate data
priority = [random.choice([1, 2, 3]) for _ in range(num_packages)]
days_since_order = [random.choice([0, 1, 2, 3]) for _ in range(num_packages)]
cost = [random.randint(1, 100) for _ in range(num_packages)]

# Constraints
max_weight = 3000
max_parcels = 100

# Priorities for the objective functions
obj_weight_priority = 1
obj_weight_days = 1

# Create a constrained quadratic model
cqm = ConstrainedQuadraticModel()

# Create binary variables for each package
bin_variables = [Binary(f"x_{i}") for i in range(num_packages)]

# Define the objective function
objective_weight = -obj_weight_priority * quicksum(priority[i] * bin_variables[i] for i in range(num_packages))
objective_days = -obj_weight_days * quicksum(days_since_order[i] * bin_variables[i] for i in range(num_packages))

cqm.set_objective(objective_weight + objective_days)

# Add constraints
cqm.add_constraint(
    quicksum(cost[i] * bin_variables[i] for i in range(num_packages)) <= max_weight,
    label="max_capacity"
)
cqm.add_constraint(
    quicksum(bin_variables[i] for i in range(num_packages)) == max_parcels,
    label="max_parcels"
)

# Convert CQM to BQM
bqm, invert = cqm_to_bqm(cqm)

# Solve using Simulated Annealing
sampler = SimulatedAnnealingSampler()
sampleset = sampler.sample(bqm, num_reads=3)

# Extract the best sample
best_sample = sampleset.first.sample
energy = sampleset.first.energy

# Display results
print("Best sample:", best_sample)
print("Energy:", energy)
print(sampleset)