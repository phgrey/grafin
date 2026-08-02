---
id: 02_deep_learning.md-chunk-1
source_file: 02_deep_learning.md
section_title: Backpropagation and Stochastic Gradient Descent
primary_stem_domain: Technology
discipline: Artificial Intelligence & Machine Learning
secondary_disciplines:
- Computer Science
confidence_score: 0.9
classification_status: classified
classification_reasoning: Detected AI/ML algorithms and neural network vocabulary.
human_verified: false
---

## Backpropagation and Stochastic Gradient Descent

Deep learning models optimize parameters using backpropagation and stochastic gradient descent (SGD). The chain rule of calculus computes gradients of the loss function $L$ with respect to model weights $W$:

$$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial z^{(l)}} \cdot \frac{\partial z^{(l)}}{\partial W^{(l)}}$$

Activation functions such as ReLU, GELU, and Sigmoid introduce non-linearity, enabling deep architectures to approximate complex continuous functions.
