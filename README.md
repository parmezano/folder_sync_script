# Folder Synchronization Script

This Python script synchronizes two folders — **source** and **replica** — ensuring that the replica is always a full, identical copy of the source.  
Synchronization is **one-way**: any changes made in the source folder are mirrored in the replica, but not vice versa.

The program supports **periodic synchronization**, detailed **logging**, and automatic **file and folder deletion** in the replica if they no longer exist in the source.

---

## Requirements

- Python 3.8 or higher
- Standard libraries only (no external dependencies):  
  `os`, `sys`, `time`, `logging`, `hashlib`, `shutil`, `datetime`

---

## Usage

Run the script directly from the command line with the following arguments **in this exact order**:

```bash
python main.py <source_folder> <replica_folder> <sync_interval_seconds> <sync_count> <log_file_path>
