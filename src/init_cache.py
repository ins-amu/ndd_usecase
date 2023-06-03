import pooch
import os
import shutil

project_root = os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
)

def init_dvc_cache():
    pooch.retrieve(
        url='https://data-proxy.ebrains.eu/api/permalinks/e162048c-b328-4276-a8ce-d45ad412b0c1',
        known_hash='9f2054c4240fd3c5fa8ef79571f51236c64e7029e278835edfbc19dfc2a18df7',
        downloader=pooch.HTTPDownloader(),
        processor=pooch.Untar(extract_dir=project_root)
    )

if __name__ == '__main__':
    init_dvc_cache()
