# Quantum Computing Fundamentals

## Superposition and Entanglement in Qubits

Quantum computing leverages the principles of quantum mechanics to process information in ways that classical computers cannot. Unlike classical bits, which represent either a 0 or a 1, a quantum bit (qubit) can exist in a superposition of both states simultaneously.

$$\vert\psi\rangle = \alpha\vert 0\rangle + \beta\vert 1\rangle$$

where $\alpha$ and $\beta$ are complex probability amplitudes satisfying $|\alpha|^2 + |\beta|^2 = 1$. When two qubits become entangled, the state of one qubit instantaneously correlates with the state of another, regardless of distance.

## Quantum Gates and Circuit Architecture

Quantum gates manipulate qubit states through unitary transformations. Common single-qubit gates include the Pauli-X, Pauli-Y, Pauli-Z, and Hadamard (H) gates. The Hadamard gate creates superposition from standard basis states. Multiqubit operations, such as the Controlled-NOT (CNOT) gate, generate entanglement across quantum registers.
