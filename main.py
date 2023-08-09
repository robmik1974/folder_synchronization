import sys
import os
import shutil
import time
from filehash import FileHash
from state import FileCollection
from logevent import create_log


def check_argument_list() -> bool:
    return False if len(sys.argv) != 5 else True


def create_files_map_info(file_hash_path: str) -> dict:
    return FileCollection().load_folders_hashes(file_path=file_hash_path)


def create_new_hash(
        file_hasher: FileHash, file_name: str,
        file_hash_map: dict, file_hash: dict
) -> tuple:
    fhash = file_hasher.hash_file(file_name)
    file_hash_map[file_name] = fhash
    file_hash[file_name] = file_hash_map[file_name]
    return file_hash, file_hash_map


def prepare_folder_structure(
        destination_file: str, replica_folder: str
) -> None:
    replica_folder_name = replica_folder.split("/")[-1]
    root_folder = "".join(replica_folder.split("/")[-2:-1])
    path = destination_file.split(root_folder)[1]
    folder_structure = path.split("/")[1:-1]
    for folder in folder_structure:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
        finally:
            os.chdir(folder)
    os.chdir(destination_file.split(replica_folder_name)[0])


def copy_files(source_file: str,
               destination_file: str,
               replica_folder: str
) -> None:
    prepare_folder_structure(
        destination_file=destination_file, replica_folder=replica_folder
    )
    shutil.copy(source_file, destination_file)


def remove_file(
        replica_folder: str, file_path: str, source_folder: str
) -> None:
    source_folder_name = source_folder.split("/")[-1]
    source_path = file_path.split(source_folder_name)[-1]
    replica_path = replica_folder + source_path
    os.remove(replica_path)


def manage_existing_files(
        file_hasher: FileHash, file_hash_map: dict, file_hash: dict,
        file_hash_path: str, source_folder: str, replica_folder: str
) -> None:
    source_folder_name = source_folder.split("/")[-1]
    for dir_path, _, files in os.walk(source_folder):
        for file in files:
            with open(f"{dir_path}/{file}", "rb") as fobj:
                if fobj.name in file_hash_map.keys():
                    if file_hasher.hash_file(fobj.name) == file_hash_map[fobj.name]:
                        file_hash[fobj.name] = file_hash_map[fobj.name]
                    else:
                        file_hash, file_hash_map = create_new_hash(
                            file_hasher, fobj.name, file_hash_map, file_hash
                        )
                        copy_files(
                            fobj.name,
                            f"{replica_folder}{(fobj.name).split(source_folder_name)[-1]}",
                            replica_folder=replica_folder
                        )
                        log.info(f"Coping file that was chanaged: '{fobj.name}' to replica folder ")
                        FileCollection().save_folders_hases(
                            map_info=file_hash_map, file_path=file_hash_path
                        )


def manage_new_files(
        file_hasher: FileHash, file_hash_map: dict, file_hash: dict,
        file_hash_path: str, source_folder: str, replica_folder: str
) -> None:
    source_folder_name = source_folder.split("/")[-1]
    for dir_path, _, files in os.walk(source_folder):
        for file in files:
            with open(f"{dir_path}/{file}", "rb") as fobj:
                if fobj.name not in file_hash_map.keys():
                    file_hash, file_hash_map = create_new_hash(
                        file_hasher, fobj.name, file_hash_map, file_hash
                    )
                    copy_files(
                        fobj.name,
                        f"{replica_folder}{(fobj.name).split(source_folder_name)[-1]}",
                        replica_folder=replica_folder
                    )
                    log.info(f"Coping file that was created: '{fobj.name}' to replica folder")
                    FileCollection().save_folders_hases(
                        map_info=file_hash_map, file_path=file_hash_path
                    )


def manage_deleted_files(
        file_hasher: FileHash, file_hash_map: dict, file_hash: dict,
        file_hash_path: str, source_folder: str, replica_folder: str
) -> None:
    hash_map_keys = set(file_hash_map.keys())
    file_names = set(file_hash.keys())
    for file in hash_map_keys.difference(file_names):
        remove_file(
            replica_folder=replica_folder,
            file_path=file,
            source_folder=source_folder
        )
        log.info(f"Removing file that was deleted: '{file}' from replica folder")
        FileCollection().save_folders_hases(
            map_info=file_hash,
            file_path=file_hash_path
            )


def synchronize_empty_folders(source_folder: str, replica_folder: str) -> None:
    source_folder_name = source_folder.split("/")[-1]
    for dir_path, dirs, files in os.walk(source_folder):
        path = dir_path.split(source_folder_name)[-1]
        if not os.path.exists(f"{replica_folder}{path}"):
            os.mkdir(f"{replica_folder}{path}")

    replica_folder_name = replica_folder.split("/")[-1]
    for dir_path, _, _ in os.walk(replica_folder, topdown=False):
        path = dir_path.split(replica_folder_name)[-1]
        if not os.path.exists(f"{source_folder}{path}"):
            os.rmdir(f"{replica_folder}{path}")


def main():
    file_hasher = FileHash("md5")
    file_hash_path = ""
    source_folder = ""
    replica_folder = ""
    source_folder = f"{os.getcwd()}/{sys.argv[1]}"
    replica_folder = f"{os.getcwd()}/{sys.argv[2]}"

    try:
        os.mkdir(source_folder)
    except FileExistsError:
        pass
    try:
        os.mkdir(replica_folder)
    except FileExistsError:
        pass

    file_hash_path = os.getcwd()

    while True:
        file_hash_map = dict()
        file_hash = dict()

        try:
            file_hash_map = create_files_map_info(
                file_hash_path=file_hash_path
                )
        except FileNotFoundError:
            FileCollection().create_file_map(file_path=file_hash_path)

        manage_existing_files(
            file_hasher=file_hasher, file_hash_map=file_hash_map,
            file_hash=file_hash, file_hash_path=file_hash_path,
            source_folder=source_folder, replica_folder=replica_folder
            )

        manage_new_files(
            file_hasher=file_hasher, file_hash_map=file_hash_map,
            file_hash=file_hash, file_hash_path=file_hash_path,
            source_folder=source_folder, replica_folder=replica_folder
            )

        manage_deleted_files(
            file_hasher=file_hasher, file_hash_map=file_hash_map,
            file_hash=file_hash, file_hash_path=file_hash_path,
            source_folder=source_folder, replica_folder=replica_folder
            )

        synchronize_empty_folders(
            source_folder=source_folder, replica_folder=replica_folder
            )

        time.sleep(int(sys.argv[3]))


if __name__ == "__main__":
    if not check_argument_list:
        sys.exit(-1)
    log = create_log(sys.argv[4])
    main()
