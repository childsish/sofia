import rvm_binding

class RadialBasisKernel(rvm_binding.radial_basis_kernel):
	pass

class PolynomialKernel(rvm_binding.polynomial_kernel):
	pass

class SigmoidKernel(rvm_binding.sigmoid_kernel):
	pass

class LinearKernel(rvm_binding.linear_kernel):
	pass

class Trainer(object):
	def __init__(self, kernel, epsilon=0.001):
		self.trainer = self.__getTrainer(kernel)
		self.trainer.set_epsilon(epsilon)
	
	def getEpsilon(self):
		return self.trainer.get_epsilon()
	
	def setEpsilon(self, epsilon):
		self.trainer.set_epsilon(epsilon)
	
	def getKernel(self):
		return self.trainer.get_kernel()
	
	def setKernel(self, kernel):
		tmp = self.trainer.get_epsilon()
		self.trainer = self.__getTrainer(kernel)
		self.trainer.set_epsilon(tmp)
	
	def train(self, samples, labels):
		res = DecisionFunction()
		res.fn = self.trainer.train(VectorSample(samples), VectorDouble(labels))
		return res
	
	def trainProbabilistic(self, samples, labels, folds=3):
		res = ProbabilisticFunction()
		res.fn = rvm_binding.train_probabilistic_decision_function(self.trainer,
		 VectorSample(samples), VectorDouble(labels), folds)
		return res
	
	def __getTrainer(self, kernel):
		if issubclass(type(kernel), rvm_binding.radial_basis_kernel):
			res = rvm_binding.rvm_trainer_rbf()
		elif issubclass(type(kernel), rvm_binding.polynomial_kernel):
			res = rvm_binding.rvm_trainer_ply()
		elif issubclass(type(kernel), rvm_binding.sigmoid_kernel):
			res = rvm_binding.rvm_trainer_sig()
		elif issubclass(type(kernel), rvm_binding.linear_kernel):
			res = rvm_binding.rvm_trainer_lin()
		else:
			raise TypeError('Unkown kernel type: %s'%(str(type(kernel))))
		res.set_kernel(kernel)
		return res

class RegressionTrainer(object):
	def __init__(self, kernel, epsilon=0.001):
		self.trainer = self.__getTrainer(kernel)
		self.trainer.set_epsilon(epsilon)
	
	def getEpsilon(self):
		return self.trainer.get_epsilon()
	
	def setEpsilon(self, epsilon):
		self.trainer.set_epsilon(epsilon)
	
	def getKernel(self):
		return self.trainer.get_kernel()
	
	def setKernel(self, kernel):
		tmp = self.trainer.get_epsilon()
		self.trainer = self.__getTrainer(kernel)
		self.trainer.set_epsilon(tmp)
	
	def train(self, samples, labels):
		res = DecisionFunction()
		res.fn = self.trainer.train(VectorSample(samples), VectorDouble(labels))
		return res
	
	def trainProbabilistic(samples, labels, folds=3):
		res = ProbabilisticFunction()
		res.fn = rvm_binding.train_probabilistic_decision_function(self.trainer,
		 VectorSample(samples), VectorDouble(labels), folds)
		return res
	
	def __getTrainer(self, kernel):
		if issubclass(type(kernel), rvm_binding.radial_basis_kernel):
			res = rvm_binding.rvm_regression_trainer_rbf()
		elif issubclass(type(kernel), rvm_binding.polynomial_kernel):
			res = rvm_binding.rvm_regression_trainer_ply()
		elif issubclass(type(kernel), rvm_binding.sigmoid_kernel):
			res = rvm_binding.rvm_regression_trainer_sig()
		elif issubclass(type(kernel), rvm_binding.linear_kernel):
			res = rvm_binding.rvm_regression_trainer_lin()
		else:
			raise TypeError('Unkown kernel type: %s'%str(type(kernel)))
		res.set_kernel(kernel)
		return res

class VectorNormalizer(object):
	def __init__(self):
		self.normalizer = rvm_binding.vector_normalizer()
	
	def __call__(self, sample):
		res = self.normalizer(Sample(sample))
		return [res[i] for i in xrange(len(res))]
	
	def train(self, samples):
		self.normalizer.train(VectorSample(samples))

