import os
import pandas as pd
from abc import ABC, abstractmethod
from unipath import Path


class Importer(ABC):
    """ Parent class for Importers """

    @abstractmethod
    def load_data(self, path, filename):
        with open(os.path.join(path, filename)) as f:
            data = pd.read_csv(f)
        
        return data

    @abstractmethod
    def form_dir_path(self, dir_name):
        
        project_dir = Path(__file__).parent.parent
        
        return os.path.join(project_dir, str(dir_name))
