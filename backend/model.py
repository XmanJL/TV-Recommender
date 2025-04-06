import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

class RecommenderModel:
    def __init__(self):
        """Initialize the recommender model by loading data and preparing KNN models"""
        # Load preprocessed data
        self.titles = joblib.load("titles.joblib")
        self.titles_transformed = joblib.load("titles_transformed.joblib")
        self.feature_names = list(self.titles_transformed.columns)
        
        # Create two separate KNN models for different functionalities
        # 1. For grouping similar items in existing dataset
        self.content_knn = NearestNeighbors(n_neighbors=10, metric='cosine')
        self.content_knn.fit(self.titles_transformed)
        
        # 2. For making predictions on unseen data (user preferences)
        self.preference_knn = NearestNeighbors(n_neighbors=20, metric='cosine')
        self.preference_knn.fit(self.titles_transformed)
    
    def get_similar_content(self, title_id=None, title_name=None, n_recommendations=10, 
                          filters=None):
        """
        Find similar shows/movies based on an existing title in the dataset.
        
        Parameters:
        - title_id: Index of a show in the dataset
        - title_name: Name of a show in the dataset (alternative to title_id)
        - n_recommendations: Number of recommendations to return
        - filters: Dictionary of filters to apply to recommendations
            - min_year: Minimum release year
            - max_year: Maximum release year
            - min_imdb: Minimum IMDB score
            - platforms: List of platforms to include
            - genres: List of genres to include
            - countries: List of countries to include
            - type: MOVIE or SHOW
            - age_certification: Age rating
            
        Returns:
        - A list of recommended show titles with metadata
        """
        # Handle title name instead of index
        if title_id is None and title_name is not None:
            title_matches = self.titles[self.titles['title'].str.lower() == title_name.lower()]
            if title_matches.empty:
                # Try partial matching
                title_matches = self.titles[self.titles['title'].str.lower().str.contains(title_name.lower())]
                if title_matches.empty:
                    print(f"Title '{title_name}' not found in dataset.")
                    return []
            title_id = title_matches.index[0]
        
        if title_id is None:
            print("Error: Either title_id or title_name must be provided.")
            return []
        
        # Get the feature vector for the selected title
        title_features = self.titles_transformed.iloc[[title_id]]
        
        # Find nearest neighbors - get more than needed to account for filtering
        distances, indices = self.content_knn.kneighbors(
            title_features, 
            n_neighbors=min(n_recommendations*3, len(self.titles_transformed))
        )
        
        # Create a filtered list of recommendations
        recommendations = []
        for i in range(1, len(indices[0])): # Skip the first one (which is the input title itself)
            idx = indices[0][i]
            title_data = self.titles.iloc[idx]
            
            # Apply filters if provided
            if filters:
                # Skip if doesn't meet minimum year
                if 'min_year' in filters and title_data['release_year'] < filters['min_year']:
                    continue
                
                # Skip if exceeds maximum year
                if 'max_year' in filters and title_data['release_year'] > filters['max_year']:
                    continue
                
                # Skip if doesn't meet minimum IMDB score
                if 'min_imdb' in filters and title_data['imdb_score'] < filters['min_imdb']:
                    continue
                
                # Skip if not in requested platforms
                if 'platforms' in filters and hasattr(title_data, 'platform'):
                    if title_data['platform'] not in filters['platforms']:
                        continue
                
                # Skip if type doesn't match (MOVIE or SHOW)
                if 'type' in filters and title_data['type'] != filters['type']:
                    continue
                
                # Skip if age certification doesn't match
                if 'age_certification' in filters and title_data['age_certification'] != filters['age_certification']:
                    continue
                
                # Skip if doesn't have at least one of the requested genres
                if 'genres' in filters:
                    if not any(genre in title_data['genres'] for genre in filters['genres']):
                        continue
                
                # Skip if doesn't have at least one of the requested countries
                if 'countries' in filters:
                    if not any(country in title_data['production_countries'] for country in filters['countries']):
                        continue
            
            # Add to recommendations if it passed all filters
            title_info = {
                'title': title_data['title'],
                'type': title_data['type'],
                'release_year': title_data['release_year'],
                'imdb_score': title_data['imdb_score'],
                'genres': title_data['genres'],
                'production_countries': title_data['production_countries'],
                'age_certification': title_data['age_certification'],
                'similarity': float(1 - distances[0][i])  # Convert distance to similarity score (0-1)
            }
            
            # Add description if available
            if 'description' in title_data:
                title_info['description'] = title_data['description']
                
            # Add platform if available
            if hasattr(title_data, 'platform'):
                title_info['platform'] = title_data['platform']
                
            recommendations.append(title_info)
            
            # Break once we have enough recommendations
            if len(recommendations) >= n_recommendations:
                break
                
        return recommendations
    
    def get_preference_vector(self, preferences):
        """
        Create a user preference vector based on specified preferences.
        
        Parameters:
        - preferences: Dictionary of user preferences
            - genres: List of preferred genres
            - countries: List of preferred countries
            - type: MOVIE or SHOW
            - age_certification: Age certification preference
            
        Returns:
        - A user preference vector
        """
        # Create an empty preference vector
        user_preferences = np.zeros(len(self.feature_names))
        
        # Set features for genres
        if 'genres' in preferences and preferences['genres']:
            for genre in preferences['genres']:
                if genre in self.feature_names:
                    idx = self.feature_names.index(genre)
                    user_preferences[idx] = 1
        
        # Set features for countries
        if 'countries' in preferences and preferences['countries']:
            for country in preferences['countries']:
                if country in self.feature_names:
                    idx = self.feature_names.index(country)
                    user_preferences[idx] = 1
        
        # Set type feature
        if 'type' in preferences and preferences['type']:
            type_upper = preferences['type'].upper()
            if type_upper in self.feature_names:
                idx = self.feature_names.index(type_upper)
                user_preferences[idx] = 1
        
        # Set age certification feature
        if 'age_certification' in preferences and preferences['age_certification']:
            if preferences['age_certification'] in self.feature_names:
                idx = self.feature_names.index(preferences['age_certification'])
                user_preferences[idx] = 1
        
        return user_preferences
    
    def get_preference_recommendations(self, preferences, n_recommendations=10, filters=None):
        """
        Generate recommendations based on user preferences vector (for unseen data).
        
        Parameters:
        - preferences: Dictionary of user preferences
        - n_recommendations: Number of recommendations to return
        - filters: Additional filters to apply
        
        Returns:
        - A list of recommended show titles
        """
        # Create user preference vector
        user_preferences = self.get_preference_vector(preferences)
        
        # If preference vector is empty (all zeros), return random recommendations
        if np.sum(user_preferences) == 0:
            # Get random indices
            random_indices = np.random.choice(
                len(self.titles), 
                min(n_recommendations*3, len(self.titles)), 
                replace=False
            )
            
            # Filter and return results
            return self._filter_and_format_results(random_indices, np.ones(len(random_indices)), filters, n_recommendations)
        
        # Convert to DataFrame with proper column names for KNN
        user_df = pd.DataFrame([user_preferences], columns=self.feature_names)
        
        # Find nearest neighbors
        distances, indices = self.preference_knn.kneighbors(
            user_df, 
            n_neighbors=min(n_recommendations*3, len(self.titles_transformed))
        )
        
        # Filter and return results
        return self._filter_and_format_results(indices[0], distances[0], filters, n_recommendations)
    
    def _filter_and_format_results(self, indices, distances, filters, n_recommendations):
        """
        Helper method to filter and format recommendation results.
        
        Parameters:
        - indices: Array of indices for recommended items
        - distances: Array of distances for recommended items
        - filters: Dictionary of filters to apply
        - n_recommendations: Maximum number of recommendations to return
        
        Returns:
        - Filtered and formatted recommendations
        """
        recommendations = []
        
        for i in range(len(indices)):
            idx = indices[i]
            title_data = self.titles.iloc[idx]
            
            # Apply filters if provided
            if filters:
                # Skip if doesn't meet minimum year
                if 'min_year' in filters and title_data['release_year'] < filters['min_year']:
                    continue
                
                # Skip if exceeds maximum year
                if 'max_year' in filters and title_data['release_year'] > filters['max_year']:
                    continue
                
                # Skip if doesn't meet minimum IMDB score
                if 'min_imdb' in filters and title_data['imdb_score'] < filters['min_imdb']:
                    continue
                
                # Skip if not in requested platforms
                if 'platforms' in filters and hasattr(title_data, 'platform'):
                    if title_data['platform'] not in filters['platforms']:
                        continue
                
                # Skip if type doesn't match (MOVIE or SHOW)
                if 'type' in filters and title_data['type'] != filters['type']:
                    continue
                
                # Skip if age certification doesn't match
                if 'age_certification' in filters and title_data['age_certification'] != filters['age_certification']:
                    continue
                
                # Skip if doesn't have at least one of the requested genres
                if 'genres' in filters:
                    if not any(genre in title_data['genres'] for genre in filters['genres']):
                        continue
                
                # Skip if doesn't have at least one of the requested countries
                if 'countries' in filters:
                    if not any(country in title_data['production_countries'] for country in filters['countries']):
                        continue
            
            # Add to recommendations if it passed all filters
            title_info = {
                'title': title_data['title'],
                'type': title_data['type'],
                'release_year': title_data['release_year'],
                'imdb_score': title_data['imdb_score'],
                'genres': title_data['genres'],
                'production_countries': title_data['production_countries'],
                'age_certification': title_data['age_certification'],
                'similarity': float(1 - distances[i])  # Convert distance to similarity score (0-1)
            }
            
            # Add description if available
            if 'description' in title_data:
                title_info['description'] = title_data['description']
                
            # Add platform if available
            if hasattr(title_data, 'platform'):
                title_info['platform'] = title_data['platform']
                
            recommendations.append(title_info)
            
            # Break once we have enough recommendations
            if len(recommendations) >= n_recommendations:
                break
                
        return recommendations

