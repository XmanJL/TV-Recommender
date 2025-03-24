import joblib
from sklearn.neighbors import NearestNeighbors

class KnnModel:
    # load data and model
    def __init__(self):
        self.titles = joblib.load("titles.joblib")
        self.titles_transformed = joblib.load("titles_transformed.joblib")

    """
    Generate a list of content-based recommendations based on user preferences.

    Optional Parameters:
    - past_movie: a past movie you watched
    - genres: List of preferred genres.
    - countries: List of preferred production countries (e.g., ["US", "GB"]).
    - type: preferred type (e.g. MOVIE or SHOW) 

    Returns:
    - A List of 10 recommended show titles.
    """
    def get_recommendations(self, genres=[], countries=[], type=""):
        titles_transformed = self.titles_transformed.copy()
        try:
            # Filter user preferred genres
            if (genres):
                for genre in genres:
                    titles_transformed = titles_transformed[titles_transformed[genre] == 1]
            # Filter user preferred countries 
            if (countries):
                for country in countries:
                    titles_transformed = titles_transformed[titles_transformed[country] == 1]
            # Filter user preferred countries 
            if (type):
                titles_transformed = titles_transformed[titles_transformed[type.upper()] == 1]
        # handle invalid input parameters
        except: 
            print("Sorry, the genres/countries/type you tried to find does not exist!")
            return []
        
        # Handle empty recommendation dataframe
        if (titles_transformed.empty):
            print("Sorry, no similar titles found, try to broaden your search!")
            return []
        
        # Use KNN with cosine similarity
        # Fits the cosine similarity of the encoded dataframe
        # X = an encoded movie title -> Y = a list of 10 similar movies
        knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
        knn_model.fit(titles_transformed)
        
        # Use the 1st title of recommendation dataframe
        distances, indices = knn_model.kneighbors(X=titles_transformed.iloc[[0]], n_neighbors=10+1) # including neighbors itself

        recommendation = [self.titles.at[ind, 'title'] for ind in indices.flatten()[1:]]
        return recommendation

# Example usage of code
model = KnnModel()
rec = model.get_recommendations(countries=["US"], genres=["crime", "thriller"], type="MOVIE")
print(rec)
