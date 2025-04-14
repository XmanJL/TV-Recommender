export type Content = {
    title: string;
    type: string;
    release_year: number;
    genres: string[];
    production_countries: string[];
    imdb_score: number;
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