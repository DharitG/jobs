'use client';

import React, { useState, useCallback } from 'react';
import type { ChangeEvent } from 'react';
// import { useAuth0 } from '@auth0/auth0-react'; // Removed Auth0
import { useSupabaseClient, useSession } from '@supabase/auth-helpers-react'; // Added Supabase
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { env } from '../env.js';
import { usePdfParser } from '~/hooks/usePdfParser';
import { api } from '~/trpc/react';
import { Loader2 } from 'lucide-react';

export function ProfileImport() {
  // const { getAccessTokenSilently } = useAuth0(); // Removed Auth0
  const session = useSession(); // Get Supabase session
  const supabase = useSupabaseClient(); // Get Supabase client
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  // const [isUploading, setIsUploading] = useState(false); // Replaced by isProcessing
  const [message, setMessage] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false); // Covers upload + parse steps before mutation

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
    // --- Check prerequisites ---
    if (!selectedFile) {
      setMessage('Please select a file first.');
      return;
    }
    // Ensure user is logged in (session exists) before proceeding
    if (!session) {
        setMessage('Authentication required. Please log in and try again.');
        return; // Exit early if no session
    }

    // --- Start processing ---
    setIsProcessing(true); // Start the overall processing state (upload + parse)
    setMessage(`Uploading ${selectedFile.name}...`);
    tailorMutation.reset(); // Reset previous mutation state

    let resumeId: number | null = null;

    try {
      // --- Step 1: Upload file to backend ---
      const token = session.access_token; // Safe to access token now due to check above
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

      // --- Step 2: Parse PDF Client-side ---
      console.log('Starting client-side PDF parsing...');
      // Note: isParsing state is handled by usePdfParser hook
      const parsedTextItems = await parsePdf(selectedFile);

      if (parseError || !parsedTextItems || parsedTextItems.length === 0) {
          throw new Error(`PDF Parsing failed: ${parseError || 'No text items extracted.'}`);
      }
      console.log(`Client-side parsing complete. Items: ${parsedTextItems.length}`);
      setMessage('Parsing complete. Tailoring resume...');
      setIsProcessing(false); // End the initial processing state before mutation starts

      // --- Step 3: Trigger Backend Tailoring/Structuring ---
      // Note: tailorMutation.isPending will track the loading state here
      await tailorMutation.mutateAsync(
          {
              resume_id: resumeId,
              text_items: parsedTextItems,
              job_description: null, // No job description for initial upload
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
              // No need for onSettled to set isProcessing false, it's handled by mutation state
          }
      );

    } catch (error: any) { // Catch errors from upload, parsing, or mutation setup
      console.error('Processing error:', error);
      // Removed Auth0-specific error check
      setMessage(`Processing failed: ${error.message || 'An unknown error occurred.'}`);
      setIsProcessing(false); // Ensure loading state is reset if error occurred *before* mutation started
    }
    // No finally block needed as mutation state handles the end of processing loading
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFile, session, parsePdf, parseError]); // Dependencies

  // Combined loading state: isProcessing (upload/parse) OR isParsing (hook) OR isPending (mutation)
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
        onClick={handleProcessResume}
        disabled={!selectedFile || overallLoading}
        className="w-full bg-primary-500 hover:bg-primary-600 text-white shadow-1 hover:-translate-y-px hover:shadow-md transition-all duration-150 ease-out disabled:opacity-50"
      >
        {overallLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
        {overallLoading ? 'Processing...' : 'Upload and Process Resume'}
      </Button>
      {message && <p className={`mt-3 text-sm ${(message.includes('failed') || message.includes('Please select') || message.includes('Error') || tailorMutation.isError || parseError) ? 'text-red-600' : 'text-green-600'}`}>{message}</p>}
      {/* Display specific errors */}
      {parseError && !message.includes('Parsing failed') && <p className="mt-1 text-sm text-red-600">Parse Error: {parseError}</p>}
      {tailorMutation.error && !message.includes('Tailoring failed') && <p className="mt-1 text-sm text-red-600">Tailor Error: {tailorMutation.error.message}</p>}
    </div>
  );
}