class DecisionFunction(object):
	def __init__(self):
		self.fn = None
	
	def __call__(self, val):
		return self.fn(Sample(val))
	
	#TODO: Implement pickling later
	def serialize(self, fname):
		rvm_binding.serialize(self.fn, fname)
	
	#TODO: Implement pickling later
	@classmethod
	def deserialize(cls, fname):
		for rvm_cls in (rvm_binding.decision_function_rbf,
		 rvm_binding.decision_function_ply,
		 rvm_binding.decision_function_sig,
		 rvm_binding.decision_function_lin):
			try:
				fn = rvm_cls()
				rvm_binding.deserialize(fn, fname)
				res = DecisionFunction()
				res.fn = fn
				return res
			except RuntimeError:
				continue
		raise RuntimeError('Unable to deserialize file. Unknown function type.')

class ProbabilisticFunction(object):
	def __init__(self):
		self.fn = None
	
	def __call__(self, val):
		return self.fn(Sample(val))
	
	#TODO: Implement pickling later
	def serialize(self, fname):
		rvm_binding.serialize(self.ndf, fname)
	
	#TODO: Implement pickling later
	@classmethod
	def deserialize(cls, fname):
		for rvm_cls in (rvm_binding.probabilistic_function_rbf,
		 rvm_binding.probabilistic_function_ply,
		 rvm_binding.probabilistic_function_sig,
		 rvm_binding.probabilistic_function_lin):
			try:
				fn = rvm_cls()
				rvm_binding.deserialize(fn, fname)
				res = ProbabilisticFunction()
				res.fn = fn
				return res
			except RuntimeError:
				continue
		raise RuntimeError('Unable to deserialize file. Unknown function type.')

class NormalizedFunction(object):
	def __init__(self, function, normalizer=VectorNormalizer()):
		""" Expects a python function (eg. DecisionFunction) and a python normalizer
		 (eg.) VectorNormalizer. """
		self.fn = self.__getNormalizedFunction(function.fn)
		self.fn.normalizer = normalizer.normalizer
	
	def __call__(self, val):
		return self.fn(Sample(val))
	
	def getNormalizer(self):
		return self.fn.normalizer
	
	def setNormalizer(self, normalizer):
		self.fn.normalizer = normalizer
	
	def getFunction(self):
		return self.fn.function
	
	def setFunction(self, function):
		tmp = self.fn.normalizer
		self.fn = self.__getNormalizedFunction(function)
		self.fn.normalizer = tmp
	
	#TODO: Implement pickling later
	def serialize(self, fname):
		rvm_binding.serialize(self.fn, fname)
	
	#TODO: Implement pickling later
	@classmethod
	def deserialize(cls, fname):
		for rvm_cls in (rvm_binding.normalized_decision_function_rbf,
		 rvm_binding.normalized_decision_function_ply,
		 rvm_binding.normalized_decision_function_sig,
		 rvm_binding.normalized_decision_function_lin,
		 rvm_binding.normalized_probabilistic_function_rbf,
		 rvm_binding.normalized_probabilistic_function_ply,
		 rvm_binding.normalized_probabilistic_function_sig,
		 rvm_binding.normalized_probabilistic_function_lin):
			try:
				fn = rvm_cls()
				rvm_binding.deserialize(fn, fname)
				# Create a temporary DecisionFunction because the NormalizedFunction
				#  constructor expects a Python object
				tmp = DecisionFunction()
				tmp.fn = fn.function
				res = NormalizedFunction(tmp)
				res.fn.normalizer = fn.normalizer
				return res
			except RuntimeError:
				continue
		raise RuntimeError('Unable to deserialize file. Unknown function type.')
	
	def __getNormalizedFunction(self, function):
		if issubclass(type(function), rvm_binding.decision_function_rbf):
			res = rvm_binding.normalized_decision_function_rbf()
		elif issubclass(type(function), rvm_binding.decision_function_ply):
			res = rvm_binding.normalized_decision_function_ply()
		elif issubclass(type(function), rvm_binding.decision_function_sig):
			res = rvm_binding.normalized_decision_function_sig()
		elif issubclass(type(function), rvm_binding.decision_function_lin):
			res = rvm_binding.normalized_decision_function_lin()
		elif issubclass(type(function), rvm_binding.probabilistic_function_rbf):
			res = rvm_binding.normalized_probabilistic_function_rbf()
		elif issubclass(type(function), rvm_binding.probabilistic_function_ply):
			res = rvm_binding.normalized_probabilistic_function_ply()
		elif issubclass(type(function), rvm_binding.probabilistic_function_sig):
			res = rvm_binding.normalized_probabilistic_function_sig()
		elif issubclass(type(function), rvm_binding.probabilistic_function_lin):
			res = rvm_binding.normalized_probabilistic_function_lin()
		else:
			raise TypeError('Unknown function type: %s'%str(type(function)))
		res.function = function
		return res

