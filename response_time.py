# import libraries
import requests
import numpy as np
import sys

# retrieve command line arguments for API IP address
host = sys.argv[1]
# Set a query text
params ={'query': "Hmm. Human Music. I like it."}

def main():
    # create empty list of elapsed times
    elapsed_time = []
    # loop 100 times: make query call to API, 
    # and add the elapsed time to the emptyy list created above
    for i in range(100):
        response = requests.get(host, params)
        elapsed_time.append(response.elapsed.total_seconds())
    # return the list of elapsed times
    return elapsed_time


if __name__ == '__main__':
    result = main()
    # print mean, median, min, max of the list elapsed_time
    print("Mean Response Time: {} seconds".format(np.mean(result)))
    print("Median Response Time: {} seconds".format(np.median(result)))
    print("Min Response Time: {} seconds".format(np.min(result)))
    print("Max Response Time: {} seconds".format(np.max(result)))