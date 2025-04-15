import * as ort from "onnxruntime-node"
import path from "path"
import { promises as fs } from "fs"
import { Content, PostInferenceBody, TransformedContentVector } from "@/lib/types";
import { getFeatures } from "@/lib/model";

const modelPath = path.join(process.cwd(), "./model/", "model.onnx");
const titleJsonPath = path.join(process.cwd(), "./model/", "titles.json");
const transformedTitleJsonPath = path.join(process.cwd(), "./model/", "titles_transformed.json");

export async function POST(req: Request) {
    const res: PostInferenceBody = await req.json();
    const titles: Content[] = JSON.parse((await fs.readFile(titleJsonPath, "utf-8")));
    const transformedTitles: TransformedContentVector[] = JSON.parse((await fs.readFile(transformedTitleJsonPath, "utf-8")));
    const { title, titleId, filters } = res;

    const session = await ort.InferenceSession.create(modelPath);
    const data = getFeatures({ title, titleId, content: titles, transformedContent: transformedTitles });
    const inputTensor = new ort.Tensor("float32", new Float32Array(data), [1, data.length]);
    const feeds = { float_input: inputTensor };

    const output = await session.run(feeds);
    const outputTensor = output["index"].data as BigInt64Array;
    const outputArray = Array.from(outputTensor).map((item) => Number(item));
    const outputTitles = outputArray.map((item) => titles[item]).filter((item) => {
        if (filters) {
            const { genres, production_countries, min_release_year, max_release_year, min_imdb_score } = filters;
            const isGenreMatch = genres && genres.length > 0 ? item.genres.some((genre) => genres.includes(genre)) : true;
            const isCountryMatch = production_countries && production_countries.length > 0 ? item.production_countries.some((country) => production_countries.includes(country)) : true;
            const isYearMatch = (min_release_year && max_release_year) ? item.release_year >= min_release_year && item.release_year <= max_release_year : true;
            const isImdbScoreMatch = min_imdb_score ? item.imdb_score >= min_imdb_score : true;
            return isGenreMatch && isCountryMatch && isYearMatch && isImdbScoreMatch;
        }
        return true;
    });


    await session.release();

    return new Response(JSON.stringify({
        data: outputTitles.slice(1),
    }))
}