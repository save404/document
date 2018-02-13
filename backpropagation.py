#-*- coding: utf-8 -*-
import random
import math

class NeutralNetwork:
	"""docstring for NeutralNetwork"""
	LEARNING_RATE = 0.5

	def __init__(self, num_inputs, num_hidden, num_outputs, hidden_layer_weights = None, hidden_layer_bias = None, output_layer_weights = None, output_layer_bias = None):
		self.num_inputs = num_inputs

		self.hidden_layer = NeuronLayer(num_hidden, hidden_layer_bias)
		self.output_layer = NeuronLayer(num_outputs, output_layer_bias)

		self.init_weights_from_inputs_to_hidden_layer_neurons(hidden_layer_weights)
		self.init_weights_from_hidden_layer_neurons_to_output_layer_neurons(output_layer_weights)

	def init_weights_from_inputs_to_hidden_layer_neurons(self, hidden_layer_weights):
		weight_num = 0
		for h in range(len(self.hidden_layer.neurons)):
			for i in range(self.num_inputs):
				if not hidden_layer_weights:
					self.hidden_layer.neurons[h].weights.append(random.random())
				else:
					self.hidden_layer.neurons[h].weights.append(hidden_layer_weights[weight_num])
				weight_num += 1

	def init_weights_from_hidden_layer_neurons_to_output_layer_neurons(self, output_layer_weights):
		weight_num = 0
		for o in range(len(self.output_layer.neurons)):
			for h in range(len(self.hidden_layer.neurons)):
				if not output_layer_weights:
					self.output_layer.neurons[o].weights.append(random.random())
				else:
					self.output_layer.neurons[o].weights.append(output_layer_weights[weight_num])
				weight_num += 1

	def inspect(self):
		print('------')
		print('* Inputs: {}'.format(self.num_inputs))
		print('------')
		print('Hidden Layer')
		self.hidden_layer.inspect()
		print('------')
		print('* Output Layer')
		self.output_layer.inspect()
		print('------')

	def train(self, training_inputs, training_outputs):
		self.feed_forward(training_inputs)

		pd_errors_wrt_output_neuron_total_net_input = [0] * len(self.output_layer.neurons)
		for o in range(len(self.output_layer.neurons)):
			pd_errors_wrt_output_neuron_total_net_input[o] = self.output_layer.neurons[o].calculate_pd_error_wrt_total_net_input(training_outputs[o])

		pd_errors_wrt_hidden_neuron_total_net_input = [0] * len(self.hidden_layer.neurons)
		for h in range(len(self.hidden_layer.neurons)):
			d_error_wrt_hidden_neuron_output = 0
			for o in range(len(self.output_layer.neurons)):
				d_error_wrt_hidden_neuron_output += pd_errors_wrt_hidden_neuron_total_net_input[o] * self.output_layer.neurons[o].weights[h]
			pd_errors_wrt_hidden_neuron_total_net_input[h] = d_error_wrt_hidden_neuron_output * self.hidden_layer.neurons[h].calculate_pd_total_net_input_wrt_input()

		for o in range(len(self.output_layer.neurons)):
			for w_ho in range(len(self.output_layer.neurons[o].weights)):
				pd_error_wrt_weight = pd_errors_wrt_output_neuron_total_net_input[o] * self.output_layer.neurons[o].calculate_pd_total_net_input_wrt_weight(w_ho)
				self.output_layer.neurons[o].weights[w_ho] -= self.LEARNING_RATE * pd_error_wrt_weight

		for h in range(len(self.hidden_layer.neurons)):
			for w_ih in range(len(self.hidden_layer.neurons[h].weights)):
				pd_error_wrt_weight = pd_errors_wrt_hidden_neuron_total_net_input[h] * self.hidden_layer.neurons[h].calculate_pd_total_net_input_wrt_weight(w_ih)
				self.hidden_layer.neurons[h].weights[w_ih] -= self.LEARNING_RATE * pd_error_wrt_weight

	def feed_forward(self, inputs):
		hidden_layer_outputs = self.hidden_layer.feed_forward(inputs)
		return self.output_layer.feed_forward(hidden_layer_outputs)

	def calculate_total_error(self, training_sets):
		total_error = 0
		for t in range(len(training_sets)):
			training_inputs, training_outputs = training_sets[t]
			self.feed_forward(training_inputs)
			for o in range(len(training_outputs)):
				total_error += self.output_layer.neurons[o].calculate_error(training_outputs[o])
		#print(self.output_layer.neurons[0].weights[0], self.output_layer.bias)
		return total_error


class NeuronLayer:
	"""docstring for NeuronLayer"""
	def __init__(self, num_neurons, bias):
		# 同截距
		self.bias = bias if bias else random.random()
		self.neurons = []
		for i in range(num_neurons):
			self.neurons.append(Neuron(self.bias))

	def inspect(self):
		print('Neurons: ', len(self.neurons))
		for n in range(len(self.neurons)):
			print(' Neuron', n)
			for w in range(len(self.neurons[n].weights)):
				print('  Weight: ', self.neurons[n].weights[w])
			print('  Bias: ', self.bias)

	def feed_forward(self, inouts):
		outputs = []
		for neuron in self.neurons:
			outputs.append(neuron.calculate_output(inouts))
		return outputs

	def get_outputs(self):
		outputs = []
		for neuron in self.neurons:
			outputs.append(neuron.output)
		return outputs
		
class Neuron:
	"""docstring for Neuron"""
	def __init__(self, bias):
		self.bias = bias
		self.weights = []

	def calculate_output(self, inputs):
		self.inputs = inputs
		self.output = self.squash(self.calculate_total_net_input())
		return self.output

	def calculate_total_net_input(self):
		total = 0
		for i in range(len(self.inputs)):
			total += self.inputs[i] * self.weights[i]
		total += self.bias
		return total

	# 激活函数sigmoid
	def squash(self, total_net_input):
		return 1 / (1 + math.exp(-total_net_input))

	def calculate_pd_error_wrt_total_net_input(self, target_output):
		return self.calculate_pd_error_wrt_output(target_output) * self.calculate_pd_total_net_input_wrt_input()

	def calculate_pd_error_wrt_output(self, target_output):
		return -(target_output - self.output)

	def calculate_pd_total_net_input_wrt_input(self):
		return self.output * (1 - self.output)

	def calculate_error(self, target_output):
		return 0.5 * (target_output - self.output) ** 2

	def calculate_pd_total_net_input_wrt_weight(self, index):
		return self.inputs[index]


if __name__ == '__main__':
	nn = NeutralNetwork(2, 2, 2, hidden_layer_weights=[0.15, 0.2, 0.25, 0.3], hidden_layer_bias=0.35, output_layer_weights=[0.4, 0.45, 0.5, 0.55], output_layer_bias=0.6)
	for i in range(10000):
		nn.train([0.05, 0.1], [0.01, 0.99])
		print(i, round(nn.calculate_total_error([[[0.05, 0.1], [0.01, 0.09]]]), 9))

	ans = nn.output_layer.get_outputs()
	print(ans[0], ans[1])


		