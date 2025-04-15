import { Content } from "@/lib/types";
import { Card, CardContent } from "@mui/material";

export const MovieCard = ({ title, type, release_year, genres, production_countries, imdb_score, age_certification }: Content) => {
    return <Card>
        <CardContent>
            <h2 className="text-2xl">{title}</h2>
            <p className="text-sm">{type}</p>
            <p className="text-sm">{release_year}</p>
            <p className="text-sm">{genres.join(", ")}</p>
            <p className="text-sm">{production_countries.join(", ")}</p>
            <p className="text-sm">IMDB Score: {imdb_score}</p>
            <p className="text-sm">Age Certification: {age_certification}</p>
        </CardContent>
    </Card>
}