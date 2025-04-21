'use client';

'use client';

import React, { useState, useCallback } from 'react'; // Added useCallback
import type { ChangeEvent } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from './ui/button';
import { Input } from './ui/input'; // Assuming shadcn/ui input is here
import { Label } from './ui/label'; // Assuming shadcn/ui label is here
import { env } from '../env.js';
import { usePdfParser } from '~/hooks/usePdfParser'; // Added parser hook
import { api } from '~/trpc/react'; // Added tRPC hook
import { Loader2 } from 'lucide-react'; // Added loader icon

export function ProfileImport() {
  const { getAccessTokenSilently } = useAuth0(); // Get token function
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false); // Combined loading state

  // Hooks
  const { parsePdf, isLoading: isParsing, error: parseError } = usePdfParser();
  const tailorMutation = api.resume.parseAndTailor.useMutation();

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
        setMessage(''); // Clear previous messages
      } else {
        setSelectedFile(null);
        setMessage('Please select a PDF file.');
      }
    } else {
      setSelectedFile(null);
    }
  };

  const handleProcessResume = useCallback(async () => {
    if (!selectedFile) {
      setMessage('Please select a file first.');
      return;
    }

    setIsProcessing(true);
    setMessage(`Uploading ${selectedFile.name}...`);
    tailorMutation.reset(); // Reset mutation state

    let resumeId: number | null = null;

    // 1. Upload to get basic record and ID
    try {
      const token = await getAccessTokenSilently();
      const formData = new FormData();
      formData.append('file', selectedFile);

      const apiUrl = `${env.NEXT_PUBLIC_BACKEND_API_URL}/resumes/upload`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          // 'Content-Type': 'multipart/form-data' is set automatically by fetch with FormData
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed with status: ' + response.status }));
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setMessage('Upload complete. Parsing PDF...');
      resumeId = result.id; // Assuming the upload endpoint returns the created resume object with ID
      console.log('Upload successful, Resume ID:', resumeId);

      if (!resumeId) {
        throw new Error("Backend did not return a valid resume ID after upload.");
      }

      // 2. Parse PDF Client-side
      console.log('Starting client-side PDF parsing...');
      const parsedTextItems = await parsePdf(selectedFile);

      if (parseError || !parsedTextItems || parsedTextItems.length === 0) {
          throw new Error(`PDF Parsing failed: ${parseError || 'No text items extracted.'}`);
      }
      console.log(`Client-side parsing complete. Items: ${parsedTextItems.length}`);
      setMessage('Parsing complete. Tailoring resume...');

      // 3. Trigger Backend Tailoring/Structuring
      await tailorMutation.mutateAsync(
          {
              resume_id: resumeId,
              text_items: parsedTextItems,
              // No job description for initial upload/parse
              job_description: null,
              job_id: null,
          },
          {
              onSuccess: (data) => {
                  console.log('Tailoring successful:', data);
                  setMessage('Resume processed successfully!');
                  setSelectedFile(null); // Clear selection on full success
                   // Reset file input visually
                  const fileInput = document.getElementById('resume-upload') as HTMLInputElement;
                  if (fileInput) fileInput.value = '';
              },
              onError: (error) => {
                  console.error('Tailoring error:', error);
                  setMessage(`Tailoring failed: ${error.message}`);
              },
          }
      );

    } catch (error: any) { // Catch errors from upload, parsing, or tailoring mutation setup
      console.error('Processing error:', error);
      // Check if the error is from Auth0 (e.g., login required)
      if (error.error === 'login_required' || error.error === 'consent_required') {
         setMessage('Authentication required. Please log in and try again.');
         // Optionally trigger login: loginWithRedirect();
      } else {
         // Set the message based on the caught error
         setMessage(`Processing failed: ${error.message || 'An unknown error occurred.'}`);
      }
      // Ensure overall processing state is false if we landed in catch
      setIsProcessing(false);
    } finally {
        // This finally block executes after try or catch.
        // It ensures isProcessing is set to false *unless* the mutation is still pending
        // (because the mutation's onSuccess/onError will handle setting it false later).
        if (!tailorMutation.isPending) { // Use isPending
             setIsProcessing(false);
        }
    }
   // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFile, getAccessTokenSilently, parsePdf, parseError]); // Removed tailorMutation.mutateAsync from deps

  // isProcessing covers the upload/parse stages before the mutation starts
  // isPending covers the mutation stage itself
  const overallLoading = isProcessing || isParsing || tailorMutation.isPending;

  return (
    <div className="mt-8 p-6 border border-grey-20 rounded-md max-w-md mx-auto bg-white text-grey-90 shadow-1">
      <h3 className="text-lg font-semibold mb-4 text-grey-90">Import Profile from PDF</h3>
      <div className="grid w-full max-w-sm items-center gap-1.5 mb-4">
        <Label htmlFor="resume-upload" className="text-grey-90">Select PDF Resume</Label>
        <Input 
          id="resume-upload"
          type="file" 
          accept="application/pdf" 
          onChange={handleFileChange}
          disabled={overallLoading}
          className="file:text-primary-500 hover:file:bg-primary-500/10 file:border-0 file:rounded-md file:px-3 file:py-1.5 file:mr-3"
        />
      </div>
      <Button
        onClick={handleProcessResume} // Changed handler
        disabled={!selectedFile || overallLoading}
        className="w-full bg-primary-500 hover:bg-primary-600 text-white shadow-1 hover:-translate-y-px hover:shadow-md transition-all duration-150 ease-out disabled:opacity-50"
      >
        {overallLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
        {overallLoading ? 'Processing...' : 'Upload and Process Resume'}
      </Button>
      {message && <p className={`mt-3 text-sm ${(message.includes('failed') || message.includes('Please select') || message.includes('Error') || tailorMutation.isError || parseError) ? 'text-red-600' : 'text-green-600'}`}>{message}</p>}
      {/* Display specific errors */}
      {parseError && !message.includes('Parsing failed') && <p className="mt-1 text-sm text-red-600">Parse Error: {parseError}</p>}
      {tailorMutation.error && !message.includes('Tailoring failed') &&<p className="mt-1 text-sm text-red-600">Tailor Error: {tailorMutation.error.message}</p>}
    </div>
  );
}
