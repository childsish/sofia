#include <boost/python.hpp>
#include <dlib/svm.h>
#include <string>
#include <iostream>

using namespace boost::python;
using namespace dlib;

typedef double scalar_type;
typedef matrix<scalar_type, 0, 1> sample_type;
typedef std::vector<sample_type> sample_vector;
typedef std::vector<scalar_type> label_vector;

//! Member function wrappers for matrix.
void set_item(sample_type& sample, int i, const double& val) { sample(i) = val; }
const double& (sample_type::*get_item)(long) const = &sample_type::operator();
void (sample_type::*set_size)(long) = &sample_type::set_size;

//! Register a vector with helpers

void IndexError() { PyErr_SetString(PyExc_IndexError, "Index out of range"); }

template<typename T>
struct vector_helper
{
	typedef typename T::value_type V;
	static V& get(T& x, int i)
	{
		if( i < 0 ) i += x.size();
		if( i >= 0 && i < (int) x.size() ) return x[i];
		else IndexError();
	}
	static void set(T& x, int i, V& v)
	{
		if( i < 0 ) i += x.size();
		if( i >= 0 && i < (int) x.size() ) x[i] = v;
		else IndexError();
	}
	static void del(T& x, int i)
	{
		if( i < 0 ) i += x.size();
		if( i >= 0 && i < (int) x.size() ) x.erase(x.begin() + i);
		else IndexError();
	}
};

template<typename T>
void register_vector(const char* type) {
	typedef std::vector<T> vector_type;
	
	std::string prefix("vector_");
	
	class_<vector_type>(prefix.append(type).c_str())
	 .def(init<long>())
	 //.def("__init__", &vector_helper<vector_type>::init)
	 .def("__len__", &vector_type::size)
	 .def("__iter__", iterator<std::vector<T> >())
	 .def("clear", &vector_type::clear)
	 .def("append", &vector_type::push_back,
	      with_custodian_and_ward<1,2>()) // to let container keep value
	 .def("__getitem__", &vector_helper<vector_type>::get,
	      return_value_policy<copy_non_const_reference>())
	 .def("__setitem__", &vector_helper<vector_type>::set,
	      with_custodian_and_ward<1,3>()) // to let container keep value
	 .def("__delitem__", &vector_helper<vector_type>::del)
	;
}

//! Serialize / deserialize helpers

template<typename T>
void serialize_helper(const T& item, std::string name) {
	std::ofstream out(name.c_str(), std::ios::binary);
	serialize(item, out);
	out.close();
}

template<typename T>
void deserialize_helper(T& item, std::string name) {
	std::ifstream in(name.c_str(), std::ios::binary);
	deserialize(item, in);
	in.close();
}

//! Register common properties of a kernel. Extra initialisation needs to occur for specialised kernels
template<typename T>
class_<T>* register_kernel(const char* name) {
	class_<T>* cls = new class_<T>(name);
	cls->def("__call__", &T::operator())
	 .def("__eq__", &T::operator==);
	def("serialize", serialize_helper<T>);
	def("deserialize", deserialize_helper<T>);
	return cls;
}

//! Register a decision function

template<typename T>
class_<T>* register_function(const char* name) {
	class_<T>* cls = new class_<T>(name);
	cls->def("__call__", &T::operator());
	def("serialize", serialize_helper<T>);
	def("deserialize", deserialize_helper<T>);
	return cls;
}

//! Register a trainer and templated functions

template<typename K>
class_<rvm_trainer<K> >* register_trainer(const char* suffix) {
	typedef rvm_trainer<K> trainer_type;
	std::string buf = "rvm_trainer_";
	class_<trainer_type>* cls = new class_<trainer_type>(buf.append(suffix).c_str());
	cls->def("set_epsilon", &trainer_type::set_epsilon)
	 .def("get_epsilon", &trainer_type::get_epsilon)
	 .def("set_kernel", &trainer_type::set_kernel)
	 .def("get_kernel", &trainer_type::get_kernel, return_internal_reference<>());
	// .def("train",  &trainer_type::train<sample_vector, label_vector>);
	 
	def("train_probabilistic_decision_function",
		train_probabilistic_decision_function<trainer_type, sample_vector, label_vector>);
	
	buf = "decision_function_";
	typedef decision_function<K> dfn;
	register_function<dfn>(buf.append(suffix).c_str());
	
	buf = "probabilistic_decision_function_";
	typedef probabilistic_decision_function<K> pdfn;
	register_function<pdfn>(buf.append(suffix).c_str());
	
	buf = "probabilistic_function_";
	typedef probabilistic_function<dfn> pfn;
	register_function<pfn>(buf.append(suffix).c_str());
	
	buf = "normalized_decision_function_";
	typedef normalized_function<dfn> ndfn;
	class_<ndfn>* fn1 = register_function<ndfn>(buf.append(suffix).c_str());
	fn1->def_readwrite("normalizer", &ndfn::normalizer)
	 .def_readwrite("function", &ndfn::function);
	
	buf = "normalized_probabilistic_function_";
	typedef normalized_function<pfn> npdfn;
	class_<npdfn>* fn2 = register_function<npdfn>(buf.append(suffix).c_str());
	fn2->def_readwrite("normalizer", &npdfn::normalizer)
	 .def_readwrite("function", &npdfn::function);
	
	return cls;
}

