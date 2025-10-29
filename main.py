import os, sys, time, logging, hashlib
from shutil import copy, copy2
from datetime import datetime


def set_logging(log_file_path):
    logging.basicConfig(level=logging.INFO,
                        filename=log_file_path,
                        filemode="w",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(console_handler)


def calculate_first_file_hash(src_dir_path):
    buffer_size = 65536
    for dirpath, dirs, files in os.walk(src_dir_path):
        for file_name in files:
            file_path = os.path.join(dirpath, file_name)
            md5 = hashlib.md5()
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        data = f.read(buffer_size)
                        if not data:
                            break
                        md5.update(data)
                file_hash = md5.hexdigest()
                logging.info(f"MD5 of first file found ({file_path}): {file_hash}")
            except Exception as e:
                logging.error(f"Failed to calculate MD5 for {file_path}: {e}")
            return


def copy_file(src_file_path, dst_file_path):
    try:
        copy2(src_file_path, dst_file_path)
        logging.info(f'File copied with metadata: {src_file_path}')
    except Exception as e:
        logging.error(f'Failed to copy with metadata {src_file_path}: {e}')
        copy(src_file_path, dst_file_path)
        logging.info(f'File copied without metadata: {src_file_path}')


def ensure_folder_exists(dst_dir_path):
    if not os.path.exists(dst_dir_path):
        dst_dir_path = os.path.abspath(dst_dir_path)
        os.makedirs(dst_dir_path)
        logging.info(f'Created directory: {dst_dir_path}')


def sync_file(dst_dir_path, dst_file_path, src_file_path):
    if not os.path.exists(dst_file_path):
        try:
            copy_file(src_file_path, dst_file_path)
        except Exception as e:
            logging.error(f'Copy failed for {src_file_path}: {e}')
    else:
        if datetime.fromtimestamp(os.path.getmtime(src_file_path)) != \
                datetime.fromtimestamp(os.path.getmtime(dst_file_path)):
            try:
                os.remove(dst_file_path)
                logging.info(f'Removed outdated file: {dst_file_path}')
                copy_file(src_file_path, dst_dir_path)
            except Exception as e:
                logging.error(f'Failed to update file {dst_file_path}: {e}')


def remove_extra_items(src_dir_path, dst_dir_path):
    for entry_name in os.listdir(dst_dir_path):
        dst_entry_path = os.path.join(dst_dir_path, entry_name)
        src_entry_path = os.path.join(src_dir_path, entry_name)

        if not os.path.exists(src_entry_path):
            try:
                if os.path.isdir(dst_entry_path):
                    remove_extra_items(src_entry_path, dst_entry_path)
                    os.rmdir(dst_entry_path)
                    logging.info(f'Removed extra directory: {dst_entry_path}')
                else:
                    os.remove(dst_entry_path)
                    logging.info(f'Removed extra file: {dst_entry_path}')
            except Exception as e:
                logging.error(f'Failed to remove {dst_entry_path}: {e}')
        elif os.path.isdir(dst_entry_path):
            remove_extra_items(src_entry_path, dst_entry_path)


def sync_directories(src_dir_path, dst_dir_path):
    if not os.path.exists(dst_dir_path):
        os.mkdir(dst_dir_path)
        logging.info(f'Created directory: {dst_dir_path}')

    for entry_name in os.listdir(src_dir_path):
        src_entry_path = os.path.join(src_dir_path, entry_name)
        dst_entry_path = os.path.join(dst_dir_path, entry_name)

        if os.path.isdir(src_entry_path):
            ensure_folder_exists(dst_entry_path)
            sync_directories(src_entry_path, dst_entry_path)
        elif os.path.isfile(src_entry_path):
            sync_file(dst_dir_path, dst_entry_path, src_entry_path)

    remove_extra_items(src_dir_path, dst_dir_path)


def main():
    src_dir_path, dst_dir_path, sync_interval_sec, sync_count, log_file_path = sys.argv[1:6]
    set_logging(log_file_path)
    logging.error(f'{src_dir_path}, {dst_dir_path}, {sync_interval_sec}, {sync_count}, {log_file_path}')
    if len(sys.argv) > 6:
        logging.error(f'Invalid argument count: {sys.argv}')
        raise Exception("Incorrect amount of arguments")



    for sync_number in range(1, int(sync_count) + 1):
        if os.path.exists(src_dir_path):
            calculate_first_file_hash(src_dir_path)
            logging.info(f'--- Synchronization {sync_number} started ---')
            sync_directories(src_dir_path, dst_dir_path)
            logging.info(f'--- Synchronization {sync_number} finished ---')
        else:
            logging.error(f'Source folder does not exists - {src_dir_path}')

        if sync_number < int(sync_count):
                logging.info(f'Waiting {sync_interval_sec} seconds before next sync')
                time.sleep(float(sync_interval_sec))

if __name__ == '__main__':
    main()