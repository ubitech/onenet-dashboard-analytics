import logging
import pickle
import base64
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class KMeansClustering():
    """
    Class for creating and training a KMeans clustering model (object)
    """

    def __init__(self, cluster_num, random_state=0):
        """
        :param `int` cluster_num: The number of clusters
        :param `int` random_state: The random state variable for deterministic randomness
        """
        self.kmeans = KMeans(n_clusters=cluster_num, random_state=random_state)

    def run_clustering(self, df):
        """
        Fitting the clustring model with given dataframe and store cluster centers and labels

        :param `Dataframe` df: The pandas Dataframe to be used for training
        """
        self.kmeans.fit(df)
        self.centers = self.kmeans.cluster_centers_
        self.cluster_labels = self.kmeans.labels_

    def get_cluster_labels(self):
        """
        Return cluster labels
        """
        return self.cluster_labels

    def get_cluster_centers(self):
        """
        Return cluster centers
        """
        return self.centers

class IFClassification():
    """
    Class for creating and training an Isolation Forest classification model (object)
    """

    def __init__(self, random_state=0):
        """
        :param `int` random_state: The random state variable for deterministic randomness
        """
        self.random_state = random_state
        self.ifc_model = IsolationForest(random_state=self.random_state)

    def train_classifier(self, df):
        """
        Train the Isolation Forest classifier by fitting the model on the given dataframe

        :param `Dataframe` df: The dataframe with the features
        """
        self.ifc_model.fit(df.to_numpy())

    def get_predictions(self, df_X):
        """
        Get predictions for the given dataframe using the trained model

        :param `Datafrane` df_X: The dataframe for which to predict labels

        :return `nd.array`: The predicted labels for the df_X samples
        """
        y_pred = self.ifc_model.predict(df_X.to_numpy())

        return y_pred

    def get_ifc_model(self):
        """
        Get the Isolation Forest classifier. (Use it after the model is trained or loaded)
        """
        return self.ifc_model

    def get_ifc_model_base64(self):
        """
        Get the binary form of the Isolation Forest classifier encoded in base64 string

        :return `str` model_64encoded_ascii: The base64 binary as string
        """
        model_in_bytes = pickle.dumps(self.ifc_model)

        model_64encoded = base64.b64encode(model_in_bytes)

        model_64encoded_ascii = model_64encoded.decode('ascii')

        return model_64encoded_ascii

    def get_ifc_model_from_base64(self, model_64encoded_ascii):
        """
        Converts and saves a base64 encoded Isolation Forest Classifier into a usable model

        :param `str` model_64encoded_ascii: The base64 binary form of model as string
        """

        # there is no need to encode firstly from ascii_base64 to bytes_base64 and then to bytes, since
        # the b64decode function can also decode an ascii string
        model_decoded_in_bytes = base64.b64decode(model_64encoded_ascii)

        model_loaded = pickle.loads(model_decoded_in_bytes)

        self.ifc_model = model_loaded