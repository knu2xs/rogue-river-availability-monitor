from datetime import datetime
from pathlib import Path
from typing import Union
from uuid import uuid4

from bs4 import BeautifulSoup
import pandas as pd
import requests


def get_row_values(tr: BeautifulSoup) -> list:
    """Get values for row in BeautifulSoup object as a list."""
    td_lst = tr.find_all('td')
    td_val_lst = [td.decode_contents() for td in td_lst]
    return td_val_lst


def get_table_values(tbl: BeautifulSoup) -> list:
    """Get the raw values for a table as a list of lists."""
    val_lst = [get_row_values(tr) for tr in tbl.find_all('tr')]
    val_lst = [r for r in val_lst if len(r) == 3]
    val_lst = [r for r in val_lst if r != ['Day', 'Date', 'Spaces']]
    return val_lst


def process_table(tbl: BeautifulSoup) -> pd.DataFrame:
    """Get the contents of a table as a Pandas ``DataFrame``."""
    # get the month the table is for
    mth_str = tbl.find('th').decode_contents()

    # get the values for the table
    row_lst = get_table_values(tbl)

    # get the year based on today's date
    yr = datetime.today().year

    # create a list of pre-prepared lists, tuples of the datetime and availability
    out_lst = [[datetime.strptime(f'{int(r[1]):02d} {mth_str} {yr}', '%d %B %Y').date().isoformat(), r[2]] for r in
               row_lst]

    # create a dataframe from the list of data item pairs
    out_df = pd.DataFrame(out_lst, columns=['launch_date', 'available_user_days'])

    return out_df


def get_rogue_availability() -> pd.DataFrame:
    """Get the availability of Rogue River permits as a Pandas ``DataFrame``."""
    # url to crawl to find availability
    url = "https://www.blm.gov/or/resources/recreation/rogue/rogue_river.php"

    # pull the rogue river availability
    res = requests.get(url)

    if res.status_code != 200:
        raise requests.RequestException(f'Received Status Code: {res.status_code}\n{res.text}')

    # parse the response into a BeautifulSoup object
    soup = BeautifulSoup(res.text, 'html.parser')

    # get a list of BeautifulSoup objects for each month's availablity table
    tbl_lst = [tbl for tbl in soup.find_all('table') if
               tbl.attrs['summary'].startswith("Available Float Space Openings")]

    # create a single Pandas DataFrame availability table
    df = pd.concat([process_table(tbl) for tbl in tbl_lst])

    return df


def save_rogue_availability_local(output_directory: Union[Path, str]) -> Path:
    """Save the current Rogue River availability locally."""
    # ensure the output_directory is a Path object
    if isinstance(output_directory, str):
        output_directory = Path(output_directory)

    # if the destination does not exist, create it
    if not output_directory.exists():
        output_directory.mkdir(parents=True)

    # create a partition name based on the retrieval date
    partition_dir_nm = f"retrieval_datetime={datetime.today().isoformat()}"

    # create the target partition directory path
    out_pth = output_directory / partition_dir_nm

    # create the target partition directory
    if not out_pth.exists():
        out_pth.mkdir(parents=True)

    # get the data
    df = get_rogue_availability()

    # create the full path to save the output file
    out_csv = out_pth / f'part-{uuid4().hex}.csv'

    # save the data
    df.to_csv(out_csv, index=False)

    return out_csv
