# Secure Communication using Quantum Key Distribution (QKD)
# Alice and Bob share a secret key using Quantum Key Distribution (QKD)
# With eavesdropping, but no noise

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import random

# Step 1: Generate random bits and bases
n_bits = 100  # Number of qubits
alice_bits = [random.randint(0, 1) for _ in range(n_bits)]
alice_bases = [random.choice(['X', 'Z']) for _ in range(n_bits)]

# Step 2: Encode qubits
circuits = []
for bit, basis in zip(alice_bits, alice_bases):
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)  # Apply X gate for |1>
    if basis == 'X':
        qc.h(0)  # Apply H for X-basis
    circuits.append(qc)

# Step 3: Eve's interception
eve_bases = [random.choice(['X', 'Z']) for _ in range(n_bits)]
eve_results = []

simulator = AerSimulator()  # Initialize the simulator once

for circuit, basis in zip(circuits, eve_bases):
    if basis == 'X':
        circuit.h(0)  # Measure in X-basis
    circuit.measure(0, 0)
    compiled_circuit = transpile(circuit, simulator)
    result = simulator.run(compiled_circuit).result()
    counts = result.get_counts()
    eve_results.append(int(max(counts, key=counts.get)))
    circuit.data.pop()  # Remove the measurement operation
    if eve_results[-1] == 1:
        circuit.x(0)  # Apply X gate if Eve measured |1>
    if basis == 'X':
        circuit.h(0)  # Apply H gate if Eve measured in X-basis

# Step 4: Bob's random bases and measurements
bob_bases = [random.choice(['X', 'Z']) for _ in range(n_bits)]
bob_results = []

for circuit, basis in zip(circuits, bob_bases):
    if basis == 'X':
        circuit.h(0)  # Measure in X-basis
    circuit.measure(0, 0)
    compiled_circuit = transpile(circuit, simulator)
    result = simulator.run(compiled_circuit).result()
    counts = result.get_counts()
    bob_results.append(int(max(counts, key=counts.get)))

# Step 5: Basis reconciliation
matched_indices = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
alice_key = [alice_bits[i] for i in matched_indices]
bob_key = [bob_results[i] for i in matched_indices]

print("Alice's Key:", alice_key)
print("Bob's Key  :", bob_key)

# Step 6: Compare keys
if alice_key == bob_key:
    print("Keys match! Secure communication established.")


# Calculate key rate
key_rate = len(alice_key) / n_bits
print(f"Key Rate: {key_rate:.2f}")

# Check for eavesdropping
discrepancies = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
# Check for eavesdropping if Alice and Bob's keys do not match in more then 11% of the bits
if discrepancies > 0.11 * len(bob_key):
    print(f"Discrepancies detected: {discrepancies}")
    print("Potential eavesdropping detected!")
elif discrepancies > 0:
    print(f"Discrepancies detected: {discrepancies}")
    print("Possibly noise. Communication is secure.")
else:
    print("No discrepancies detected. Communication is secure.")