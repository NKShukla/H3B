import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import glob

# TO ADD THE TIME DIFFERENCE COLUMN IN THE UPDATED CSV


def get_files(path, extension):
    """
    get all files in a directory
    """
    return glob.glob(os.path.join(path, f'*.{extension}'))


print(get_files('data/phase1', 'pcap.csv'))


def part1(file_location, file_name):
    print(file_location)
    print(file_name)
    df = pd.read_csv(file_location, sep='\t')
    headerList = ['Time(ms)', 'Length']
    df.to_csv(f"data/phase2/new-{file_name}",
              header=headerList, index=False)


def part2(file_location, file_name):
    df = pd.read_csv(f"data/phase2/new-{file_name}")
    df['Time(ms)'] = df['Time(ms)']*1000
    new_df = pd.DataFrame(df['Time(ms)'].astype(int), columns=['Time(ms)'])
    new_df['Length'] = df['Length']
    new_df = new_df.groupby('Time(ms)').sum()

    new_df.to_csv(f"data/phase2/new-{file_name}", index=True)


def part3(file_location, file_name):
    df = pd.read_csv(f"data/phase2/new-{file_name}")
    df['Time Diff'] = 0
    i = 1
    for ind, row in df.iterrows():
        df.at[ind, 'Time Diff'] = df.iloc[ind]['Time(ms)'] - \
            df.iloc[ind-1]['Time(ms)']
        assert df.iloc[ind]['Time(ms)'] - \
            df.iloc[ind-1]['Time(ms)'] == df.iloc[ind]['Time Diff']
        print(i)
        i += 1
    df.at[0, 'Time Diff'] = 0
    # raise Exception(df.iloc[0]['Time Diff'])
    df.to_csv(f"data/phase2/new-{file_name}", header=False, index=False)


for file_location in get_files('data/phase1', 'pcap.csv'):
    if os.path.isfile(file_location):
        file_name = file_location.split('/')[-1]

        part1(file_location, file_name)

        part2(file_location, file_name)

        part3(file_location, file_name)

        print(f"Done with {file_name}")
