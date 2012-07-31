#include "digen.h"

int N_BASE = 4;
int N_DNUC = 16;
char BASES[] = {'a', 'c', 'g', 'u'};

char* generate(const int* frq)
{
	// Initialise the output array
	int seq_len = sum(frq, N_DNUC)+1;
	
	if (split(frq)) { return NULL; }
	
	// Calculate the imbalance
	int* imb = imbalance(frq);
	int* abs_imb = abs(imb, N_BASE);
	int sum_abs_imb = sum(abs_imb, N_BASE);
	if (sum_abs_imb > 2) {
		// No valid sequence can be generated with this frequency. Cleanup and return NULL
		delete [] abs_imb;
		abs_imb = NULL;
		delete [] imb;
		imb = NULL;
		
		return NULL;
	}
	
	// Choose the next node to visit
	std::stack<Node*> stk;
	int fr = 0;
	int to = 0;
	int con = consumer(imb);
	if (con != -1) {
		fr = con * N_BASE;
		to = fr + N_BASE;
	}
	else {
		fr = 0;
		to = N_DNUC;
	}
	
	// Insert the next nodes randomly onto the stack
	int* order = randomOrder(frq, fr, to);
	for (int i = 0; i < to-fr; ++i) {
		if (order[i] == -1) { continue; }
		int idx = fr + order[i];
		if (frq[idx] <= 0) { continue; }
		
		Node* node = new Node(idx, frq, BASES[(idx)/N_BASE], seq_len);
		stk.push(node);
	}
	delete [] order;
	order = NULL;
	
	delete [] abs_imb;
	abs_imb = NULL;
	delete [] imb;
	imb = NULL;
	
	// Explore the possibilities
	while (!stk.empty()) {
		// Adjust the frequencies and path
		Node* cur = stk.top();
		stk.pop();
		cur->frq[cur->i] -= 1;
		
		if (split(cur->frq)) {
			// Cleanup node if we split the graph
			delete cur;
			cur = NULL;
			continue;
		}
		
		cur->pth[strlen(cur->pth)] = BASES[cur->i%N_BASE];
		if (strlen(cur->pth) == seq_len) {
			// We've found a possibility
			char* res = new char[seq_len+1];
			strcpy(res, cur->pth);
			
			// Cleanup node
			delete cur;
			cur = NULL;
			return res;
		}
		
		int fr = (cur->i%N_BASE)*N_BASE;
		int to = fr + N_BASE;
		
		// Insert the next nodes randomly onto the stack
		int* order = randomOrder(cur->frq, fr, to);
		for (int i = 0; i < to-fr; ++i) {
			if (order[i] == -1) { continue; }
			int idx = fr + order[i];
			if (cur->frq[idx] <= 0) { continue; }
			Node* nxt = new Node(idx, cur->frq, cur->pth, seq_len);
			stk.push(nxt);
		}
		delete [] order;
		order = NULL;
		
		delete cur;
		cur = NULL;
	}
	
	return NULL;
}

// Is the graph split?
bool split(const int* frq)
{
	// Initialise the visited array
	bool* vis = new bool[N_DNUC];
	for (int i = 0; i < N_DNUC; ++i) {
		vis[i] = false;
	}
	
	// Push the first valid node onto the stack
	std::stack<int> stk;
	for (int i = 0; i < N_DNUC; ++i) {
		if (frq[i] > 0) {
			stk.push(i);
			vis[i] = true;
			break;
		}
	}
	// Depth first search to visit all nodes
	while (!stk.empty()) {
		int j = stk.top();
		stk.pop();
		for (int k = 0; k < N_BASE; ++k) {
			// Visit the parents
			int up = k*N_BASE + j/N_BASE;
			if (!vis[up] && frq[up] > 0) {
				stk.push(up);
				vis[up] = true;
			}
			// Visit the children
			int dn = k + (j%N_BASE)*N_BASE;
			if (!vis[dn] && frq[dn] > 0) {
				stk.push(dn);
				vis[dn] = true;
			}
		}
	}
	
	for (int i = 1; i < N_DNUC; ++i) {
		if (frq[i] > 0 && !vis[i]) {
			delete [] vis;
			vis = NULL;
			return true;
		}
	}
	
	delete [] vis;
	vis = NULL;
	
	return false;
}

