# Daniel Diaz Benito <daniel.diaz.benito@gmail.com>
# 31-VIII-2018 and 2-IX-2018
# A small exercise in preparation for the Kiwi meeting.
# No License is offered for this piece of code.

import sys  # To capture stdin, stdout and stderr
import datetime  # To parse transfer time
import csv

csv_separation_character = ","

def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

def hours_difference(date_string1, date_string2):
    diff = parse_date(date_string2) - parse_date(date_string1)
    return diff.days*24 + diff.seconds/3600

class FlightBase:
    @staticmethod
    def get_CSV_headers():
        # This is a list of the intended headers for the output and
        # its order
        return "source,destination,departure,arrival,transfers_count,flight_numbers_chain,bags_allowed,price,price_with_1_bag,price_with_2_bags"

    def to_CSV_entry(self):
        # Because the output of the command is not very well defined
        # besides it should be able to be procesed later, let's just
        # transfer all the info for the combination in a way it is
        # easy to capture by a postprocessing pipe
        flight_code = lambda fl: fl.flight_number
        return csv_separation_character.join((
            self.source,
            self.destination,
            self.departure,
            self.arrival,
            str(len(self.flights)-1),  # Number of transfers involved
            "->".join(map(flight_code, self.flights)),  # Chain of flights
            str(self.bags_allowed),
            str(self.price),  # Price for no bags
            str(self.price+self.bag_price) if self.bags_allowed>=1 else "-",  # Price for one bag
            str(self.price+self.bag_price*2) if self.bags_allowed>=2 else "-",  # Price for two bags
        ))

    def can_chain(itinerary1, itinerary2):
        # Additionally the transfer between both itineraries should be
        # between 1 hour and 4
        diff = hours_difference(itinerary1.arrival, itinerary2.departure)
        if(diff<1 or diff>4):
            return False
        # In order for two itineraries to be chainable the destination of
        # the first must match the source of the second, and none of their
        # source airports should repeat. The destination of the second
        # itinerary neither can be repeate, except as the source of the
        # first itinerary.
        if itinerary1.destination != itinerary2.source:
            return False
        for airport2 in (f.source for f in itinerary2.flights):
            for airport1 in (f.source for f in itinerary1.flights):
                if airport1 == airport2:
                    return False
        # Finally check itinerary2 destination is not within 1
        airport2 = itinerary2.destination
        for airport1 in (f.source for f in itinerary1.flights[1:]):
            if airport1 == airport2:
                return False
        return True

class Flight(FlightBase):
    def __init__(self,
            source=None, 
            destination=None,
            departure=None,
            arrival=None,
            flight_number=None,
            price=None,
            bags_allowed=None,
            bag_price=None):
        self.source = source 
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.flight_number = flight_number
        self.price = int(price)
        self.bags_allowed = int(bags_allowed)
        self.bag_price = int(bag_price)
        # For compatibility with Flight Itineraries
        self.flights = [self]

    def __str__(self):
        return "{} ({}->{})".format(self.flight_number, self.source, self.destination)

class FlightItinerary(FlightBase):
    def __init__(self, itinerary1, itinerary2):
        # Chain the flights in both itineraries
        self.flights = itinerary1.flights + itinerary2.flights
        self.source = itinerary1.source
        self.destination = itinerary2.destination
        self.departure = itinerary1.departure
        self.arrival = itinerary2.arrival
        # And calculate their values
        self.price = itinerary1.price + itinerary2.price
        self.bag_price = itinerary1.bag_price + itinerary2.bag_price
        self.bags_allowed = min(itinerary1.bags_allowed, itinerary2.bags_allowed)

    def __str__(self):
        return "Itinerary ({}->{})".format("->".join((f.source for f in self.flights)), self.destination)

def split_line(row):
    return (h.strip() for h in row.split(csv_separation_character))

def main(f_input, f_output, f_error, has_header=True):
    if f_input.isatty():
        f_error.write("Cannot input data to 'find_combinations' in interactive mode\n")
        exit(1)

    # Load each line as a flight
    flights = list(Flight(**l) for l in csv.DictReader(f_input))

    # Flights database is populated, let's begin our calculus
    
    def match_itineraries(start_itineraries, end_itineraries):
        new_itineraries = []
        for i in start_itineraries:
            for j in end_itineraries:
                if i == j:
                    continue
                if i.can_chain(j):
                    new_itineraries.append(FlightItinerary(i, j))
        return new_itineraries

    # Not much time to think on a combinatory algorithm, the input is
    # not that large, let's just break through this in the brute way for now...
    # Starting itineraries equal the flights list
    itineraries = []
    new_itineraries = flights+[]
    while len(new_itineraries):
        recent_itineraries = new_itineraries
        itineraries += new_itineraries
        # Only compare the recent itineraries against the all other existing ones
        new_itineraries = match_itineraries(recent_itineraries, itineraries)
        # Because the way we chain the next matching is already ensured by mirroring
        #new_itineraries += match_itineraries(itineraries, recent_itineraries)

    #check_equivalent_itineraries(itineraries)

    # And pass the result for further processing
    f_output.write(FlightBase.get_CSV_headers()+"\n")
    for it in itineraries:
        f_output.write(it.to_CSV_entry()+"\n")

    # And we are done, depending on the program purpose we would
    # close the stream, let the system close it on program exit,
    # or just stay alive for more input-output (with some modifications)

# This is a test to check during development whether there are repeated
# combinations in the output
def check_equivalent_itineraries(itineraries):
    combinations = ['PV404', 'PV755', 'PV729', 'PV966', 'PV398', 'PV870', 'PV320', 'PV540', 'PV290', 'PV876', 'PV275', 'PV996', 'PV243', 'PV146', 'PV634', 'PV961', 'PV101', 'PV100', 'PV672', 'PV442', 'PV837', 'PV953', 'PV388', 'PV378', 'PV046', 'PV883', 'PV999', 'PV213', 'PV873', 'PV452', 'PV278', 'PV042', 'PV207', 'PV620', 'PV478', 'PV414', 'PV699', 'PV974', 'PV519', 'PV260', 'PV451', 'PV197', 'PV755->PV634', 'PV966->PV146', 'PV870->PV837', 'PV540->PV634', 'PV876->PV442', 'PV996->PV540', 'PV101->PV870', 'PV837->PV320', 'PV837->PV290', 'PV837->PV275', 'PV378->PV414', 'PV046->PV974', 'PV046->PV451', 'PV213->PV197', 'PV873->PV260', 'PV207->PV634', 'PV620->PV042', 'PV414->PV243', 'PV699->PV634', 'PV974->PV672', 'PV519->PV442', 'PV260->PV243', 'PV451->PV042', 'PV378->PV414->PV243', 'PV046->PV974->PV672', 'PV873->PV260->PV243']
    flight_code = lambda fl: fl.flight_number
    flights_str = lambda it: "->".join(map(flight_code, it.flights))
    names = []
    for it in itineraries:
        name = flights_str(it)
        if name in names:
            print("Found a repeated combination:", name)
        else:
            names.append(name)
        if name not in combinations:
            print("Found an unexpected combination:", name)
    print(names)

if __name__ == "__main__":
    try:
        main(sys.stdin, sys.stdout, sys.stderr)
    except Exception as err:
        sys.stderr.write(str(err)+"\n")
        exit(3)