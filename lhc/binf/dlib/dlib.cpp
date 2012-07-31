BOOST_PYTHON_MODULE(dlib_binding) {
	object package = scope();
	package.attr("__path__") = "dlib_binding";
	
	export_util();
	export_io();
}
