from copy import deepcopy

class SidonState:
    """Contains a Sidon set in state, with additional data about differences and possible other elements"""
    def __init__( self, initState=[] ):
        self.state = []              # our Sidon set
        self.excluded = set([])      # numbers that cannot be added to our Sidon set
        self.differences = set([])   # differences between all elements of the set
        self.nextPositiveOpening = 1 # for canonical Sidon sets, the smallest positive number that can be added to the set
        
        # initialize
        for element in initState:
            self.add( element )
    
    def add( self, x ):
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
    
    def __str__( self ):
        return self.state.__str__()
    
    def __repr__( self ):
        return "<" + self.__str__() + ">"

def setsUnder( n ):
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

def maxUnder( n ):
    sets = setsUnder( n )
    maxElements = max( [len(x.state) for x in sets] )
    return filter( lambda x: len( x.state ) == maxElements, sets )

    


def buildSequence( n ):
    """Return the Mian-Chowla sequence for n elements.
    Could be more efficient, this is just a very simple sieve.
    """
    result = [1]
    excluded = set([1])
    differences = set([])
    
    while len( result ) < n:
        # find the next non-excluded element in the sequence
        x = result[-1]
        while x in excluded:
            x += 1
        
        # add any new differences between x and previous elements
        for a in result:
            differences.add( abs( a - x ) )
        
        # add our new element to our reslt sequence
        result.append( x )
        
        # exclude any numbers that would cause a duplicate difference
        # inefficient here, since we would only need to handle the
        # newest lengths
        for a in result:
            for difference in differences:
                excluded.add( a + difference )
                excluded.add( a - difference )
    return result