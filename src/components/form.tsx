"use client";

import { Content, PostInferenceBody } from "@/lib/types";
import { Autocomplete, Box, Button, ButtonGroup, Container, Divider, Slider, Stack, TextField } from "@mui/material";
import { useCallback, useMemo, useReducer, useState } from "react";
import { MovieCard } from "./movie-card";

type FormProps = {
    content: Content[]
}

export const Form = ({ content }: FormProps) => {
    const [title, setTitle] = useState("");

    let mpaRatings = useMemo(() => Array.from(new Set(content.map((item) => item.age_certification).flat())).sort(), [content]);
    mpaRatings = useMemo(() => mpaRatings.filter((rating) => rating !== "None"), [mpaRatings]);

    const titles = useMemo(() => content.map((item) => item.title).sort(), [content]);
    const countries = useMemo(() => Array.from(new Set(content.map((item) => item.production_countries).flat())).sort(), [content]);
    const genres = useMemo(() => Array.from(new Set(content.map((item) => item.genres).flat())).sort(), [content]);

    const minYear = useMemo(() => Math.min(...content.map((item) => item.release_year)), [content]);
    const maxYear = useMemo(() => Math.max(...content.map((item) => item.release_year)), [content]);
    const [yearRange, setYearRange] = useState<number[]>([minYear, maxYear]);

    const maxImdbScore = useMemo(() => Math.max(...content.map((item) => item.imdb_score)), [content]);
    const [imdbScore, setImdbScore] = useState(0);

    const [results, setResults] = useState<Content[]>([]);

    const [typeFilter, dispatchTypeFilter] = useReducer((state, action) => {
        if (action.toggle === "movies" && state.shows) {
            return {
                "movies": !state.movies,
                "shows": state.shows
            }
        } else if (action.toggle === "shows" && state.movies) {
            return {
                "movies": state.movies,
                "shows": !state.shows
            }
        }

        return state;
    }, { movies: true, shows: false });


    const [countryFilter, dispatchCountryFilter] = useReducer((state, action) => {
        if (action.toggle === "country") {
            const newState = { ...state };
            if (newState[action.country]) {
                delete newState[action.country];
            } else {
                newState[action.country] = true;
            }
            return newState;
        }
        return state;
    }, Object.fromEntries(countries.map(country => [country, false])));

    const [mpaRatingFilter, dispatchMpaRatingFilter] = useReducer((state, action) => {
        if (action.toggle === "rating") {
            const newState = { ...state };
            if (newState[action.rating]) {
                delete newState[action.rating];
            } else {
                newState[action.rating] = true;
            }
            return newState;
        }
        return state;
    }, Object.fromEntries(mpaRatings.map(rating => [rating, false])));


    const [genreFilter, dispatchGenreFilter] = useReducer((state, action) => {
        if (action.toggle === "genre") {
            const newState = { ...state };
            if (newState[action.genre]) {
                delete newState[action.genre];
            } else {
                newState[action.genre] = true;
            }
            return newState;
        }
        return state;
    }, Object.fromEntries(genres.map(genre => [genre, false])));

    const splitGenresIntoChunks = useCallback((chunkSize: number) => {
        const result: string[][] = [];
        for (let i = 0; i < genres.length; i += chunkSize) {
            result.push(genres.slice(i, i + chunkSize));
        }
        return result;
    }, [genres]);

    const handleSubmit = async () => {
        if (!title) {
            alert("Please enter a title");
            return;
        }

        const data: PostInferenceBody = {
            title: title, filters: {
                genres: Object.keys(genreFilter).filter((key) => genreFilter[key]),
                production_countries: Object.keys(countryFilter).filter((key) => countryFilter[key]),
                min_release_year: yearRange[0],
                max_release_year: yearRange[1],
                min_imdb_score: imdbScore,
                type: typeFilter.movies ? "MOVIES" : "SHOWS"
            }
        };

        console.log(data);

        const res = await fetch("/api/model/inference", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        const json: Content[] = (await res.json()).data;
        if (res.status !== 200) {
            alert("Error: " + json);
            return;
        }
        setResults(json);
    }

    return <Container className="bg-slate-100">
        <Stack spacing={2}>
            <span className="font-semibold">Search for a show or movie:</span>
            <span className="flex flex-row gap-x-5">
                <Autocomplete onChange={(e, value) => setTitle(value || "")} value={title} selectOnFocus handleHomeEndKeys fullWidth size="small" options={titles} freeSolo renderInput={(params) => <TextField {...params} />} />
                <Button variant="contained" onClick={handleSubmit}>Search</Button>
            </span>
            <h2 className="font-semibold">Filter Results</h2>
            <Stack spacing={1}>
                <label>Content Type</label>
                <Box>
                    <ButtonGroup variant="contained">
                        <Button onClick={() => dispatchTypeFilter({ toggle: "movies" })} variant={typeFilter.movies ? "contained" : "outlined"}>Movies</Button>
                        <Button onClick={() => dispatchTypeFilter({ toggle: "shows" })} variant={typeFilter.shows ? "contained" : "outlined"}>Shows</Button>
                    </ButtonGroup>
                </Box>
            </Stack>
            <Stack spacing={1}>
                <label>Genres</label>
                <Box>
                    {splitGenresIntoChunks(5).map((chunk, index) => (
                        <ButtonGroup key={index} variant="contained">
                            {chunk.map((genre) => (
                                <Button key={genre} onClick={() => dispatchGenreFilter({ toggle: "genre", genre })} variant={genreFilter[genre] ? "contained" : "outlined"}>{genre}</Button>
                            ))}
                        </ButtonGroup>
                    ))
                    }
                </Box>
            </Stack>
            <Stack spacing={1}>
                <label>Production Countries</label>
                <Box>
                    <Autocomplete size="small" fullWidth={false} multiple options={countries} renderInput={(params) => <TextField onChange={() => dispatchCountryFilter({ "toggle": "country", country: countries[countries.indexOf(params.id)] })} {...params} />} />
                </Box>
            </Stack>
            <Stack spacing={1}>
                <label>Age Ratings</label>
                <Box>
                    <ButtonGroup variant="contained">
                        {mpaRatings.map((rating) => (
                            <Button key={rating} onClick={() => dispatchMpaRatingFilter({ toggle: "rating", rating })} variant={mpaRatingFilter[rating] ? "contained" : "outlined"}>{rating}</Button>
                        ))}
                    </ButtonGroup>
                </Box>
            </Stack>
            <Stack spacing={1}>
                <label>Release Year</label>
                <Box className="px-3">
                    <Slider valueLabelDisplay="auto" step={1} disableSwap value={yearRange} min={minYear} max={maxYear} onChange={(e, value) => setYearRange(value)} />
                </Box>
            </Stack>
            <Stack spacing={1}>
                <label>IMDB Score Threshold</label>
                <Box className="px-3">
                    <Slider valueLabelDisplay="auto" value={imdbScore} step={0.5} disableSwap min={0} max={maxImdbScore} onChange={(e, value) => setImdbScore(value)} />
                </Box>
            </Stack>
        </Stack>
        {results.length > 0 &&
            <Stack spacing={2}>
                <Divider className="my-5" />
                <h2 className="font-semibold">Results</h2>
                {results.map((result, idx) => <MovieCard key={idx} {...result} />)}
            </Stack>
        }
    </Container>
}