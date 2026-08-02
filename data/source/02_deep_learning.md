# Deep Learning and Neural Networks

## Backpropagation and Stochastic Gradient Descent

Deep learning models optimize parameters using backpropagation and stochastic gradient descent (SGD). The chain rule of calculus computes gradients of the loss function $L$ with respect to model weights $W$:

$$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial z^{(l)}} \cdot \frac{\partial z^{(l)}}{\partial W^{(l)}}$$

Activation functions such as ReLU, GELU, and Sigmoid introduce non-linearity, enabling deep architectures to approximate complex continuous functions.

## Convolutional and Transformer Architectures

Convolutional Neural Networks (CNNs) utilize spatial feature extraction filters for computer vision tasks, while Transformer models employ multi-head self-attention mechanisms to process sequential and relational tokens in natural language processing.
