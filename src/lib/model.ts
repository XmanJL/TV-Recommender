import { GetFeaturesParams } from "./types";

export const getFeatures = ({ title, titleId, content, transformedContent }: GetFeaturesParams) => {
    if (!titleId) {
        if (!title) {
            throw new Error("Either titleId or title must be provided");
        }

        // search for an exact match first
        let match = content.find((item) => item.title.toLowerCase() === title.toLowerCase());
        if (!match) {
            // if no exact match, search for a partial match
            match = content.find((item) => item.title.toLowerCase().includes(title.toLowerCase()));
            if (!match) {
                console.warn(`No match found for title: ${title}`);
                return [];
            }
        }

        titleId = content.indexOf(match);
    }

    return Object.values(transformedContent[titleId]);
}
