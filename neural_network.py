import math
import numpy as np


class ActivationFunction:
	def __init__(self, func, dfunc):
		self.func = func
		self.dfunc = dfunc
		
sigmoid = ActivationFunction(
	lambda x : 1 / (1 + math.exp(-x)),
	lambda y : y * (1 - y)
)

tanh = ActivationFunction(
	lambda x : math.tanh(x),
	lambda y : 1 - (y * y)
)

class NeuralNetwork:
	def __init__(self, in_nodes, hid_nodes, out_nodes):
		if isinstance(in_nodes, NeuralNetwork):
			a = in_nodes                                                        
			self.input_nodes = a.input_nodes
			self.hidden_nodes = a.hidden_nodes
			self.output_nodes = a.output_nodes

			self.weights_ih = a.weights_ih
			self.weights_ho = a.weights_ho
			
			self.bias_h = a.bias_h
			self.bias_o = a.bias_o
		else:
			self.input_nodes = in_nodes
			self.hidden_nodes = hid_nodes
			self.output_nodes = out_nodes

			self.weights_ih = np.random.rand(self.input_nodes, self.hidden_nodes)
			self.weights_ho = np.random.rand(self.hidden_nodes, self.output_nodes)
			
			self.bias_h = np.random.rand(1, self.hidden_nodes)
			self.bias_o = np.random.rand(1, self.output_nodes)
			
		self.setLearningRate()
		self.setActivationFunction()
		self.func = np.vectorize(self.activation_function.func)
		self.dfunc = np.vectorize(self.activation_function.dfunc)
		
	def predict(self, inputs):

		# Generating the Hidden Outputs
		inputs = np.asarray([inputs])
		hidden = inputs.dot(self.weights_ih)
		hidden = hidden + self.bias_h
    
		# activation function!
		hidden = self.func(hidden)

		# Generating the output's output!
		output = hidden.dot(self.weights_ho)
		output = output + self.bias_o
		
		# activation function!
		output = self.func(output)

		# Sending back to the caller!
		return output.tolist()

	def setLearningRate(self, learning_rate = 0.1) :
		self.learning_rate = learning_rate


	def setActivationFunction(self, func = sigmoid) :
		self.activation_function = func

	def train(self, inputs, targets) :
		# Generating the Hidden Outputs
		inputs = np.asarray([inputs])
		hidden = inputs.dot(self.weights_ih)
		hidden = hidden + self.bias_h
		# activation function!
		hidden = self.func(hidden)

		# Generating the output's output!
		outputs = hidden.dot(self.weights_ho)
		outputs = outputs + self.bias_o
		outputs = self.func(outputs)

		# Calculate the error
		# ERROR = TARGETS - OUTPUTS
		targets = np.asarray([targets])
		output_errors = targets - outputs

    # let gradient = outputs * (1 - outputs)
		
		# Calculate gradient
		gradients = self.dfunc(outputs)
		gradients = gradients * output_errors
		gradients = gradients * self.learning_rate

		# Calculate deltas
		hidden_T = hidden.transpose()
		weight_ho_deltas = hidden_T.dot(gradients)

		# Adjust the weights by deltas
		self.weights_ho += weight_ho_deltas
		
		# Adjust the bias by its deltas (which is just the gradients)
		self.bias_o += gradients

		# Calculate the hidden layer errors
		who_t = self.weights_ho.transpose()
		hidden_errors = output_errors.dot(who_t)

		# Calculate hidden gradient
		hidden_gradient = self.dfunc(hidden)
		hidden_gradient *= hidden_errors
		hidden_gradient *= self.learning_rate

		# Calcuate input->hidden deltas
		inputs_T = inputs.transpose()
		weight_ih_deltas = inputs_T.dot(hidden_gradient)

		self.weights_ih += weight_ih_deltas
    
		# Adjust the bias by its deltas (which is just the gradients)
		self.bias_h += hidden_gradient

    # outputs.print()
    # targets.print()
    # error.print()


	# Adding function for neuro-evolution
	def copy(self) :
		return NeuralNetwork(self)

	# Accept an arbitrary function for mutation
	def mutate(self, func) :
		vect = np.vectorize(func)
		self.weights_ih = vect(self.weights_ih)
		self.weights_ho = vect(self.weights_ho)
		self.bias_h = vect(self.bias_h)
		self.bias_o = vect(self.bias_o)