# Example usage
if __name__ == "__main__":
    # Initialize the model
    model = RecommenderModel()
    
    # Example 1: Get similar shows to an existing title
    similar_shows = model.get_similar_content(
        title_name="Stranger Things",
        filters={
            'genres': ['crime', 'thriller'],
            'min_year': 2015,
            'min_imdb': 7.0,
            'type': 'SHOW'
        }
    )
    
    print("Shows similar to 'Stranger Things':")
    for i, show in enumerate(similar_shows[:5]):
        print(f"{i+1}. {show['title']} ({show['type']}, {show['release_year']}) - IMDB: {show['imdb_score']} - Similarity: {show['similarity']:.2f}")
    
    # Example 2: Get recommendations based on preferences vector
    # This part doesn't work quite well. We should fix it 
    preferences = {
        'genres': ['crime', 'thriller'],
        'countries': ['US'],
        'type': 'MOVIE'
    }
    
    preference_recs = model.get_preference_recommendations(
        preferences=preferences,
        filters={
            'min_year': 2010,
            'min_imdb': 7.0
        }
    )
    
    print("\nRecommendations based on preferences:")
    for i, show in enumerate(preference_recs[:5]):
        print(f"{i+1}. {show['title']} ({show['type']}, {show['release_year']}) - IMDB: {show['imdb_score']} - Similarity: {show['similarity']:.2f}")