template<typename K>
class_<rvm_regression_trainer<K> >* register_regression_trainer(const char* suffix) {
	typedef rvm_regression_trainer<K> trainer_type;
	std::string buf = "rvm_regression_trainer_";
	class_<trainer_type>* cls = new class_<trainer_type>(buf.append(suffix).c_str());
	cls->def("set_epsilon", &trainer_type::set_epsilon)
	 .def("get_epsilon", &trainer_type::get_epsilon)
	 .def("set_kernel", &trainer_type::set_kernel)
	 .def("get_kernel", &trainer_type::get_kernel, return_internal_reference<>());
	// .def("train",  &trainer_type::train<sample_vector, label_vector>);
	
	return cls;
}

//! The main module function

BOOST_PYTHON_MODULE(rvm_binding) {
	class_<sample_type>("sample")
	 .def(init<long>())
	 .def("__len__", &sample_type::size)
	 .def("__setitem__", set_item, with_custodian_and_ward<1, 3>())
	 .def("__getitem__", get_item, return_value_policy<copy_const_reference>())
	 .def("set_size", set_size);
	 //.def("__call__", &sample_type::operator());
	
	class_<vector_normalizer<sample_type> >("vector_normalizer")
	 .def("train", &vector_normalizer<sample_type>::train<std::vector<sample_type> >)
	 .def("__call__", &vector_normalizer<sample_type>::operator(),
	      return_value_policy<copy_const_reference>());
	
	register_vector<sample_type>("sample");
	register_vector<double>("double");
	
	def("compute_mean_squared_distance", compute_mean_squared_distance<sample_vector>);
	
	typedef radial_basis_kernel<sample_type> krbf;
	class_<krbf>* k1 = register_kernel<krbf>("radial_basis_kernel");
	k1->def(init<const sample_type::type>())
	 .def(init<const krbf&>())
	 .def_readonly("gamma", &krbf::gamma);
	class_<rvm_trainer<krbf> >* t1 = register_trainer<krbf>("rbf");
	t1->def("train",  &rvm_trainer<krbf>::train<sample_vector, label_vector>);
	class_<rvm_regression_trainer<krbf> >* r1 = register_regression_trainer<krbf>("rbf");
	r1->def("train",  &rvm_regression_trainer<krbf>::train<sample_vector, label_vector>);
	
	typedef polynomial_kernel<sample_type> kply;
	class_<kply>* k2 = register_kernel<kply>("polynomial_kernel");
	k2->def(init<const sample_type::type, const sample_type::type, const sample_type::type>())
	 .def(init<const kply&>())
	 .def_readonly("gamma", &kply::gamma)
	 .def_readonly("coef", &kply::coef)
	 .def_readonly("degree", &kply::degree);
	class_<rvm_trainer<kply> >* t2 = register_trainer<kply>("ply");
	t2->def("train",  &rvm_trainer<kply>::train<sample_vector, label_vector>);
	class_<rvm_regression_trainer<kply> >* r2 = register_regression_trainer<kply>("ply");
	r2->def("train",  &rvm_regression_trainer<kply>::train<sample_vector, label_vector>);
	
	typedef sigmoid_kernel<sample_type> ksig;
	class_<ksig>* k3 = register_kernel<ksig>("sigmoid_kernel");
	k3->def(init<const sample_type::type, const sample_type::type>())
	 .def(init<const ksig&>())
	 .def_readonly("gamma", &ksig::gamma)
	 .def_readonly("coef", &ksig::coef);
	class_<rvm_trainer<ksig> >* t3 = register_trainer<ksig>("sig");
	t3->def("train",  &rvm_trainer<ksig>::train<sample_vector, label_vector>);
	class_<rvm_regression_trainer<ksig> >* r3 = register_regression_trainer<ksig>("sig");
	r3->def("train",  &rvm_regression_trainer<ksig>::train<sample_vector, label_vector>);
	
	typedef linear_kernel<sample_type> klin;
	register_kernel<klin>("linear_kernel");
	class_<rvm_trainer<klin> >* t4 = register_trainer<klin>("lin");
	t4->def("train",  &rvm_trainer<klin>::train<sample_vector, label_vector>);
	class_<rvm_regression_trainer<klin> >* r4 = register_regression_trainer<klin>("lin");
	r4->def("train",  &rvm_regression_trainer<klin>::train<sample_vector, label_vector>);
}
