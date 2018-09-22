"""
plot.py
This script reads a data file of daily events and plots them on a graph
with accompanying statistics using matplotlib.

The data file should have the following format for each day:

180917
# Comment (optional)
0622 0835 1106 1219 1315 1506 1644
"""

# matplotlib
import matplotlib.pyplot as plt

# For customizing axis ticks
import matplotlib.ticker as ticker

# For offsetting annotation on dates axis
# and converting times to float
import matplotlib.dates as mdates

# For adding dates axis left/right margins
# and using the datetime format
from datetime import datetime, timedelta, time

# For counting frequency of events on the same date
from collections import Counter

# For calculating standard deviation
from math import sqrt

AVERAGE_PERIOD = 7				# Plot average over how many previous days
DATE_TICKS_INTERVAL = 7			# Frequency of X axis date ticks
Y_AXIS_TICKS = ['02h', '07h', '12h', '17h', '22h']

# Initialize lists of events, comments, event counts & deltas
events = []
comments = []
events_per_day = []
deltas = []

def normalized_event_time(event):
	"""Return the time of a datetime event normalized to a value between 0 and 1."""
	# date2num takes a datetime and converts it to matplotlib float notation,
	# counting whole days from 1900 with decimals as fractions 24 hours.
	# With modulo 1 we just extract the time from the datetime objects
	# and convert it to a value between 0.0 and 1.0
	return mdates.date2num(event) % 1

# Read the data file
with open('data.txt', 'r', encoding='utf-8') as f:

	while True:

		# Read only the first 6 characters of a date
		date = f.readline()[:6]

		# If there is no data then we have reached the end of the file
		if not date:
			break

		# Read the next line to get the hours data
		hours = f.readline().strip('\n')

		# If the next line is a comment,
		# store the comment and read the next line to get the hours
		if hours.startswith('#'):
			comments.append(hours[2:])
			hours = f.readline().strip('\n')
		else:
			comments.append('')

		# Split the hours line and reverse its order
		hours = list(reversed(hours.split(' ')))

		# For each event, add a properly formatted datetime item
		# to the events list
		for hour in hours:
			events.append(datetime.strptime(date + hour, '%y%m%d%H%M'))
		
		# Skip an empty line
		f.readline()

# Reverse the events and comments lists
# because the data is recorded in reverse order
events = list(reversed(events))
comments = list(reversed(comments))

# Build list of time deltas between all events
deltas = [y - x for x,y in zip(events,events[1:])]

# Build list of dates and times for all events and for long nights without events
long_nights_x = []
long_nights_y = []
event_dates = []
event_times = []

for i, e in enumerate(events):

	# List of the dates extracted from the datetime objects
	# This will be the main scatter x axis value
	event_dates.append(e.date())

	# List of the times extracted from the datetime objects
	# This will be the main scatter y axis value
	event_times.append(normalized_event_time(e))

	# x and y lists of dates and times of long nights without events
	# We want time periods of more than 6 hours ending between 6h30 and 8h00
	if e - events[i-1] >= timedelta(hours=(6)) and e.time() < time(hour=8) and e.time() > time(hour=6, minute=30): 
		long_nights_x.append(e.date())
		long_nights_y.append(normalized_event_time(e))

# Counter (from 'collections' module) creates a dictionary where
# key = date, value = frequency
# values() returns a view of the values of that dictionary
# list converts the view into a list
events_per_day = list(Counter(event_dates).values())

# Get a list of dates only using the same method
unique_dates = list(Counter(event_dates).keys())

# We want to plot stats for all dates except the last one
# We keep "today" for showing this value later
today = events_per_day.pop()
unique_dates.pop()
comments.pop()

# Build a sorted list of events_per_day for median calculations
events_per_day_sorted = sorted(events_per_day)

# Calculate the average, median, midrange & deviation of number of events per day
average  = sum(events_per_day_sorted) / len(events_per_day_sorted)
median   = events_per_day_sorted[int(len(events_per_day_sorted)/2)]
midrange = (events_per_day_sorted[0] + events_per_day_sorted[-1])/2
standard_dev = sqrt(sum([(count - average) ** 2 for count in events_per_day]) / len(events_per_day))

# Scale the events_per_day list to fit 0.0 to 1.0
# We want the median value to be at 0.5 on the y axis
events_per_day_normalized = [n  / (median * 2) for n in events_per_day]

# Create an average progress plot showing
# the average calculated over the last AVERAGE_PERIOD days
# Iterate through the events_per_day list (we need the index, 'value' is ignored)
average_over_period = []
for index, value in enumerate(events_per_day):

	# Iterate through the N days leading up to and including the current index
	# Since we go back N days this can result in a negative index,
	# in which case we round to zero with the max function
	# 'range' in exclusive so we add 1 to the index value
	total = 0
	for j in range(max(0, index+1-AVERAGE_PERIOD), index+1):
		total += events_per_day[j]

	# Calculate the average over the last N days
	average_over_period.append(total / min(AVERAGE_PERIOD, index+1))

