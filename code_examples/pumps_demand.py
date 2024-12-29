from dimod import BinaryQuadraticModel
from dimod import make_quadratic
from dwave.samplers import SimulatedAnnealingSampler
import numpy as np

bqm = BinaryQuadraticModel("BINARY")  # Specify dtype to handle larger numbers

pumps = [0, 1, 2, 3]  # Pump IDs
costs = [
    [136, 227],
    [156, 165],
    [148, 136],
    [152, 216]
]  # Costs to pump with different pumps at different times
flow = [2, 7, 3, 8]  # Flows for 4 pumps
demand = 20  # The demand for the pumps that need to be satisfied (equality)
time = [0, 1]  # AM and PM separation

x = [[f"P{p}_AM", f"P{p}_PM"] for p in pumps]  # Variable names for each pump timeslot

for p in pumps:
    for t in time:
        bqm.add_variable(x[p][t], costs[p][t])  # Create a variable with variable name at x[p][t] with bias equal to its cost

# Each pump is run at least once and no more than 'len(time)' times
for p in pumps:
    c1 = [(x[p][t], 1) for t in time]  # Initialize constraint with variable name and bias for it in the constraint inequality
    bqm.add_linear_inequality_constraint(
        c1,  # Put the constraints with their biases, this is used to calculate weighted sum
        lb=1,  # Each pump is occupied at least once a day
        ub=len(time),  # Each pump can't be occupied for more than the whole day
        lagrange_multiplier=5,  # Penalty factor
        label="c1_pump_" + str(p)
    )

# At most 'len(pumps)' pumps at 1 time
for t in time:
    c2 = [(x[p][t], 1) for p in pumps]
    bqm.add_linear_inequality_constraint(
        c2,
        constant=-len(pumps),
        lagrange_multiplier=1,
        label="c1_time_" + str(t)
    )

# Satisfy demand
c3 = [(x[p][t], flow[p]) for p in pumps for t in time]
bqm.add_linear_equality_constraint(
    c3,
    constant=-demand,
    lagrange_multiplier=28
)

sampler = SimulatedAnnealingSampler()
sampleset = sampler.sample(bqm, num_reads=1000)

sample = sampleset.first.sample

total_cost = 0
total_flow = 0

print("\n\tAM\tPM")
for p in pumps:
    printout = 'P' + str(p)
    for t in time:
        sample_val = int(sample[x[p][t]])
        flow_val = flow[p]
        cost_val = costs[p][t]  # Debugging mess

        printout += '\t' + str(sample_val)
        total_flow += sample_val * flow_val
        total_cost += sample_val * cost_val
    print(printout)

print("Total flow:", total_flow)
print("Total cost:", total_cost)
