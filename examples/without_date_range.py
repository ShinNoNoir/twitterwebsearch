'''
Example without date range.
'''

import time
import twitterwebsearch

QUERY = 'president'
CUTOFF = 500

def main():
    start_time = time.time()
    for i, tweet in enumerate(twitterwebsearch.search(QUERY)):
        n = i+1
        print '%s tweets crawled...\r' % n,
        
        if n >= CUTOFF:
            break
    
    end_time = time.time()
    
    print '\nTook %s seconds' % (end_time - start_time) 

if __name__ == '__main__':
    main()
