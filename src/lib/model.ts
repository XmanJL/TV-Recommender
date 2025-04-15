import { GetFeaturesParams } from "./types";

/**
 * Retrieves feature values for a given title or titleId from the transformed content.
 * 
 * @param params - The parameters for getting features
 * @param params.title - The title of the content to search for
 * @param params.titleId - The index of the content in the array
 * @param params.content - Array of content items with title property
 * @param params.transformedContent - Array of transformed content features
 * 
 * @returns Array of feature values for the matched content
 * @throws {Error} When neither titleId nor title is provided
 */
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
