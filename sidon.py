#!/usr/bin/python -O

# computation of canonical Sidon sets
# @author Jonathan Olson

from copy import deepcopy

class SidonState:
    """Contains a Sidon set in state, with additional data about differences and possible other elements"""
    def __init__( self, *initState ):
        self.state = []              # our Sidon set
        self.excluded = set([])      # numbers that cannot be added to our Sidon set
        self.differences = set([])   # differences between all elements of the set
        self.nextPositiveOpening = 1 # for canonical Sidon sets, the smallest positive number that can be added to the set
        
        # initialize
        for element in initState:
            self.add( element )
    
    def add( self, x ):
        """Adds a number into the Sidon set, and computes the associated extra data"""
        # store new differences that we need to apply to all old elements
        freshDifferences = []
        
        # scan for new differences
        for a in self.state:
            diff = abs( a - x )
            if diff not in self.differences:
                freshDifferences.append( diff )
                self.differences.add( diff )
        
        # append the actual element, and exclude it
        self.state.append( x )
        self.excluded.add( x )
        
        # TODO: consider option for not adding in negative differences
        for a in self.state:
            # exclude fresh differences from all old elements
            for diff in freshDifferences:
                self.addExcludeDifferences( a, diff )
            
            # and exclude ALL differences from the new element
            for diff in self.differences:
                self.addExcludeDifferences( x, diff )
        
        # ensure that our next opening is not excluded
        while self.nextPositiveOpening in self.excluded:
            self.nextPositiveOpening += 1
    
    def addExcludeDifferences( self, a, diff ):
        self.excluded.add( a + diff )
        self.excluded.add( a - diff )
    
    def negatedPair( self, n ):
        return SidonState( *sorted( [n - x + 1 for x in self.state] ) )
    
    def canonical( self ):
        # negated pair for the maximum element
        offset = 1 - self.state[0]
        translated = SidonState( *[x + offset for x in self.state] )
        n = translated.state[-1]
        pair = translated.negatedPair( n )
        if translated.state < pair.state:
            return translated
        else:
            return pair
    
    def __str__( self ):
        return self.state.__str__()
    
    def __repr__( self ):
        return "<" + self.__str__() + ">"

def setsUnder( n ):
    """List of all Sidon subsets of 1,...,n"""
    # TODO: consider rewrite from setsIterate
    baseState = SidonState()
    baseState.add( 1 )
    
    def under( state, a ):
        result = [state]
        if a > n:
            return result
        for option in range( a, n + 1 ):
            if option not in state.excluded:
                stateCopy = deepcopy( state )
                stateCopy.add( option )
                result.extend( under( stateCopy, option + 1 ) )
        return result
    return under( baseState, 2 )

def setsIterate( n, callback ):
    """Calls callback successively with all elements from setsUnder( n )"""
    baseState = SidonState()
    baseState.add( 1 )
    
    def under( state, a ):
        callback( state )
        if a <= n:
            for option in range( a, n + 1 ):
                if option not in state.excluded:
                    stateCopy = deepcopy( state )
                    stateCopy.add( option )
                    under( stateCopy, option + 1 )
    under( baseState, 2 )

def maxUnder( n ):
    """List of Sidon subsets of 1,...,n that have the maximum possible cardinality"""
    sets = setsUnder( n )
    maxElements = max( [len(x.state) for x in sets] )
    return filter( lambda x: len( x.state ) == maxElements, sets )

def canonicalList( states ):
    """Canonicalizes multiple states, removing duplicates"""
    canonical = [state.canonical() for state in states]
    # TODO: better way of sorting out unique states
    results = []
    for element in canonical:
        ok = True
        for result in results:
            if result.state == element.state:
                ok = False
                break
        if ok:
            results.append( element )
    return results 

def canonicalMax( n ):
    """Returns a list of canonicalized Sidon sets of maximum cardinality within 1,...,n"""
    return canonicalList( maxUnder( n ) )

def mianChowla( n ):
    """First n elements of the Mian-Chowla Sequence"""
    result = SidonState()
    while len( result.state ) < n:
        result.add( result.nextPositiveOpening )
    return result

def hasMaximalOnly( n ):
    """Whether all maximal Sidon sets in 1,...,n contain 1 and n"""
    #return all( [x.state[-1] == n for x in maxUnder( n )] )
    k = [0] # array but a scalar value, so we can modify inside the closure
    kn = [True]
    def handle( s ):
        if len( s.state ) > k[0]:
            k[0] = len( s.state )
            kn[0] = (s.state[-1] == n)
        elif len( s.state ) == k[0]:
            kn[0] = kn[0] and (s.state[-1] == n)
    setsIterate( n, handle )
    return kn[0]

def websiteCanonicalList( nMax ):
    """Prints out a MathJax-compatible list of maximal canonical Sidon sets"""
    for n in [1,2,4,7,12,18,26,35,45]:
        sets = canonicalMax( n )
        print "<li>" + (", ".join( [ "$\{" + ",".join( [x.__str__() for x in s.state] ) + "\}$" for s in sets ] ) ) + "</li>"

def sumset( state ):
    """A sorted list of numbers of the form a+b where a and b are in the state"""
    result = []
    size = len( state.state )
    for i in range( size ):
        a = state.state[i]
        for j in range( i, size ):
            b = state.state[j]
            result.append( a + b )
    result.sort()
    return result

def holes( state ):
    """Numbers not in the sumset that are between 2*(minElement) and 2*(maxElement)"""
    spread = set(range( 2 * min( state.state ), 2 * max( state.state ) + 1 ))
    for x in sumset( state ):
        spread.remove( x )
    return sorted( list( spread ) )
