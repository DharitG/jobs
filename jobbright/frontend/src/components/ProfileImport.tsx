'use client';

import React, { useState } from 'react';
import type { ChangeEvent } from 'react'; // Use type-only import
import { Button } from './ui/button';
import { Input } from './ui/input'; // Assuming shadcn/ui input is here
import { Label } from './ui/label'; // Assuming shadcn/ui label is here

export function ProfileImport() {
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

    // --- TODO: Replace with actual API call --- 
    console.log('Uploading file:', selectedFile.name);
    // Example: const formData = new FormData();
    // formData.append('file', selectedFile);
    // try {
    //   const response = await fetch('/api/resumes/upload', { // Adjust API endpoint as needed
    //     method: 'POST',
    //     body: formData,
    //     // Add authentication headers if needed
    //   });
    //   if (!response.ok) throw new Error('Upload failed');
    //   const result = await response.json();
    //   setMessage('Upload successful!');
    //   console.log('Upload result:', result);
    // } catch (error: any) {
    //   setMessage(`Upload failed: ${error.message}`);
    //   console.error('Upload error:', error);
    // } finally {
    //   setIsUploading(false);
    // }
    // --- End of placeholder --- 

    // Simulate upload delay for now
    await new Promise(resolve => setTimeout(resolve, 1500));
    setMessage(`Simulated upload complete for ${selectedFile.name}. Check console.`);
    setIsUploading(false);
    setSelectedFile(null); // Clear selection after simulated upload
    // Reset file input visually if possible (tricky)
    const fileInput = document.getElementById('resume-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
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