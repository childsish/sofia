import random

from collections import defaultdict
from math import log

from lhc.interval import Interval


class Graph(object):
    def __init__(self, es=[], vs=[]):
        self.es = defaultdict(set)
        for v in vs:
            self.es[v] = set()
        for fr, to in es:
            self.es[fr].add(to)

    def __len__(self):
        return len(self.es)

    def add_node(self, node):
        self.es[node] = []

    def add_edge(self, fr, to):
        self.es[fr].add(to)
        self.es[to].add(fr)

    def decompose(self, visited=None):
        graphs = []
        visited = set() if visited is None else visited
        for fr, tos in self.es.iteritems():
            if fr in visited:
                continue
            visited.add(fr)
            stk = [(fr, to) for to in tos]
            graph = Graph(vs=[fr])
            for fr, to in stk:
                graph.add_edge(fr, to)
            while len(stk) > 0:
                root, fr = stk.pop()
                if fr in visited:
                    continue
                visited.add(fr)
                es = [(fr, to) for to in self.es[fr]]
                for fr, to in es:
                    graph.add_edge(fr, to)
                stk.extend(es)
            graphs.append(graph)
        return graphs


class Track(object):
    def __init__(self, graphs):
        self.graphs = graphs

    def get_index_points(self, intervals):
        return sorted(min(intervals[i].start for i in graph.es) for graph in self.graphs)

    def get_cost(self):
        try:
            res = log(len(self.graphs), 2) +\
                  sum(len(graph) for graph in self.graphs) / float(len(self.graphs))
        except ValueError, e:
            import sys
            sys.stderr.write('len(graphs): {}, sum(graph_lengths): {}'.format(len(self.graphs), sum(len(graph) for graph in self.graphs)))
            raise e
        return res

    def add_intervals(self, nodes, intervals):
        graphs = [Graph(vs=nodes)]
        for i in xrange(len(nodes)):
            for j in xrange(i + i, len(nodes)):
                if intervals[nodes[i]].overlaps(intervals[nodes[j]]):
                    graphs[0].add_edge(nodes[i], nodes[j])
        for graph in self.graphs:
            sz = len(graphs[0])
            for to in graph.es:
                for node in nodes:
                    if intervals[node].overlaps(intervals[to]):
                        graphs[0].add_edge(node, to)
            if len(graphs[0]) > sz:
                for fr, tos in graph.es.iteritems():
                    for to in tos:
                        graphs[0].add_edge(fr, to)
            else:
                graphs.append(graph)
        self.graphs = graphs

    def test_intervals(self, nodes, intervals):
        lens = [len(nodes)]
        for graph in self.graphs:
            sz = lens[0]
            for to in graph.es:
                if any(intervals[node].overlaps(intervals[to]) for node in nodes):
                    lens[0] += len(graph)
                    break
            if lens[0] == sz:
                lens.append(len(graph))
        return log(len(lens), 2) + max(lens), -log(len(lens), 2)

    def remove_intervals(self, graph_idx, nodes):
        graph = self.graphs[graph_idx]
        for node in nodes:
            for to in graph.es[node]:
                graph.es[to].remove(node)
            del graph.es[node]

        del self.graphs[graph_idx]
        self.graphs.extend(graph.decompose())

    def suggest_candidates(self):
        res = []
        for i, graph in enumerate(self.graphs):
            score, vertex = self.get_highest_degree(graph)
            res.append((score, vertex, i))
        return sorted(res)[-1]

    def get_highest_degree(self, graph):
        degrees = [(len(es), [v]) for v, es in graph.es.iteritems()]
        degrees.sort()
        return degrees[-1]

def analyse(intervals):
    tracks = get_initial_tracks(intervals)
    while True:
        (score, vertices, graph), track_idx = sorted(((track.suggest_candidates(), track_idx)
                                        for track_idx, track in enumerate(tracks)), key=lambda x: x[0][0])[-1]
        track = tracks[track_idx]
        d_sub = track.get_cost()
        original_cost = sum(track.get_cost() for track in tracks)
        all_nodes = set()
        track.remove_intervals(graph, vertices)
        all_nodes.update(vertices)
        d_sub = track.get_cost() - d_sub
        all_nodes = list(all_nodes)

        d_adds = []
        for i, track in enumerate(tracks):
            if i == track_idx:
                continue
            d_add, pref = track.test_intervals(all_nodes, intervals)
            d_adds.append((d_add - track.get_cost(), pref, i))
        graph = Graph(vs=all_nodes)
        for i in xrange(len(all_nodes)):
            for j in xrange(i + 1, len(all_nodes)):
                graph.add_edge(intervals[all_nodes[i]], intervals[all_nodes[j]])
        track = Track(graph.decompose())
        d_adds.append((track.get_cost(), 0, -1))
        d_add, pref, track_idx = min(d_adds)
        print original_cost, d_sub + d_add, sum(track.get_cost() for track in tracks), len(tracks)
        if d_sub + d_add <= 0:
            if track_idx == -1:
                tracks.append(track)
            else:
                tracks[track_idx].add_intervals(all_nodes, intervals)
        else:
            break
    return tracks


def get_initial_tracks(intervals):
    for i, interval in enumerate(intervals):
        interval.data = i
    from lhc.collections import IntervalTree
    tree = IntervalTree(intervals)
    graph = Graph()
    for i, interval in enumerate(intervals):
        overlap = tree.intersect(interval)
        for o in overlap:
            if i != o.data:
                graph.add_edge(i, o.data)
    track = Track(graph.decompose())
    return [track]


def remove_duplicates(intervals):
    res = defaultdict(list)
    for i, interval in enumerate(intervals):
        if interval.start == interval.stop:
            continue
        res[interval].append(i)
    return list(zip(*sorted(res.items(), key=lambda item: item[1]))[0]), res


def main():
    intervals = read_file()
    #intervals = generate_intervals(160000)
    unq_intervals, interval_map = remove_duplicates(intervals)
    print 'Number of intervals: ', len(intervals)
    print 'Number of unique intervals: ', len(unq_intervals)
    print 'Analysing'
    tracks = analyse(unq_intervals)
    track_costs = [track.get_cost() for track in tracks]
    #for track in tracks:
    #    print sorted(track.get_index_points(intervals))
    #    for graph in track.graphs:
    #        print sorted(unq_intervals[idx] for idx in graph.es)
    #    print
    print track_costs
    print sum(track_costs)


def generate_intervals(n):
    random.seed(260782)
    intervals = []
    for i in xrange(n):
        start = random.randint(1900, 2015)
        stop = start + random.randint(70, 100)
        intervals.append(Interval(start, stop))
    return intervals


def read_file():
    intervals = []
    #fhndl = open(r'D:\data\public\genomic_feature\gencode.v19.annotation.gtf')
    fhndl = open(r'D:\data\public\genomic_feature\TAIR10_GFF3_genes.gff')
    for i, line in enumerate(fhndl):
        parts = line.rstrip('\r\n').split('\t')
        if parts[0].lower() != 'chr1':
            break
        intervals.append(Interval(int(parts[3]), int(parts[4])))
    return intervals

if __name__ == '__main__':
    import sys
    sys.exit(main())
