#ifndef DIGEN_H
#define DIGEN_H

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stack>
#include <algorithm>

extern int N_BASE;
extern int N_DNUC;
extern char BASES[];

struct Node
{
	int i; // The next dinucleotide to add
	int* frq; // The remaining dinucleotides (including i)
	char* pth; // The current path followed
	
	Node(int i, const int* frq, char pth, int seq_len);
	
	Node(int i, const int* frq, const char* pth, int seq_len);
	
	~Node();
};

char* generate(const int* frq);

bool split(const int* frq);

int* imbalance(const int* frq);

int sum(const int* arr, int n);

int* abs(const int* arr, int n);

int consumer(const int* arr);

int* randomOrder(const int* frq, int fr, int to);

int baseToIndex(char base);

#endif//DIGEN_H
