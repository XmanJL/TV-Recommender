import * as ort from "onnxruntime-node"
import path from "path"
import { promises as fs } from "fs"
import { Content, TransformedContentVector } from "@/lib/types";
import { getFeatures } from "@/lib/model";

const modelPath = path.join(process.cwd(), "./model/", "model.onnx");
const titleJsonPath = path.join(process.cwd(), "./model/", "titles.json");
const transformedTitleJsonPath = path.join(process.cwd(), "./model/", "titles_transformed.json");

export async function POST(req: Request) {
    const res = await req.json();
    const titles: Content[] = JSON.parse((await fs.readFile(titleJsonPath, "utf-8")));
    const transformedTitles: TransformedContentVector[] = JSON.parse((await fs.readFile(transformedTitleJsonPath, "utf-8")));

    const { title, titleId, filters } = res;

    const session = await ort.InferenceSession.create(modelPath);

    const data = getFeatures({ title, titleId, content: titles, transformedContent: transformedTitles });
    const inputTensor = new ort.Tensor("float32", new Float32Array(data), [1, data.length]);
    const feeds = { float_input: inputTensor };
    const output = await session.run(feeds);
    
    const results = output["index"].data as Float32Array;
    console.log(results);
    console.log(transformedTitles.indexOf(results));

    await session.release();

    return new Response(JSON.stringify({
        message: "Hello from the API!"
    }))
}