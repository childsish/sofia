# Copyright (c) 2008-2009, David Simcha
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#   * Neither the name of the authors nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import psyco

from scipy.stats import *

def fisherExact(c) :
        """Performs a Fisher exact test on a 2x2 contingency table in list of lists
           format.  Returns a tuple of (odds ratio, two-tailed P-value).
           
           Examples:
           >>> fisherExact([[100, 2], [1000, 5]])
           (0.25, 0.13007593634330314)
           """
        oddsRatio = c[0][0] * c[1][1] / float(c[1][0] * c[0][1])
        n1 = c[0][0] + c[0][1]
        n2 = c[1][0] + c[1][1]
        n  = c[0][0] + c[1][0]
       
        mode = int(float((n + 1) * (n1 + 1)) / (n1 + n2 + 2))
        pExact = hypergeom.pmf(c[0][0], n1 + n2, n1, n)
        pMode = hypergeom.pmf(c[0][0], n1 + n2, n1, n)
       
        if c[0][0] == mode :
                return oddsRatio, 1.0
        elif c[0][0] < mode :
                pLower = hypergeom.cdf(c[0][0], n1 + n2, n1, n)
               
                # Binary search for where to begin upper half.
                min = mode
                max = n
                guess = -1
                while min != max :
                        guess = max if (max == min + 1 and guess == min) else \
                                        (max + min) / 2

                        pGuess = hypergeom.pmf(guess, n1 + n2, n1, n)
                        if pGuess <= pExact and hypergeom.pmf(guess - 1, n1 + n2, n1, n) > pExact :
                                break
                        elif pGuess < pExact :
                                max = guess
                        else :
                                min = guess

                if guess == -1 and min == max :
                        guess = min

                return oddsRatio, pLower + hypergeom.sf(guess - 1, n1 + n2, n1, n)
        else :
                pUpper = hypergeom.sf(c[0][0] - 1, n1 + n2, n1, n);

                # Special case to prevent binary search from getting stuck.
                if hypergeom.pmf(0, n1 + n2, n1, n) > pExact :
                        return oddsRatio, pUpper

                # Binary search for where to begin lower half.
                min = 0
                max = mode
                guess = -1
                while min != max :
                        guess = max if (max == min + 1 and guess == min) else \
                                        (max + min) / 2
                        pGuess = hypergeom.pmf(guess, n1 + n2, n1, n);

                        if pGuess <= pExact and hypergeom.pmf(guess + 1, n1 + n2, n1, n) > pExact :
                                break;
                        elif pGuess <= pExact  :
                                min = guess
                        else :
                                max = guess

                if guess == -1 and min == max :
                        guess = min

                return oddsRatio, pUpper + hypergeom.cdf(guess, n1 + n2, n1, n)
psyco.bind(fisherExact)

def testFisherExact() :
        """Just some tests to show that fisherExact() works correctly."""
        def approxEqual(n1, n2) :
                return abs(n1 - n2) < 0.01

        res = fisherExact([[100, 2], [1000, 5]])
        assert(approxEqual(res[1], 0.1301))
        assert(approxEqual(res[0], 0.25))
        res = fisherExact([[2, 7], [8, 2]])
        assert(approxEqual(res[1], 0.0230141))
        assert(approxEqual(res[0], 4.0 / 56))
        res = fisherExact([[5, 1], [10, 10]])
        assert(approxEqual(res[1], 0.1973244))
        res = fisherExact([[5, 15], [20, 20]])
        assert(approxEqual(res[1], 0.0958044))
        res = fisherExact([[5, 16], [20, 25]])
        assert(approxEqual(res[1], 0.1725862))
        res = fisherExact([[10, 5], [10, 1]])
        assert(approxEqual(res[1], 0.1973244))
       
testFisherExact() 