def VectorSample(x):
	res = rvm_binding.vector_sample(len(x))
	for i in xrange(len(x)):
		res[i] = Sample(x[i])
	return res

def VectorDouble(x):
	res = rvm_binding.vector_double()
	for i in xrange(len(x)):
		res.append(x[i])
	return res

def Sample(x):
	res = rvm_binding.sample(len(x))
	for i in xrange(len(x)):
		res[i] = x[i]
	return res


from lhc import math


def sinc(x):
	if x == 0:
		return 1
	return math.sin(x) / x

def test_rvc():
	samples = []
	labels = []
	
	for r in xrange(-20, 20):
		for c in xrange(-20, 20):
			s = (float(r), float(c))
			samples.append(s)
			
			if (math.sqrt(r*r + c*c) <= 10):
				labels.append(1.)
			else:
				labels.append(-1.)
	
	normalizer = VectorNormalizer()
	normalizer.train(samples)
	for i in xrange(len(samples)):
		samples[i] = normalizer(samples[i])
	
	trainer = Trainer(RadialBasisKernel(0.08), 0.01)
	
	fn = NormalizedFunction(trainer.train(samples, labels), normalizer)
	
	for x, y in ((3.123, 2), (3.123, 9.3545)):
		print "This sample should be >= 0 and it is classified as a %.3f"%fn((x, y))

	for x, y in ((13.123, 9.3545), (13.123, 0)):
		print "This sample should be < 0 and it is classified as a %.3f"%fn((x, y))
	
	fn.serialize("saved_function.dat")
	fn = NormalizedFunction.deserialize("saved_function.dat")
	print fn((x, y))
	
	pfn = NormalizedFunction(trainer.trainProbabilistic(samples, labels), normalizer)
	
	for x, y in ((3.123, 2), (3.123, 9.3545)):
		print "This +1 example should have high probability. Its probability is: %.3f"%pfn((x, y))
	
	for x, y in ((13.123, 9.3545), (13.123, 0)):
		print "This -1 example should have low probability. Its probability is: %.3f"%pfn((x, y))
	
	pfn.serialize("saved_function.dat")
	pfn = NormalizedFunction.deserialize("saved_function.dat")
	print pfn(s)

def test_rvr():
	samples = []
	labels = []
	
	for x in xrange(-10, 4):
		samples.append((x,))
		labels.append(sinc(x))
	
	gamma = 2.0 / rvm_binding.compute_mean_squared_distance(VectorSample(samples))
	trainer = RegressionTrainer(RadialBasisKernel(gamma), 0.00001)
	print 'using gamma of', gamma
	
	fn = trainer.train(samples, labels)
	
	m = (2.5,); print sinc(m[0]), fn(m)
	m = (0.1,); print sinc(m[0]), fn(m)
	m = (-4.,); print sinc(m[0]), fn(m)
	m = (5.0,); print sinc(m[0]), fn(m)
	
	fn.serialize("saved_function.dat")
	fn = DecisionFunction.deserialize("saved_function.dat")
	print fn(m)

def main():
	test_rvc()
	test_rvr()

if __name__ == '__main__':
	import sys
	sys.exit(main())
