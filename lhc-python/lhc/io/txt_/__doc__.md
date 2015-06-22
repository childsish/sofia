CSV function files
==================

analyse.py
----------

Analyses a csv file to determine a good separation strategy for assigning entries to tracks.

### Algorithm (greedy)

 1. Start with all entries in one track.

 2. Remove intervals that reduce the cost when added to another or own track.

Cost is defined as the average cost for searching the index.

Cost = The sum of the costs for searching each track
Cost_track = log2(n) + mean number of intervals over all index points (n = number of index points)
Cost_point = Number of intervals at the point


-- Step 1 --

Track A (one index point)
1  [                  ]
2      [   ]
3      [ ]
4            [      ]
5            [ ]
6                [  ]
cost = log2(1) + 6/1
     = 6

-- Step 2 (solution) --

Track A (two index points)
2      [   ]
3      [ ]
4            [      ]
5            [ ]
6                [  ]
cost = log2(2) + 5/2
     = 3.5

Track B (one index point)
1  [                  ]
cost = log2(1) + 1/1
     = 1

total_cost = 4.5 

-- Step 3 --

Track A (two index points)
2      [   ]
3      [ ]
5            [ ]
6                [  ]
cost = log2(3) + 4/3
     = 2.585

Track B (ine index points)
1  [                  ]
4            [      ]
cost = log2(1) + 2/1
     = 2

total_cost = 4.585

### Procedure

1. Analyse intervals
2. Block compress file
3. Create index