import * as ort from "onnxruntime-node"
import path from "path"

export async function GET() {
    const modelPath = path.join(process.cwd(), "../model/", "model.onnx")
    const session = await ort.InferenceSession.create(modelPath);


    await session.release();

    return new Response(JSON.stringify({
        message: "Hello from the API!"
    }))
}