# Secure Communication using Quantum Key Distribution (QKD)
# Alice and Bob share a secret key using Quantum Key Distribution (QKD)
# No eavesdropping, but with noise

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

# Step 3: Introduce noise
noise_probability = 0.06  # Probability of a bit flip
for circuit in circuits:
    if random.random() < noise_probability:
        circuit.x(0)  # Apply X gate to flip the bit

# Step 4: Bob's random bases and measurements
bob_bases = [random.choice(['X', 'Z']) for _ in range(n_bits)]
bob_results = []

simulator = AerSimulator()  # Initialize the simulator once

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
else:
    print("Keys do not match! Communication compromised.")



# Check for eavesdropping
discrepancies = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
# Check for eavesdropping if Alice and Bob's keys do not match in more than 11% of the bits
if discrepancies > 0.11 * len(bob_key):
    print(f"Discrepancies detected: {discrepancies}")
    print("Potential eavesdropping detected!")
elif discrepancies > 0:
    print(f"Discrepancies detected: {discrepancies}")
    print("Possibly noise. Communication is secure.")
    print("Use error correction codes to correct the errors.")


    # Step 6: Key reconciliation using parity check
    def parity_check(bits):
        return sum(bits) % 2


    # Split keys into blocks and compare parities
    block_size = 10
    for i in range(0, len(alice_key), block_size):
        alice_block = alice_key[i:i + block_size]
        bob_block = bob_key[i:i + block_size]
        if parity_check(alice_block) != parity_check(bob_block):
            # If parities do not match, correct the first bit in the block
            for j in range(len(bob_block)):
                if alice_block[j] != bob_block[j]:
                    bob_key[i + j] = alice_block[j]
                    break
    print("Used parity check to correct errors.")

    # Step 7: Compare keys after reconciliation
    if alice_key == bob_key:
        print("Keys match after reconciliation! Secure communication established.")
    else:
        print("Keys do not match after reconciliation! Communication compromised.")
    print("Alice's Key:", alice_key)
    print("Bob's Key  :", bob_key)
else:
    print("No discrepancies detected. Communication is secure.")


# Calculate key rate
key_rate = len(alice_key) / n_bits
print(f"Key Rate: {key_rate:.2f}")
