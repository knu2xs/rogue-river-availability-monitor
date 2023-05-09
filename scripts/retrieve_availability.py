#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from bs4 import BeautifulSoup
import pandas as pd
import requests

# url where to find the rogue river availability
url = "https://www.blm.gov/or/resources/recreation/rogue/rogue_river.php"

# paths to useful resources
dir_prj = Path.cwd().parent
dir_data = dir_prj / 'data'
dir_raw = dir_data / 'raw'

# location where partitioned output will be saved
out_dir = dir_raw / 'rogue_retrieved_availability'

def get_row_values(tr: BeautifulSoup) -> List[str]:
    """
    Extract the values from the BeautifulSoup row representation into just a list of values.
    
    Args:
        tr: BeautifulSoup table row.
    """
    td_lst = tr.find_all('td')
    td_val_lst = [td.decode_contents() for td in td_lst]
    return td_val_lst

def get_table_values(tbl: BeautifulSoup) -> List[List[str]]:
    """
    Pluck the table row BeautifulSoup objects into a list of lists repressenting the rows values.
    
    Args:
        tbl: BeautifulSoup object for the table extracted from the full "soup".
    """
    val_lst = [get_row_values(tr) for tr in tbl.find_all('tr')]
    val_lst = [r for r in val_lst if len(r) == 3]
    val_lst = [r for r in val_lst if r != ['Day', 'Date', 'Spaces']]
    return val_lst

def process_table(tbl: BeautifulSoup) -> pd.DataFrame:
    """
    Convert a BeautifulSoup table into a Pandas DataFrame.

    Args:
        tbl: BeautifulSoup table plucked from the larger "soup".
    """
    mth_str = tbl.find('th').decode_contents()    
    row_lst = get_table_values(tbl_lst[0])
    out_lst = [[datetime.strptime(f'{int(r[1]):02d} {mth_str} {yr}', '%d %B %Y').date().isoformat(), r[2]] 
               for r in row_lst]
    out_df = pd.DataFrame(out_lst, columns=['launch_date', 'available_user_days'])
    return out_df

# retrieve the data from the url
res = requests.get(url)

# parse the returned html into 'soup'
soup = BeautifulSoup(res.text, 'html.parser')

# extract the availablity tables out of the soup
tbl_lst = [tbl for tbl in soup.find_all('table') if tbl.attrs['summary'].startswith("Available Float Space Openings")]

# get today's date and extract the year to a discrete variable
today = datetime.today()
yr = today.year

# get all the availability into one pandas data frame
df = pd.concat([process_table(tbl) for tbl in tbl_lst])

# create a partition directory in the output directory
partition_dir_nm = f"retrieval_date={today.date().isoformat()}"

out_pth = out_dir / partition_dir_nm

if not out_pth.exists():
    out_pth.mkdir(parents=True)

# save the data as a part file in the partition directory
out_prt = out_pth / f'part-{uuid4().hex}.csv'
df.to_csv(out_prt)
