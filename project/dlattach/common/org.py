import os
import shutil
import logging

DIRECTORIES = {
    "html":        [".html5", ".html", ".htm", ".xhtml"],
    "markup":      [".md"],
    "images":      [".jpeg", ".jpg", ".tiff", ".gif", ".bmp", ".png", ".bpg", "svg", ".heif", ".psd"],
    "videos":      [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mng", ".qt", ".mpg", ".mpeg", ".3gp", ".mkv"],
    "documents":   [".oxps", ".epub", ".pages", ".docx", ".doc", ".fdf", ".ods", ".odt", ".pwi", ".xsn", ".xps", ".dotx", ".docm", ".dox", ".rvg", ".rtf", ".rtfd", ".wpd", ".xls", ".xlsx", ".ppt", "pptx", ".md", ".pages", ".numbers"],
    "archives":    [".a", ".ar", ".arh", ".tar", ".tar.bz2", ".tar.gz", ".cpio", ".tar", ".gz", ".rz", ".7z", ".rar", ".xar", ".zip", ".xz", ".pkg", ".deb", ".rpm"],
    "diskimage":   [".iso", ".img", ".vcd", ".dmg"],
    "audio":       [".aac", ".aa", ".aac", ".dvf", ".m4a", ".m4b", ".m4p", ".mp3", ".msv", "ogg", "oga", ".raw", ".vox", ".wav", ".wma"],
    "text":        [".txt", ".in", ".out", ".csv", ".log"],
    "powershell":  [".ps1", ".psm1", ".psd1"],
    "pdf":         [".pdf"],
    "python":      [".py", ".pyi", ".pyc"],
    "xml":         [".xml", ".fxml"],
    "executable":  [".exe", ".run"],
    "shell":       [".sh"],
    "database":    [".db", ".sql"],
    "c#":          [".cs"],
    "c++":         [".cpp"],
    "c":           [".c"],
    "go":          [".go"],
    "yaml":        [".yaml"],
    "json":        [".json"],
    "asp classic": [".asp"],
    "asp_net":     [".aspx", ".axd", ".asx", ".asmx", ".ashx"],
    "css":         [".css"],
    "coldfusion":  [".cfm"],
    "erlang":      [".yaws"],
    "flash":       [".swf"],
    "java":        [".jar", ".java", ".jsp", ".jspx", ".wss", ".do", ".action"],
    "kotlin":      [".kt", ".kts", ".ktm"],
    "javascript":  [".js"],
    "typescript":  [".ts"],
    "rust":        [".rs", ".rlib"],
    "toml":        [".toml"],
    "travis":      [".travis"],
    "perl":        [".pl"],
    "php":         [".php", ".php4", ".php3", ".phtml"],
    "ruby":        [".rb", ".rhtml"],
    "ssi":         [".shtml"],
    "xml":         [".xml", ".rss", ".svg"],
    "apps":        [".app", ".ipa", ".apk"],
    "links":       [".webloc", ".lnk"]
}

FILE_FORMATS = {file_format: directory
                for directory, file_formats in DIRECTORIES.items()
                for file_format in file_formats
}


def by_type(src_dir, dest_dir):
    """
    Organise files into directories by extension:
    Creates directories by file type. These directories will be created under org-files root
    :param src_dir: Root directory where the files to treat are present
    :param dest_dir: Destination directory where the files will be moved
    :return: Error code 0 = Ok, otherwise Nok
    """

    # Set org-files directory
    org_dir = os.path.join(dest_dir, 'org-files')

    logging.basicConfig(filename=os.path.join(dest_dir, 'org.log'), level=logging.INFO)
    logging.info(f'Set-up - Source directory is {src_dir}')
    logging.info(f'Set-up - Destination directory is {dest_dir}')

    try:
        for entry in os.scandir(path=src_dir):
            if entry.is_dir():
                pass

            elif entry.is_file():
                file_path = entry.path
                file_format = file_path.suffix.lower()

                # Move file to corresponding destination directory
                if file_format in FILE_FORMATS:
                    directory_path = os.path.join(org_dir, FILE_FORMATS[file_format])
                    if not os.path.isdir(directory_path):
                        os.mkdir(directory_path)

                    shutil.move(src=file_path, dst=directory_path)
                    logging.info(f'file {os.path.basename(file_path)} successfully moved to {directory_path} from {file_path}')

                # Move file to corresponding other-files directory
                else:
                    oth_path = os.path.join(org_dir, 'other-files')
                    if not os.path.isdir(oth_path):
                        os.mkdir(oth_path)

                    shutil.move(src=file_path, dst=oth_path)
                    logging.warning(f'file {os.path.basename(file_path)} successfully moved to {oth_path} from {file_path}.')

        # Clean empty directories
        try:
            os.rmdir(path=src_dir)
        except OSError as e:
            logging.error(e)
            logging.error("Directories can not be removed")
            return -1

        return 0

    except:
        return -1

    # Debug purposes
# if __name__ == "__main__":
#     byType(dest_dir='', src_dir= '')