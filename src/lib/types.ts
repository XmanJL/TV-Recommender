export type Content = {
    title: string;
    type: string;
    release_year: number;
    genres: string[];
    production_countries: string[];
    imdb_score: number;
    age_certification: string;
}

export type TransformedContentVector = {
    [key: string]: number
}

export type GetFeaturesParams = {
    title?: string;
    titleId?: number;
    content: Content[];
    transformedContent: TransformedContentVector[];
}

export type PostInferenceBody = {
    title?: string;
    titleId?: number;
    filters?: {
        type: "SHOWS" | "MOVIES";
        genres?: string[];
        production_countries?: string[];
        min_release_year?: number;
        max_release_year?: number;
        min_imdb_score?: number;
    }
}

export type PostInferenceResponse = {
    data?: Content[];
}