// Calculate the imbalance
int* imbalance(const int* frq)
{
	int* res = new int[N_BASE];
	for (int i = 0; i < N_BASE; ++i) {
		res[i] = 0;
	}
	for (int i = 0; i < N_DNUC; ++i) {
		res[i/N_BASE] -= frq[i];
		res[i%N_BASE] += frq[i];
	}
	return res;
}

// Helper function
int sum(const int* arr, int n)
{
	int res = 0;
	for (int i = 0; i < n; ++i)
		res += arr[i];
	return res;
}

// Helper function
int* abs(const int* arr, int n)
{
	int* res = new int[n];
	for (int i = 0; i < n; ++i)
		res[i] = abs(arr[i]);
	return res;
}

int consumer(const int* arr)
/* Return the consumer else return -1 */
{
	for (int i = 0; i < N_BASE; ++i)
		if (arr[i] == -1) return i;
	return -1;
}

int* randomOrder(const int* frq, int fr, int to)
/* In-place shuffle */
{
	int sz = to-fr;
	int* valid = new int[sz];
	for (int i = 0; i < sz; ++i) {
		if (frq[fr+i] > 0) { valid[i] = 1; }
		else { valid[i] = 0; }
	}
	
	int* res = new int[sz];
	int c_pos = sz-1;
	while (c_pos >= 0) {
		int ttl = 0;
		for (int j = 0; j < sz; ++j) {
			if (valid[j] == 1) { ttl += frq[fr+j]; }
		}
		
		if (ttl > 0) {
			int pos = rand()%ttl;
			
			ttl = 0;
			for (int i = 0; i < sz; ++i) {
				if (valid[i] == 1) {
					ttl += frq[fr+i];
					if (pos < ttl) {
						res[c_pos] = i;
						valid[i] = 0;
						break;
					}
				}
			}
		}
		else { // Fill with junk
			while (c_pos >= 0) {
				res[c_pos] = -1;
				c_pos -= 1;
			}
			break;
		}
		c_pos -= 1;
	}
	delete [] valid;
	valid = NULL;
	
	return res;
}

int baseToIndex(char base)
{
	if (base == 'a') return 0;
	else if (base == 'c') return 1;
	else if (base == 'g') return 2;
	else if (base == 't') return 3;
	else if (base == 'u') return 3;
	return -1;
}

// --- Node class ---
Node::Node(int i, const int* frq, char pth, int seq_len)
{
	this->i = i;
	this->frq = new int[N_DNUC];
	memcpy(this->frq, frq, sizeof(int)*N_DNUC);
	this->pth = new char[seq_len+1];
	for (int j = 0; j < seq_len+1; ++j)
	{
		this->pth[j] = '\0';
	}
	this->pth[0] = pth;
}

Node::Node(int i, const int* frq, const char* pth, int seq_len)
{
	this->i = i;
	this->frq = new int[N_DNUC];
	memcpy(this->frq, frq, sizeof(int)*N_DNUC);
	this->pth = new char[seq_len+1];
	strncpy(this->pth, pth, seq_len+1);
}

Node::~Node()
{
	delete [] frq;
	frq = NULL;
	delete [] pth;
	pth = NULL;
}

// --- Entry point ---
int main(int argc, char** argv)
{
	srand(time(NULL));
	// Initialise the frequency array
	int* frq = new int[N_DNUC];
	for (int i = 0; i < N_DNUC; ++i)
	{
		frq[i] = 0;
	}
	int n = 1;
	
	// Parse the input into the frequecy array
	for (int i = 1; i < argc; ++i)
	{
		if (argv[i][0] == 'n')
		{
			char* val = new char[strlen(argv[i])-1];
			strcpy(val, argv[i]+2);
			n = atoi(val);
			continue;
		}
		int idx = baseToIndex(argv[i][0]) * N_BASE + baseToIndex(argv[i][1]);
		char* val = new char[strlen(argv[i])-2];
		strcpy(val, argv[i]+3);
		frq[idx] = atoi(val);
		delete [] val;
		val = NULL;
	}
	
	// Run the algorithm and print the output
	for (int i = 0; i < n; ++i)
	{
		char* res = generate(frq);
		if (res == NULL)
		{
			std::cout << "No sequence possible." << std::endl;
			delete [] res;
			res = NULL;
			break;
		}
		std::cout << res << std::endl;
		delete [] res;
		res = NULL;
	}
	
	// Cleanup and return
	delete [] frq;
	frq = NULL;
	return 0;
}
