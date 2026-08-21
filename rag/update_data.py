
# update_data.py
import sys

from utils.data_loader import build_dataset

query = " ".join(sys.argv[1:]) or None
build_dataset(query=query)
