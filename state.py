class FileCollection:
    FILE_NAME = "hash_info.txt"

    def load_folders_hashes(self, file_path: str) -> dict:
        file_map_info = dict()
        with open(f"{file_path}/{FileCollection.FILE_NAME}", "r") as fobj:
            for line in fobj:
                assignment = line.split()
                file_map_info[assignment[0]] = assignment[1]
        return file_map_info

    def save_folders_hases(self, map_info: dict, file_path: str) -> None:
        with open(f"{file_path}/{FileCollection.FILE_NAME}", "w") as fobj:
            for file in map_info:
                fobj.write(f"{file} {map_info[file]}\n")

    def create_file_map(self, file_path: str):
        with open(f"{file_path}/{FileCollection.FILE_NAME}", "w") as _:
            pass
