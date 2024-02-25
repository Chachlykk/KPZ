from datetime import datetime
from pandas import DataFrame
import csv


def get_entances():
    now = datetime.now()
    new_row = [now.year, now.month, now.day, now.hour, now.minute, now.second]

    try:
        with open('entrances.csv', 'r', newline='') as f:
            csvreader = csv.reader(f)
            entrances = DataFrame(csvreader)

    except FileNotFoundError:
        entrances = DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second'])
        with open('entrances.csv', 'w', newline='') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(entrances)

    entrances.loc[len(entrances)] = new_row

    with open('entrances.csv', 'a', newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(new_row)


if __name__ == '__main__':
    get_entances()
