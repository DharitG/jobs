import { useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import type { TextItem } from 'pdfjs-dist/types/src/display/api'; // Import type

// Import worker explicitly (adjust path if using a different setup/bundler)
// Option 1: Direct import (might need specific bundler config)
import 'pdfjs-dist/build/pdf.worker.min.mjs'; // Side effect import

// Option 2: Set worker source path (often more reliable)
// pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs'; // Needs worker file in public folder
// Alternative path if using node_modules directly (less common for frontend)
pdfjsLib.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;


// Define the structure we expect for backend (matches Pydantic schema)
interface PdfTextItemBackend {
  text: string;
  fontName: string;
  width: number;
  height: number;
  x: number; // transform[4]
  y: number; // transform[5]
  hasEOL: boolean; // Simplified, need logic if required
}

interface UsePdfParserReturn {
  parsePdf: (file: File) => Promise<PdfTextItemBackend[]>;
  isLoading: boolean;
  error: string | null;
}

export function usePdfParser(): UsePdfParserReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parsePdf = async (file: File): Promise<PdfTextItemBackend[]> => {
    setIsLoading(true);
    setError(null);

    if (!file || file.type !== 'application/pdf') {
      setError('Invalid file type. Please upload a PDF.');
      setIsLoading(false);
      return [];
    }

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const numPages = pdf.numPages;
      const allTextItems: PdfTextItemBackend[] = [];

      console.log(`Parsing PDF: ${file.name}, Pages: ${numPages}`);

      for (let i = 1; i <= numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();

        textContent.items.forEach((item) => {
          // Check if item is a TextItem (it has 'str' property)
          if ('str' in item) {
             const textItem = item as TextItem; // Type assertion
             // Basic EOL detection (very simplistic)
             const hasEOL = textItem.hasEOL || textItem.str.endsWith('\n');

             allTextItems.push({
                 text: textItem.str,
                 fontName: textItem.fontName,
                 width: textItem.width,
                 height: textItem.height,
                 x: textItem.transform[4], // X coordinate
                 y: textItem.transform[5], // Y coordinate
                 hasEOL: hasEOL, // Simple EOL check
             });
          }
        });
         console.log(`Parsed page ${i}`);
         // Clean up page resources if needed (optional for performance)
         page.cleanup();
      }

       console.log(`PDF Parsing complete. Extracted ${allTextItems.length} text items.`);
       return allTextItems;

    } catch (err) {
      console.error('Error parsing PDF:', err);
      const message = err instanceof Error ? err.message : String(err);
      setError(`Error parsing PDF: ${message}`);
      return []; // Return empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  return { parsePdf, isLoading, error };
}