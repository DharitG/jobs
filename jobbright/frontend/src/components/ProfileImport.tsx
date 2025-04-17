'use client';

'use client';

import React, { useState } from 'react';
import type { ChangeEvent } from 'react'; // Use type-only import
import { useAuth0 } from '@auth0/auth0-react'; // Import useAuth0
import { Button } from './ui/button';
import { Input } from './ui/input'; // Assuming shadcn/ui input is here
import { Label } from './ui/label'; // Assuming shadcn/ui label is here
import { env } from '../env.js'; // Import env using relative path

export function ProfileImport() {
  const { getAccessTokenSilently } = useAuth0(); // Get token function
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<string>('');

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

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setMessage(`Uploading ${selectedFile.name}...`);

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
      setMessage('Upload successful!');
      console.log('Upload result:', result);
      setSelectedFile(null); // Clear selection on success
      // Reset file input visually
      const fileInput = document.getElementById('resume-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

    } catch (error: any) {
      console.error('Upload error:', error);
      // Check if the error is from Auth0 (e.g., login required)
      if (error.error === 'login_required' || error.error === 'consent_required') {
         setMessage('Authentication required. Please log in and try again.');
         // Optionally trigger login: loginWithRedirect();
      } else {
         setMessage(`Upload failed: ${error.message || 'An unknown error occurred.'}`);
      }
    } finally {
      setIsUploading(false);
    }
  };

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
          disabled={isUploading}
          className="file:text-primary-500 hover:file:bg-primary-500/10 file:border-0 file:rounded-md file:px-3 file:py-1.5 file:mr-3"
        />
      </div>
      <Button 
        onClick={handleUpload} 
        disabled={!selectedFile || isUploading}
        className="w-full bg-primary-500 hover:bg-primary-600 text-white shadow-1 hover:-translate-y-px hover:shadow-md transition-all duration-150 ease-out disabled:opacity-50"
      >
        {isUploading ? 'Uploading...' : 'Upload Resume'}
      </Button>
      {message && <p className={`mt-3 text-sm ${message.includes('failed') || message.includes('Please select') ? 'text-error' : 'text-accent'}`}>{message}</p>}
    </div>
  );
}