# Scale the average_over_period list to fit 0.0 to 1.0
# We want the median value to be at 0.5 on the y axis
average_over_period_normalized = [n / (median * 2) for n in average_over_period]

# Calculate min, max and average delta
# Giving datetime.timedelta(0) as the start value makes sum work on timedeltas
# (https://stackoverflow.com/questions/3617170/average-timedelta-in-list)
# We use only the first 3 characters from the string. It's a tiny hack because
# deltas never have two digits, so we don't deal with them.
delta_min = str(min(deltas))[:4] + ' on ' + str(events[deltas.index(min(deltas))].date())
delta_max = str(max(deltas))[:4] + ' on ' + str(events[deltas.index(max(deltas))].date())
delta_average = str(sum(deltas, timedelta(0)) / len(deltas))[:4]

# Print stats
stats = {
	'Today' : today,
	'Days recorded' : len(events_per_day),
	'Events recorded' : sum(events_per_day),
	'Min events per day' : events_per_day_sorted[0],
	'Max events per day' : events_per_day_sorted[-1],
	'Per day average' : "%.2f" % average,
	'Per day median' : "%.2f" % median,
	'Per day midrange' : "%.2f" % midrange,
	'Std deviation' : "%.2f" % standard_dev,
	'Min delta' : delta_min,
	'Max delta' : delta_max,
	'Average delta' : delta_average,
	'Long nights' : len(long_nights_x)
}

for key, value in stats.items():
	print('{:>18} : {}'.format(key, str(value)))

# Plot horizontal lines of median, min and max values
plt.axhline(median/(median * 2), color='#ff4d4d')
plt.text(0.01, median/(median * 2) + 0.01, str(median), transform=plt.gca().transAxes, fontsize=8)
plt.axhline(events_per_day_sorted[-1]/(median * 2), color='r', linewidth=0.5)
plt.text(0.01, events_per_day_sorted[-1]/(median * 2) + 0.01, str(events_per_day_sorted[-1]), transform=plt.gca().transAxes, fontsize=8)
plt.axhline(events_per_day_sorted[0]/(median * 2), color='r', linewidth=0.5)
plt.text(0.01, events_per_day_sorted[0]/(median * 2) + 0.01, str(events_per_day_sorted[0]), transform=plt.gca().transAxes, fontsize=8)

# Plot horizontal lines of standard deviation
plt.axhline((median + standard_dev)/(median * 2), color='#ffcc00', linewidth=0.5)
plt.axhline((median - standard_dev)/(median * 2), color='#ffcc00', linewidth=0.5)

# Plot the scatter graph
plt.scatter(event_dates, event_times, marker='.', color='#ffa327')

# Plot the average_over_period line
plt.plot(unique_dates, average_over_period_normalized, color='#00b300')

# Plot the count line
plt.plot(unique_dates, events_per_day_normalized, marker='o', markersize=3)

# Plot the long nights bars
plt.bar(long_nights_x, long_nights_y, width=0.1, alpha=0.5, color='#d147a3', linewidth=0)

# Plot the comments
# enumerate returns an index and an element in a tuple
# We iterate through that list and, if there's a comment,
# we plot it with a slight offset and properly rotated
# (without rotation_mode this looks bad)
# In order to offset the date value we first convert it to a float with date2num
offset_x = 0.65  # 1 is a whole axis tick here
offset_y = 0.02  # The y axis goes from 0.0 to 1.0

for i, text in enumerate(comments):
	if text:
		text_x = mdates.date2num(unique_dates[i]) + offset_x
		text_y = offset_y
		plt.annotate(
			text, (text_x, text_y),
			fontsize=8,
			color='#777777',
			rotation='vertical',
			rotation_mode='anchor')

# Set x axis limits, one day margin on each side
plt.xlim(events[0] - timedelta(days=2), events[-1] + timedelta(days=1))

# Set y axis limits
plt.ylim(0, 1)

# Set x axis font size
# We don't need rotation when using autofmt below
plt.xticks(fontsize=8)

# Set y axis tick labels by converting from string %H:%M to matplotlib float
# (0.5 = noon)
tick_values = [mdates.date2num(datetime.strptime(tick, '%Hh')) % 1 for tick in Y_AXIS_TICKS]
plt.yticks(tick_values, Y_AXIS_TICKS)

# Set x axis ticker labels to display every tick
# (otherwise we get 5-day interval ticks only)
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(DATE_TICKS_INTERVAL))

# Labels and title
plt.xlabel('Date')
plt.ylabel('Time')
plt.title('Events time distribution')

# Autoformat x axis labels with 45 degree rotation
plt.gcf().autofmt_xdate()
plt.show()
