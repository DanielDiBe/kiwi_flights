# Daniel Diaz Benito <daniel.diaz.benito@gmail.com>
# 31-VIII-2018
# A small exercise in preparation for the Kiwi meeting.
# No License is offered for this piece of code.

import sys  # To capture stdin, stdout and stderr

csv_separation_character = ","

class Flight:
    def __init__(self, index,
            source=None, 
            destination=None,
            departure=None,
            arrival=None,
            flight_number=None,
            price=None,
            bags_allowed=None,
            bag_price=None):
        self.id = index
        self.source = source 
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.flight_number = flight_number
        self.price = price
        self.bags_allowed = bags_allowed
        self.bag_price = bag_price

def split_line(row):
    return (h.strip() for h in row.split(csv_separation_character))

def main(f_input, f_output, f_error, has_header=True):
    if f_input.isatty():
        f_error.write("Cannot input data to 'find_combinations' in interactive mode")
        exit(1)

    headers = ['source', 'destination', 'departure', 'arrival', 'flight_number', 'price', 'bags_allowed', 'bag_price']
    # Check the input header
    if has_header:
        accepted_headers = set(headers)
        headers = list(split_line(f_input.readline()))
        # Use sets in order to accept any order but ensure all the required 
        # fields exist and only once
        headers_set = set(headers)
        if len(accepted_headers & headers_set) != 8:
            f_error.write("Required input headers missing: {}".format(", ".join(accepted_headers - headers_set)))
            exit(2)
        if len(headers_set - accepted_headers) > 0:
            f_error.write("Unknown headers are present: {}".format(", ".join(headers_set - accepted_headers)))
            exit(2)

    # Load each line as a flight
    flights = []
    index = 0
    for l in f_input:
        index += 1
        flights.append(
            Flight(index, **dict(zip(headers, split_line(l))))
        )
    
    # Flights database is populated, let's begin our calculus
    for f in flights:
        print(f.id, f.flight_number)


if __name__ == "__main__":
    main(sys.stdin, sys.stdout, sys.stderr)