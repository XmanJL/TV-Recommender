import { Form } from "@/components/form";
import { Content } from "@/lib/types";
import { Box, Container, Stack } from "@mui/material";
import { promises as fs } from "fs"
import path from "path";

export default async function Home() {
  const titleJsonPath = path.join(process.cwd(), "./model/", "titles.json");
  const titles: Content[] = JSON.parse(await fs.readFile(titleJsonPath, "utf-8"));

  return (
    <Stack spacing={2}>
      <Box className="text-center bg-slate-700 text-white rounded-xl p-5">
        <Stack spacing={2}>
          <h1 className="text-3xl">Discover Your Next Favorite Show</h1>
          <p className="text-xl">Find similar shows and hidden gems across Netflix, Amazon Prime, and Apple TV+</p>
        </Stack>
      </Box>
      <Box>
        <Container className="bg-blue-400 py-2">
          <span className="text-white text-2xl">Find Similar Shows</span>
        </Container>
        <Form content={titles} />
      </Box>
    </Stack>
  );
}
