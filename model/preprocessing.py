import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler, MultiLabelBinarizer
import joblib

class Preprocessing:

    def __init__(self):
        self.amazon_titles = pd.read_csv("./dataset/amazonPrime/titles.csv")
        self.appletv_titles = pd.read_csv("./dataset/appletv/titles.csv")
        self.netflix_titles = pd.read_csv("./dataset/netflix/titles.csv")
    
    # Preprocess data and save it in .joblib
    def preprocess_data(self):
        # Create an informative dataframe of all the tv shows & movies
        titles = pd.concat([self.amazon_titles, self.appletv_titles, self.netflix_titles], axis=0)
        titles = titles.copy()  # Ensure dataframe is a copy, not a view, to avoid SettingWithCopyWarning
        titles = titles.drop_duplicates(subset=['title'])

        # Clean data
        titles["age_certification"] = titles["age_certification"].fillna("None")
        unnecessary_columns = ["id", "imdb_votes", "tmdb_popularity", "seasons", "imdb_id", "description", "runtime", "tmdb_score"]
        titles = titles.drop(columns=unnecessary_columns)
        titles = titles.dropna()

        # Reset index
        titles = titles.reset_index(drop=True)

        # Convert list-based columns
        titles['genres'] = titles['genres'].apply(eval)  # Convert string to list
        titles['production_countries'] = titles['production_countries'].apply(eval)

        mlb_genres = MultiLabelBinarizer()
        genres_encoded = pd.DataFrame(mlb_genres.fit_transform(titles['genres']), columns=mlb_genres.classes_)

        mlb_countries = MultiLabelBinarizer()
        countries_encoded = pd.DataFrame(mlb_countries.fit_transform(titles['production_countries']), columns=mlb_countries.classes_)

        # Convert Other columns 

        # Apply One-Hot Encoding to 'type' & age_certification
        onehot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        type_encoded = pd.DataFrame(onehot_encoder.fit_transform(titles[['type']]), columns=onehot_encoder.get_feature_names_out(['type']))
        age_encoded = pd.DataFrame(onehot_encoder.fit_transform(titles[['age_certification']]), columns=onehot_encoder.get_feature_names_out(['age_certification']))
        
        # Remove 'type_' prefix
        type_encoded.columns = type_encoded.columns.str.replace('type_', '', regex=False)
        age_encoded.columns = age_encoded.columns.str.replace('age_certification_', '', regex=False)

        # Apply Min-Max Scaling to numerical columns
        scaler = MinMaxScaler()
        numerical_features = ['release_year', 'imdb_score']
        numerical_encoded = pd.DataFrame(scaler.fit_transform(titles[numerical_features]), columns=numerical_features)

        # Combine encoded data
        titles_transformed = pd.concat([genres_encoded, countries_encoded, type_encoded, age_encoded, numerical_encoded], axis=1)
        
        # Make & Save the preprocessed data
        joblib.dump(titles, "titles.joblib")
        joblib.dump(titles_transformed, "titles_transformed.joblib")
        print("Data saved successfully!")

# Example usage of loading data    
preprocessor = Preprocessing()
preprocessor.preprocess_data()
