#include "math.h"

// Square root of integer
// https://en.wikipedia.org/wiki/Integer_square_root
unsigned int sqrt(unsigned int s)
{
	unsigned int x0 = s / 2;			// Initial estimate
	                        			// Avoid overflow when s is the maximum representable value

	// Sanity check
	if ( x0 != 0 )
	{
		unsigned int x1 = ( x0 + s / x0 ) / 2;	// Update

		while ( x1 < x0 )				// This also checks for cycle
		{
			x0 = x1;
			x1 = ( x0 + s / x0 ) / 2;
		}

		return x0;
	}
	else
	{
		return s;
	}
}